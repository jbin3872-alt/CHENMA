$ErrorActionPreference = "Stop"
$products = Get-Content -Path "products_full.json" -Raw -Encoding UTF8 | ConvertFrom-Json
New-Item -ItemType Directory -Path "products" -Force | Out-Null

$catMeta = @{
    "SC" = @{ pillar = "stair-climbers.html"; label = "Stair Climbers" }
    "FE" = @{ pillar = "electric-forklifts.html"; label = "Electric Forklifts" }
    "SE" = @{ pillar = "semi-electric-forklifts.html"; label = "Semi-Electric Forklifts" }
    "LM" = @{ pillar = "lift-machines.html"; label = "Lift Machines" }
}
$catBlog = @{
    "SC" = '<a href="../stair-climber-guide.html" class="text-blue-400 underline">Stair Climber Safety Guide</a>'
    "FE" = '<a href="../electric-forklift-guide.html" class="text-blue-400 underline">Forklift Maintenance Guide</a>'
    "SE" = '<a href="../electric-stacker-guide.html" class="text-blue-400 underline">Stacker Selection Guide</a>'
    "LM" = '<a href="../lift-machine-guide.html" class="text-blue-400 underline">Aerial Work Platform Guide</a>'
}

function Get-Slug([string]$name) {
    $slug = $name -replace '\([^)]*\)', '' -replace '&', 'and'
    $slug = $slug -replace '[^a-zA-Z0-9 -]', '' -replace ' +', ' '
    $slug = $slug.Trim() -replace ' ', '-'
    return $slug.ToLower()
}

$nav = @'
<div class="hidden md:flex space-x-6 text-xs font-bold uppercase tracking-widest">
    <a href="../index.html" class="hover:text-blue-400">Home</a>
    <a href="../stair-climbers.html" class="hover:text-blue-400">Stair Climbers</a>
    <a href="../electric-forklifts.html" class="hover:text-blue-400">Electric Forklifts</a>
    <a href="../semi-electric-forklifts.html" class="hover:text-blue-400">Semi-Electric</a>
    <a href="../lift-machines.html" class="hover:text-blue-400">Lift Machines</a>
</div>
'@

$footer = @'
<footer class="bg-slate-900 text-white py-12 mt-16">
  <div class="container mx-auto px-6 grid md:grid-cols-3 gap-10">
    <div>
      <img src="https://sc02.alicdn.com/kf/H094d445ef7544ed0b8eea6b6d0d98b9bQ.jpg" class="h-10 bg-white p-1 rounded mb-4">
      <p class="text-slate-400">Xi'an Chen Ma Materials Co.,Ltd. Professional material handling solutions since 2011.</p>
    </div>
    <div>
      <h4 class="font-black uppercase tracking-widest mb-4">Product Categories</h4>
      <p class="text-slate-400 mb-2"><i class="fas fa-chevron-right text-blue-400 mr-2"></i><a href="../stair-climbers.html" class="underline">Stair Climbers</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-chevron-right text-blue-400 mr-2"></i><a href="../electric-forklifts.html" class="underline">Electric Forklifts</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-chevron-right text-blue-400 mr-2"></i><a href="../semi-electric-forklifts.html" class="underline">Semi-Electric Forklifts</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-chevron-right text-blue-400 mr-2"></i><a href="../lift-machines.html" class="underline">Lift Machines</a></p>
    </div>
    <div>
      <h4 class="font-black uppercase tracking-widest mb-4">Guides & Contact</h4>
      <p class="text-slate-400 mb-2"><i class="fas fa-book text-blue-400 mr-2"></i><a href="../stair-climber-guide.html" class="underline">Blog: Stair Climber Guide</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-book text-blue-400 mr-2"></i><a href="../electric-stacker-guide.html" class="underline">Blog: Stacker Selection Guide</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-book text-blue-400 mr-2"></i><a href="../lift-machine-guide.html" class="underline">Blog: Aerial Work Platform Guide</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-book text-blue-400 mr-2"></i><a href="../ce-certification-guide.html" class="underline">Blog: CE Certification Guide</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-envelope text-blue-400 mr-2"></i>chenmagongsi@163.com</p>
    </div>
  </div>
</footer>
'@

$count = 0
foreach ($p in $products) {
    $slug = Get-Slug $p.name
    $meta = $catMeta[$p.cat]
    $file = "products/$slug.html"

    $related = @($products | Where-Object { $_.cat -eq $p.cat -and $_.id -ne $p.id } | Select-Object -First 3)
    $relatedHtml = ""
    foreach ($r in $related) {
        $rSlug = Get-Slug $r.name
        $rShort = ($r.name -replace ' \([^)]*\)', '').Trim()
        $relatedHtml += '<a href="' + $rSlug + '.html" class="block p-4 bg-slate-50 rounded-xl border border-slate-100 hover:shadow-md transition"><span class="block text-[10px] font-black uppercase text-blue-600 mb-1">' + $rShort + '</span><img src="' + $r.img + '" class="h-16 object-contain mx-auto" alt="' + $r.name + '"></a>'
    }

    $specRows = ""
    foreach ($s in $p.specs) {
        $specRows += '<tr class="border-b border-slate-100"><td class="p-3 text-[10px] text-slate-400 font-bold uppercase tracking-wider">' + $s.k + '</td><td class="p-3 font-black text-slate-800 text-sm">' + $s.v + '</td></tr>'
    }

    $desc = "$($p.name) - CE certified material handling equipment from Chenma Lifting."
    $waText = [uri]::EscapeDataString("Hello, I am interested in: $($p.name). Please send specifications and best price.")
    $waLink = "https://wa.me/8615991627891?text=" + $waText
    $mailSubject = [uri]::EscapeDataString("Inquiry: $($p.name)")

    $page = '<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>' + $p.name + ' | Chenma Lifting</title>
<meta name="description" content="' + $desc + '">
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<!-- GEO Optimization: JSON-LD -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "' + $p.name + '",
  "image": "' + $p.img + '",
  "description": "' + $desc + '",
  "brand": {"@type": "Brand", "name": "chenma"},
  "offers": {
    "@type": "Offer",
    "url": "https://www.chenmalifting.com/products/' + $slug + '.html",
    "priceCurrency": "USD",
    "price": "1200.00",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  }
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type":"ListItem","position":1,"name":"Home","item":"https://www.chenmalifting.com/"},
    {"@type":"ListItem","position":2,"name":"' + $meta.label + '","item":"https://www.chenmalifting.com/' + $meta.pillar + '"},
    {"@type":"ListItem","position":3,"name":"' + $p.name + '","item":"https://www.chenmalifting.com/products/' + $slug + '.html"}
  ]
}
</script>
</head>
<body class="bg-slate-100 font-sans">
<nav class="bg-slate-900 text-white sticky top-0 z-50 shadow-xl">
  <div class="container mx-auto px-6 py-4 flex justify-between items-center">
    <div class="flex items-center space-x-3 cursor-pointer" onclick="location.href=''../index.html''">
      <img src="https://sc02.alicdn.com/kf/H094d445ef7544ed0b8eea6b6d0d98b9bQ.jpg" class="h-10 bg-white p-1 rounded" alt="Logo">
      <span class="text-xl font-black uppercase">CHENMA <span class="text-blue-400">LIFTING</span></span>
    </div>
    ' + $nav + '
    <a href="mailto:chenmagongsi@163.com" class="bg-blue-600 px-4 py-2 rounded text-xs font-black uppercase hover:bg-blue-700">Get Quote</a>
  </div>
</nav>

<header class="bg-slate-900 text-white py-12">
  <div class="container mx-auto px-6">
    <nav class="text-xs text-slate-400 mb-4">
      <a href="../index.html" class="hover:text-blue-400">Home</a>
      <span class="mx-2">/</span>
      <a href="../' + $meta.pillar + '" class="hover:text-blue-400">' + $meta.label + '</a>
      <span class="mx-2">/</span>
      <span class="text-blue-400 font-bold">' + $p.name + '</span>
    </nav>
    <h1 class="text-2xl md:text-4xl font-black uppercase tracking-tighter">' + $p.name + '</h1>
    <span class="inline-block mt-3 px-3 py-1 bg-blue-600 rounded-full text-[10px] font-black uppercase tracking-widest">' + $meta.label + ' · CE Certified</span>
  </div>
</header>

<section class="container mx-auto px-6 py-12">
  <div class="grid md:grid-cols-2 gap-10">
    <div>
      <img src="' + $p.img + '" class="w-full h-96 object-contain bg-white rounded-3xl p-8 shadow-sm border border-slate-100" alt="' + $p.name + '">
    </div>
    <div>
      <h2 class="text-xl font-black uppercase tracking-tight mb-6">Technical Specifications</h2>
      <table class="w-full bg-white rounded-2xl shadow-sm border border-slate-100">
        <tbody>
          ' + $specRows + '
        </tbody>
      </table>
      <div class="grid grid-cols-2 gap-4 mt-8">
        <a href="' + $waLink + '" target="_blank" class="bg-green-500 text-white py-4 rounded-xl font-black flex items-center justify-center hover:bg-green-600 transition">
          <i class="fab fa-whatsapp mr-2 text-xl"></i>WhatsApp
        </a>
        <a href="mailto:chenmagongsi@163.com?subject=' + $mailSubject + '" class="bg-blue-600 text-white py-4 rounded-xl font-black flex items-center justify-center hover:bg-blue-700 transition">
          <i class="fas fa-envelope mr-2"></i>Get Quote
        </a>
      </div>
    </div>
  </div>
</section>

<section class="container mx-auto px-6 pb-12">
  <h2 class="text-xl font-black uppercase tracking-tight mb-6">Related Products</h2>
  <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
    ' + $relatedHtml + '
  </div>
</section>

<section class="container mx-auto px-6 pb-16">
  <div class="bg-white rounded-2xl p-8 shadow-sm border border-slate-100">
    <h2 class="text-lg font-black uppercase tracking-tight mb-3">Related Guide</h2>
    <p class="text-sm text-slate-600">Learn more about using and maintaining this equipment: ' + $catBlog[$p.cat] + '</p>
  </div>
</section>

' + $footer + '
</body>
</html>'

    [System.IO.File]::WriteAllText((Resolve-Path $file), $page, (New-Object System.Text.UTF8Encoding($false)) )
    $count++
}
Write-Host "Generated $count product pages in products/"
