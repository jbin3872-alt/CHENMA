$ErrorActionPreference = "Stop"
$products = Get-Content -Path "products_full.json" -Raw -Encoding UTF8 | ConvertFrom-Json

function Get-Slug([string]$name) {
    $slug = $name -replace '\([^)]*\)', '' -replace '&', 'and'
    $slug = $slug -replace '[^a-zA-Z0-9 -]', '' -replace ' +', ' '
    return ($slug.Trim() -replace ' ', '-').ToLower()
}

function Get-SpecValue($specs, [string[]]$keys) {
    foreach ($s in $specs) {
        foreach ($k in $keys) {
            if ($s.k -eq $k -and $s.v -ne '') { return $s.v }
        }
    }
    return $null
}

function New-ESC([string]$t) {
    return $t.Replace('\', '\\').Replace('"', '\"').Replace("`n", '\n').Replace("`r", '')
}

$count = 0
foreach ($p in $products) {
    $slug = Get-Slug $p.name
    $file = "products/$slug.html"
    if (-not (Test-Path $file)) { Write-Host "SKIP (missing): $file"; continue }

    # --- Build FAQ items from REAL specs ---
    $faqs = New-Object System.Collections.ArrayList

    # 1. Load capacity (key varies by category)
    $loadKeys = @("Max Load", "Load Capacity", "Load Capacity ", "Safe Working Load", "Rated Load")
    $load = Get-SpecValue $p.specs $loadKeys
    if ($load) {
        [void]$faqs.Add(@{ q = "What is the load capacity of the $($p.name)?"
            a = "The $($p.name) has a load capacity of $load." })
    }

    # 2. Lift height / working height
    $heightKeys = @("Lift Height", "Max Lift Height", "Max Working Height", "Lifting Height", "Lift Range", "Max Height", "Max Operate Height")
    $height = Get-SpecValue $p.specs $heightKeys
    if ($height) {
        [void]$faqs.Add(@{ q = "What is the lifting height of the $($p.name)?"
            a = "The $($p.name) provides a lift height of $height." })
    }

    # 3. Battery
    $batteryKeys = @("Battery", "Charging Voltage", "Voltage", "Power Supply")
    $battery = Get-SpecValue $p.specs $batteryKeys
    if ($battery -and $battery -notmatch '220V|380V') {
        [void]$faqs.Add(@{ q = "What battery does the $($p.name) use?"
            a = "The $($p.name) is powered by $battery." })
    }

    # 4. Motor / power
    $powerKeys = @("Power", "Motor Power", "Drive Motor", "Hoist Motor", "Motor", "Rated Power")
    $power = Get-SpecValue $p.specs $powerKeys
    if ($power) {
        [void]$faqs.Add(@{ q = "What is the power specification of the $($p.name)?"
            a = "The $($p.name) features $power." })
    }

    # 5. CE certification (fixed, true for all)
    [void]$faqs.Add(@{ q = "Is the $($p.name) CE certified?"
        a = "Yes, all products from Xi'an Chenma Materials Co., Ltd., including the $($p.name), are CE-certified and exported to 50+ countries." })

    # 6. OEM/ODM (fixed, true)
    [void]$faqs.Add(@{ q = "Does Chenma support OEM or ODM customization for the $($p.name)?"
        a = "Yes, Xi'an Chenma Materials Co., Ltd. supports both OEM and ODM cooperation models with end-to-end support from custom development to global shipment." })

    # --- Build FAQPage JSON-LD ---
    $jsonFaqs = ""
    foreach ($f in $faqs) {
        $qEsc = New-ESC $f.q
        $aEsc = New-ESC $f.a
        $jsonFaqs += '{"@type":"Question","name":"' + $qEsc + '","acceptedAnswer":{"@type":"Answer","text":"' + $aEsc + '"}},'
    }
    $jsonFaqs = $jsonFaqs.TrimEnd(',')

    $faqLd = @'
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
' + $jsonFaqs + @'
  ]
}
</script>
'@

    # --- Build visible FAQ HTML ---
    $faqHtml = '<section class="container mx-auto px-6 pb-16">
  <h2 class="text-xl font-black uppercase tracking-tight mb-6">Frequently Asked Questions</h2>
  <div class="space-y-4">'
    foreach ($f in $faqs) {
        $faqHtml += '<div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
      <h3 class="font-black text-slate-800 mb-2">' + $f.q + '</h3>
      <p class="text-sm text-slate-600 leading-relaxed">' + $f.a + '</p>
    </div>'
    }
    $faqHtml += '</div>
</section>'

    # --- Inject into the page ---
    $page = Get-Content -Path $file -Raw -Encoding UTF8

    # 1. Insert FAQPage JSON-LD before </head>
    $headMarker = '</head>'
    if (-not $page.Contains('FAQPage')) {
        $idx = $page.IndexOf($headMarker)
        if ($idx -gt 0) {
            $page = $page.Substring(0, $idx) + $faqLd + "`n" + $page.Substring($idx)
        }
    }

    # 2. Insert visible FAQ section before <footer
    $footerMarker = '<footer'
    $fIdx = $page.IndexOf($footerMarker)
    if ($fIdx -gt 0) {
        $page = $page.Substring(0, $fIdx) + $faqHtml + "`n" + $page.Substring($fIdx)
    }

    [System.IO.File]::WriteAllText((Resolve-Path $file), $page, (New-Object System.Text.UTF8Encoding($false)) )
    $count++
    Write-Host "OK: $file ($($faqs.Count) FAQs)"
}
Write-Host "=== Done: $count product pages updated ==="
