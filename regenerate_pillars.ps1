$ErrorActionPreference = "Stop"
$products = Get-Content -Path "products_full.json" -Raw -Encoding UTF8 | ConvertFrom-Json

function Get-Slug([string]$name) {
    $slug = $name -replace '\([^)]*\)', '' -replace '&', 'and'
    $slug = $slug -replace '[^a-zA-Z0-9 -]', '' -replace ' +', ' '
    return ($slug.Trim() -replace ' ', '-').ToLower()
}
$slugMap = @{}
foreach ($p in $products) { $slugMap[$p.id] = Get-Slug $p.name }

$navCommon = @'
<div class="hidden md:flex space-x-6 text-xs font-bold uppercase tracking-widest">
    <a href="index.html" class="hover:text-blue-400">Home</a>
    <a href="stair-climbers.html" class="hover:text-blue-400">Stair Climbers</a>
    <a href="electric-forklifts.html" class="hover:text-blue-400">Electric Forklifts</a>
    <a href="semi-electric-forklifts.html" class="hover:text-blue-400">Semi-Electric</a>
    <a href="lift-machines.html" class="hover:text-blue-400">Lift Machines</a>
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
      <p class="text-slate-400 mb-2"><i class="fas fa-chevron-right text-blue-400 mr-2"></i><a href="stair-climbers.html" class="underline">Stair Climbers</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-chevron-right text-blue-400 mr-2"></i><a href="electric-forklifts.html" class="underline">Electric Forklifts</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-chevron-right text-blue-400 mr-2"></i><a href="semi-electric-forklifts.html" class="underline">Semi-Electric Forklifts</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-chevron-right text-blue-400 mr-2"></i><a href="lift-machines.html" class="underline">Lift Machines</a></p>
    </div>
    <div>
      <h4 class="font-black uppercase tracking-widest mb-4">Guides & Contact</h4>
      <p class="text-slate-400 mb-2"><i class="fas fa-book text-blue-400 mr-2"></i><a href="stair-climber-guide.html" class="underline">Blog: Stair Climber Guide</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-book text-blue-400 mr-2"></i><a href="electric-stacker-guide.html" class="underline">Blog: Stacker Selection Guide</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-book text-blue-400 mr-2"></i><a href="lift-machine-guide.html" class="underline">Blog: Aerial Work Platform Guide</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-book text-blue-400 mr-2"></i><a href="ce-certification-guide.html" class="underline">Blog: CE Certification Guide</a></p>
      <p class="text-slate-400 mb-2"><i class="fas fa-envelope text-blue-400 mr-2"></i>chenmagongsi@163.com</p>
    </div>
  </div>
</footer>
'@

$cats = @(
    @{ key="SC"; file="stair-climbers.html"; title="Electric Stair Climbers"; h1="Electric Stair Climbers"; desc="Chenma electric stair climbers are professional material handling solutions designed to transport heavy loads up and down stairs with minimal physical effort. Our stair climbing trolleys use 48V lithium battery systems and powerful motors (600W-1500W) to lift 150kg to 400kg loads safely. Models like the LP800 series and DP800 series feature manganese steel frames, anti-skid tracks, and silent wheels, making them ideal for logistics, construction sites, appliance delivery, and warehouse operations. All stair climbers are CE-certified and export-proven in 50+ countries. Whether you need a compact 150kg model for household use or a heavy-duty 400kg all-terrain climber, Chenma offers OEM and ODM customization to match your exact requirements."; faq=@(@{q="What is the maximum load capacity of Chenma stair climbers?"; a="The LP800 series stair climbers support up to 400 kg, while the LP-600 crawler model handles 300 kg and the LP800-101/102 models handle 250kg and 150kg respectively."},@{q="What battery do Chenma stair climbers use?"; a="All Chenma stair climbers use 48V lithium batteries with 20AH to 72AH capacity, providing 3-6 hours of continuous work time and a 3-5 year battery life."},@{q="Are Chenma stair climbers CE certified?"; a="Yes, all Chenma material handling equipment including stair climbers are CE-certified and exported to over 50 countries."},@{q="Can stair climbers handle all types of stairs?"; a="Most Chenma models fit standard cement and tile stairs up to 20cm step height. The DP800 series with rubber or inflatable wheels is suitable for all terrains, while crawler-type models can climb 60-degree inclines."}) },
    @{ key="FE"; file="electric-forklifts.html"; title="Full Electric Forklifts"; h1="Full Electric Forklifts"; desc="Chenma full electric forklifts deliver zero-emission material handling power for warehouses, factories, and logistics centers. Our lineup ranges from the compact CMAE-F02 seated forklift (800kg) to the heavy-duty CMAE-F07 (2000kg) with a 3m lift height. Every model features lead-acid battery packs (48V), solid rubber tires for indoor/outdoor stability, and durable C-channel steel masts. The CMAE-R10 brushless motor forklift offers reduced maintenance, while the CMAE-S13 lithium battery stacker provides 6-7 hours of runtime. All forklifts are CE-certified and engineered for narrow-aisle navigation with precise hydraulic control."; faq=@(@{q="What is the load capacity range of Chenma electric forklifts?"; a="Chenma electric forklifts range from 500kg compact models like the CMAE-F02-2 to 2000kg heavy-duty models like the CMAE-F07 with 3m lift height."},@{q="What batteries do Chenma electric forklifts use?"; a="Most models use 48V lead-acid batteries (32AH to 75AH). The CMAE-S13 stacker uses a 48V 15AH lithium battery providing 6-7 hours of work time."},@{q="Are these forklifts suitable for indoor use?"; a="Yes, all models feature solid rubber tires and electric drive, making them zero-emission and suitable for indoor warehouse operations."},@{q="What is the maximum travel speed?"; a="The heavy-duty CMAE-F07 reaches 12 km/h empty, while the precision CMAE-F06 travels at 8 km/h empty."}) },
    @{ key="SE"; file="semi-electric-forklifts.html"; title="Semi-Electric Forklifts"; h1="Semi-Electric Forklifts"; desc="Chenma semi-electric forklifts combine electric lifting with manual pushing, offering the perfect balance of cost-efficiency and labor savings. The CMSE series features electric lifting powered by lead-acid or lithium batteries (12V-48V), eliminating manual pumping while keeping acquisition costs low. Models like the CMSE-S01 (1 ton / 1.6m) and CMSE-S03 remote control stacker (500kg) are compact enough for elevators and narrow aisles, making them ideal for small warehouses, retail stores, and cross-floor transport. With adjustable forks for single and double pallets, CE certification, and OEM customization, Chenma semi-electric stackers are the entry-level solution trusted by businesses in 50+ countries."; faq=@(@{q="What is the capacity of Chenma semi-electric stackers?"; a="Semi-electric stackers range from 400kg (CMSE-S12) to 2000kg (CMSE-S08 universal model), with lifting heights from 1.3m to 3.5m."},@{q="How do semi-electric stackers work?"; a="Lifting is powered by an electric motor (800W-2200W), while movement is manual push/pull. Some models like the CMSE-S03 feature wired and wireless remote control."},@{q="Are semi-electric stackers suitable for small warehouses?"; a="Yes, their compact dimensions fit standard elevators and narrow aisles, and electric lifting prevents operator fatigue from manual pumping."},@{q="Do semi-electric stackers require charging?"; a="Yes, they use rechargeable batteries (12V or 48V) providing approximately 200 lifts per charge."}) },
    @{ key="LM"; file="lift-machines.html"; title="Lift Machines & Platforms"; h1="Lift Machines & Aerial Work Platforms"; desc="Chenma lift machines cover the full spectrum of vertical material handling: from electric hoists and table lifts to scissor lifts and high-altitude aerial work platforms. The CMLM-E09 self-propelled scissor lift carries 450kg up to 10m, while the CMLM-E03 galvanized lift reaches 4-20m for high-altitude maintenance. For warehouse ergonomics, our hydraulic and electric table lifts handle 150kg to 1000kg loads. The aluminum pillar lift series provides safe working platforms from 4m to 18m. Every machine is built with steel or aluminum alloy construction, features wireless remote controls, and is CE-certified. Chenma supports OEM/ODM projects with end-to-end support from development to global shipment."; faq=@(@{q="What is the highest working height available?"; a="The CMLM-E03 galvanized high-altitude lift covers 4-20m, while the aluminum pillar lift series reaches up to 18m with 125-300kg capacity."},@{q="Which lift machine carries the heaviest load?"; a="The CMLM-E01 channel steel lift carries 1000kg, and the CMLM-E09 scissor lift carries 450kg to a 10m working height."},@{q="Are electric table lifts available?"; a="Yes, the CMLM-E12 electric table lift handles 200-1000kg with lift ranges from 30.5cm to 126cm, featuring 12V lead-acid batteries."},@{q="Are all lift machines CE certified?"; a="Yes, all Chenma lift machines and platforms are CE-certified material handling equipment."}) }
)

foreach ($cat in $cats) {
    $catProducts = @($products | Where-Object { $_.cat -eq $cat.key })
    $cards = ""
    foreach ($p in $catProducts) {
        $slug = $slugMap[$p.id]
        $cards += '<a href="products/' + $slug + '.html" class="block">
<div class="card bg-white rounded-2xl shadow hover:shadow-2xl transition cursor-pointer overflow-hidden border border-slate-100 flex flex-col">
  <div class="h-44 p-3 flex items-center justify-center bg-white relative overflow-hidden">
    <img src="' + $p.img + '" class="max-h-full object-contain" alt="' + $p.name + '" onerror="this.src=''https://via.placeholder.com/300x200?text=CHENMA''">
  </div>
  <div class="p-4 flex flex-col flex-grow bg-slate-50">
    <h4 class="font-bold text-[11px] uppercase text-slate-800 line-clamp-2 mb-2 leading-tight h-9">' + $p.name + '</h4>
    <div class="mt-auto pt-2 border-t border-slate-200 flex justify-between text-[10px] font-black uppercase">
      <span class="text-blue-600">' + $p.cat + '</span>
      <span class="text-slate-400">ID: ' + $p.id + '</span>
    </div>
  </div>
</div>
</a>'
    }

    $faqItems = ""
    foreach ($f in $cat.faq) {
        $faqItems += '{"@type":"Question","name":"' + $f.q + '","acceptedAnswer":{"@type":"Answer","text":"' + $f.a + '"}},'
    }
    $faqItems = $faqItems.TrimEnd(',')

    $faqHtml = ""
    foreach ($f in $cat.faq) {
        $faqHtml += '<div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
      <h3 class="font-black text-slate-800 mb-2">' + $f.q + '</h3>
      <p class="text-sm text-slate-600 leading-relaxed">' + $f.a + '</p>
    </div>'
    }

    $descTrim = $cat.desc
    if ($descTrim.Length -gt 155) { $descTrim = $descTrim.Substring(0, 155) }

    $page = '<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>' + $cat.title + ' | Chenma Lifting</title>
<meta name="description" content="' + $descTrim + '">
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<!-- GEO Optimization: JSON-LD -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type":"ListItem","position":1,"name":"Home","item":"https://www.chenmalifting.com/"},
    {"@type":"ListItem","position":2,"name":"' + $cat.h1 + '","item":"https://www.chenmalifting.com/' + $cat.file + '"}
  ]
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "' + $cat.h1 + ' | Chenma Lifting",
  "url": "https://www.chenmalifting.com/' + $cat.file + '",
  "isPartOf": {"@type":"WebSite","name":"Chenma Lifting","url":"https://www.chenmalifting.com/"}
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [' + $faqItems + ']
}
</script>
</head>
<body class="bg-slate-100 font-sans">
<nav class="bg-slate-900 text-white sticky top-0 z-50 shadow-xl">
  <div class="container mx-auto px-6 py-4 flex justify-between items-center">
    <div class="flex items-center space-x-3 cursor-pointer" onclick="location.href=''index.html''">
      <img src="https://sc02.alicdn.com/kf/H094d445ef7544ed0b8eea6b6d0d98b9bQ.jpg" class="h-10 bg-white p-1 rounded" alt="Logo">
      <span class="text-xl font-black uppercase">CHENMA <span class="text-blue-400">LIFTING</span></span>
    </div>
    ' + $navCommon + '
    <a href="mailto:chenmagongsi@163.com" class="bg-blue-600 px-4 py-2 rounded text-xs font-black uppercase hover:bg-blue-700">Get Quote</a>
  </div>
</nav>

<header class="bg-slate-900 text-white py-16">
  <div class="container mx-auto px-6">
    <nav class="text-xs text-slate-400 mb-4">
      <a href="index.html" class="hover:text-blue-400">Home</a>
      <span class="mx-2">/</span>
      <span class="text-blue-400 font-bold">' + $cat.h1 + '</span>
    </nav>
    <h1 class="text-3xl md:text-5xl font-black uppercase tracking-tighter">' + $cat.h1 + '</h1>
    <p class="text-slate-400 mt-4 max-w-3xl leading-relaxed">' + $cat.desc + '</p>
  </div>
</header>

<section class="container mx-auto px-6 py-12">
  <h2 class="text-2xl font-black uppercase tracking-tight mb-8">Product Catalog <span class="text-blue-600">(' + $catProducts.Count + ' Models)</span></h2>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    ' + $cards + '
  </div>
</section>

<section class="container mx-auto px-6 py-12 max-w-4xl">
  <h2 class="text-2xl font-black uppercase tracking-tight mb-8">Frequently Asked Questions</h2>
  <div class="space-y-4">
    ' + $faqHtml + '
  </div>
</section>

' + $footer + '
</body>
</html>'

    [System.IO.File]::WriteAllText((Resolve-Path $cat.file), $page, (New-Object System.Text.UTF8Encoding($false)) )
    Write-Host "Regenerated $($cat.file)"
}
