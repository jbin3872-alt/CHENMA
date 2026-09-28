$ErrorActionPreference = "Stop"

function New-ESC([string]$t) {
    $out = $t.Replace('\', '\\').Replace('"', '\"')
    $out = $out.Replace("`r", '').Replace("`n", '\n').Replace("`t", '\t')
    return $out
}

$count = 0
Get-ChildItem products/*.html | ForEach-Object {
    $file = $_.FullName
    $page = Get-Content -Path $file -Raw -Encoding UTF8

    # Skip if no visible FAQ section
    if (-not $page.Contains('Frequently Asked Questions')) { Write-Host "SKIP (no FAQ): $($_.Name)"; return }

    # 1. Extract Q&A pairs from the visible FAQ section
    $faqStart = $page.IndexOf('Frequently Asked Questions')
    $faqEnd = $page.IndexOf('</section>', $faqStart)
    if ($faqEnd -lt 0) { $faqEnd = $page.Length }
    $faqSection = $page.Substring($faqStart, $faqEnd - $faqStart)

    $qRegex = [regex]'<h3 class="font-black text-slate-800 mb-2">(.*?)</h3>'
    $aRegex = [regex]'<p class="text-sm text-slate-600 leading-relaxed">(.*?)</p>'
    $qs = @($qRegex.Matches($faqSection) | ForEach-Object { $_.Groups[1].Value })
    $as = @($aRegex.Matches($faqSection) | ForEach-Object { $_.Groups[1].Value })

    if ($qs.Count -eq 0 -or $qs.Count -ne $as.Count) {
        Write-Host "WARN: Q/A mismatch in $($_.Name) (Q=$($qs.Count), A=$($as.Count))"
        return
    }

    # 2. Build the FAQPage JSON-LD
    $items = ""
    for ($i = 0; $i -lt $qs.Count; $i++) {
        $qEsc = New-ESC $qs[$i]
        $aEsc = New-ESC $as[$i]
        $items += '    {"@type":"Question","name":"' + $qEsc + '","acceptedAnswer":{"@type":"Answer","text":"' + $aEsc + '"}}'
        if ($i -lt $qs.Count - 1) { $items += "," }
        $items += "`n"
    }

    $faqLd = '<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
' + $items + '  ]
}
</script>'

    # 3. Replace the old (broken) FAQPage JSON-LD block
    $ldStart = $page.IndexOf('"@type": "FAQPage"')
    if ($ldStart -gt 0) {
        $scriptStart = $page.LastIndexOf('<script type="application/ld+json">', $ldStart)
        $scriptEnd = $page.IndexOf('</script>', $ldStart)
        if ($scriptStart -ge 0 -and $scriptEnd -gt $scriptStart) {
            $scriptEndFull = $scriptEnd + '</script>'.Length
            $page = $page.Substring(0, $scriptStart) + $faqLd + $page.Substring($scriptEndFull)
        }
    } else {
        # No FAQPage LD present - insert before </head>
        $headIdx = $page.IndexOf('</head>')
        if ($headIdx -gt 0) {
            $page = $page.Substring(0, $headIdx) + $faqLd + "`n" + $page.Substring($headIdx)
        }
    }

    [System.IO.File]::WriteAllText((Resolve-Path $file), $page, (New-Object System.Text.UTF8Encoding($false)) )
    $count++
    Write-Host "REPAIRED: $($_.Name) ($($qs.Count) FAQs)"
}
Write-Host "=== Done: $count pages repaired ==="
