#!/usr/bin/env python3
"""
STEP 2: Generate the complete Central Asia interactive timeline map HTML.
Reads geodata.json and embeds it. ALL writing via Python file I/O.
"""
import json, os

GEODATA_PATH = "/home/user/geodata.json"
OUTPUT_PATH = "/home/user/central-asia-map.html"

with open(GEODATA_PATH) as f:
    geodata_raw = f.read()

# Build HTML as a Python string
html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Central Asia — Historical Timeline Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --glass-bg:rgba(13,17,23,0.88);
  --glass-border:rgba(255,255,255,0.08);
  --glass-blur:16px;
  --accent:#81B29A;
  --text-primary:#E6EDF3;
  --text-secondary:#8B949E;
  --text-muted:#484F58;
  --font-serif:'Crimson Pro',Georgia,serif;
  --font-sans:'DM Sans',-apple-system,BlinkMacSystemFont,sans-serif;
}
html,body{height:100%;overflow:hidden;background:#0d1117;color:var(--text-primary)}
body{font-family:var(--font-sans)}
#map{width:100%;height:100%;z-index:1}

.glass{
  background:var(--glass-bg);
  backdrop-filter:blur(var(--glass-blur));
  -webkit-backdrop-filter:blur(var(--glass-blur));
  border:1px solid var(--glass-border);
  border-radius:12px;
}

/* Info Panel */
#info-panel{
  position:absolute;top:16px;right:16px;z-index:1000;
  width:300px;padding:20px;
  transition:opacity 0.35s ease,transform 0.35s ease;
  opacity:0;transform:translateX(20px);pointer-events:none;
}
#info-panel.visible{opacity:1;transform:translateX(0);pointer-events:auto}
#info-panel h2{
  font-family:var(--font-serif);font-size:1.45rem;font-weight:700;
  margin-bottom:2px;color:var(--text-primary);line-height:1.2;
}
#info-panel .subtitle{
  font-size:0.78rem;color:var(--text-secondary);margin-bottom:14px;
  font-style:italic;line-height:1.3;
}
#info-panel .stats{display:grid;grid-template-columns:1fr 1fr;gap:10px}
#info-panel .stat-item{display:flex;flex-direction:column}
#info-panel .stat-label{font-size:0.68rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em}
#info-panel .stat-value{font-size:0.95rem;font-weight:600;color:var(--text-primary);margin-top:2px}
#info-panel .close-btn{
  position:absolute;top:10px;right:14px;background:none;border:none;
  color:var(--text-secondary);cursor:pointer;font-size:1.2rem;line-height:1;
}
#info-panel .close-btn:hover{color:var(--text-primary)}

/* Legend */
#legend{
  position:absolute;top:16px;left:16px;z-index:1000;
  padding:14px 16px;max-height:calc(100vh - 140px);overflow-y:auto;
  width:200px;
}
#legend h3{
  font-family:var(--font-serif);font-size:1.05rem;font-weight:600;
  margin-bottom:10px;color:var(--text-primary);
}
#legend .legend-section{margin-bottom:8px}
#legend .legend-section-title{
  font-size:0.62rem;text-transform:uppercase;letter-spacing:0.08em;
  color:var(--text-muted);margin-bottom:5px;font-weight:600;
}
.legend-item{
  display:flex;align-items:center;gap:8px;padding:3px 6px;
  border-radius:6px;cursor:pointer;transition:background 0.2s;
  font-size:0.78rem;color:var(--text-secondary);
}
.legend-item:hover{background:rgba(255,255,255,0.06);color:var(--text-primary)}
.legend-swatch{
  width:13px;height:13px;border-radius:3px;flex-shrink:0;
  border:1px solid rgba(255,255,255,0.12);
}

/* Timeline */
#timeline{
  position:absolute;bottom:20px;left:50%;transform:translateX(-50%);z-index:1000;
  padding:18px 30px 22px;width:500px;max-width:calc(100vw - 32px);
  text-align:center;
}
#timeline-year{
  font-family:var(--font-serif);font-size:2rem;font-weight:700;
  color:var(--accent);line-height:1;margin-bottom:2px;
}
#timeline-era{
  font-size:0.78rem;color:var(--text-secondary);margin-bottom:16px;
  font-style:italic;
}
#timeline-track{
  position:relative;width:100%;height:40px;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 6px;
}
#timeline-line{
  position:absolute;top:50%;left:6px;right:6px;height:3px;
  background:rgba(255,255,255,0.08);border-radius:2px;transform:translateY(-50%);
}
#timeline-fill{
  position:absolute;top:50%;left:6px;height:3px;
  background:var(--accent);border-radius:2px;transform:translateY(-50%);
  transition:width 0.4s ease;
}
.timeline-dot{
  position:relative;z-index:2;width:14px;height:14px;
  border-radius:50%;background:rgba(255,255,255,0.12);
  border:2px solid rgba(255,255,255,0.2);
  cursor:pointer;transition:all 0.3s ease;
  display:flex;align-items:center;justify-content:center;
}
.timeline-dot:hover{
  background:rgba(129,178,154,0.3);border-color:var(--accent);
  transform:scale(1.2);
}
.timeline-dot.active{
  width:18px;height:18px;
  background:var(--accent);border-color:#fff;
  box-shadow:0 0 12px rgba(129,178,154,0.5);
}
#timeline-labels{
  display:flex;justify-content:space-between;
  margin-top:4px;padding:0 2px;
}
#timeline-labels span{
  font-size:0.68rem;color:var(--text-muted);
  width:50px;text-align:center;
  font-family:var(--font-sans);font-weight:500;
}

/* Home button */
#home-btn{
  position:absolute;top:16px;left:224px;z-index:1000;
  width:34px;height:34px;border-radius:8px;
  background:var(--glass-bg);backdrop-filter:blur(var(--glass-blur));
  border:1px solid var(--glass-border);
  color:var(--text-secondary);cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  font-size:1.1rem;transition:all 0.2s;
}
#home-btn:hover{color:var(--text-primary);background:rgba(13,17,23,0.95)}

/* Water labels */
.water-label{
  font-family:var(--font-serif);font-style:italic;
  color:rgba(100,160,210,0.5);font-weight:400;
  white-space:nowrap;pointer-events:none;
}
.water-label-lg{font-size:13px;letter-spacing:0.15em}
.water-label-sm{font-size:11px;letter-spacing:0.1em}

/* Country/entity labels on map */
.entity-label{
  font-family:var(--font-serif);font-weight:700;
  white-space:nowrap;pointer-events:none;text-align:center;
  text-transform:uppercase;letter-spacing:3px;
  text-shadow:0 1px 6px rgba(0,0,0,0.8),0 0 20px rgba(0,0,0,0.5);
  transition:opacity 0.4s ease;
}
.entity-label-ca{font-size:12px;color:rgba(230,237,243,0.82)}
.entity-label-neighbor{
  font-size:10px;color:#6b7280;font-style:italic;
  letter-spacing:4px;font-weight:400;text-transform:uppercase;
}
.entity-label .sub{
  display:block;font-family:var(--font-sans);font-weight:400;
  font-size:8.5px;color:rgba(139,148,158,0.7);margin-top:2px;
  font-style:italic;text-transform:none;letter-spacing:0.5px;
}

/* City markers */
.city-marker{pointer-events:none;text-align:center;transition:opacity 0.35s ease}
.city-dot{
  width:5px;height:5px;border-radius:50%;
  background:rgba(230,237,243,0.8);border:1px solid rgba(0,0,0,0.4);
  margin:0 auto 2px;
}
.city-dot.capital{
  width:8px;height:8px;background:#F2CC8F;
  border:1.5px solid rgba(0,0,0,0.5);
  box-shadow:0 0 6px rgba(242,204,143,0.4);
}
.city-name{
  font-family:var(--font-sans);font-size:10px;
  color:rgba(230,237,243,0.7);white-space:nowrap;
  text-shadow:0 1px 3px rgba(0,0,0,0.9),0 0 8px rgba(0,0,0,0.6);
}
.city-name.capital-name{font-weight:600;font-size:11px;color:rgba(242,204,143,0.9)}

/* Leaflet overrides */
.leaflet-control-zoom{display:none}
.leaflet-control-scale-line{
  background:rgba(13,17,23,0.8)!important;
  border-color:rgba(255,255,255,0.15)!important;
  color:var(--text-secondary)!important;
  font-family:var(--font-sans)!important;font-size:10px!important;
  backdrop-filter:blur(8px);
}

/* SVG overlay pane transition */
.leaflet-overlay-pane{transition:opacity 0.35s ease}
</style>
</head>
<body>
<div id="map"></div>

<!-- Info Panel -->
<div id="info-panel" class="glass">
  <button class="close-btn" onclick="closeInfoPanel()">&times;</button>
  <h2 id="info-name"></h2>
  <div class="subtitle" id="info-subtitle"></div>
  <div class="stats">
    <div class="stat-item"><span class="stat-label">Population</span><span class="stat-value" id="info-pop"></span></div>
    <div class="stat-item"><span class="stat-label">Area</span><span class="stat-value" id="info-area"></span></div>
    <div class="stat-item"><span class="stat-label">GDP PPP</span><span class="stat-value" id="info-gdp"></span></div>
    <div class="stat-item"><span class="stat-label">Currency</span><span class="stat-value" id="info-currency"></span></div>
  </div>
</div>

<!-- Legend -->
<div id="legend" class="glass">
  <h3 id="legend-title">Central Asia</h3>
  <div class="legend-section">
    <div class="legend-section-title" id="legend-ca-title">Entities</div>
    <div id="legend-ca"></div>
  </div>
  <div class="legend-section">
    <div class="legend-section-title">Neighbors</div>
    <div id="legend-neighbors"></div>
  </div>
</div>

<!-- Timeline -->
<div id="timeline" class="glass">
  <div id="timeline-year">2024</div>
  <div id="timeline-era">Modern Era</div>
  <div id="timeline-track">
    <div id="timeline-line"></div>
    <div id="timeline-fill"></div>
  </div>
  <div id="timeline-labels"></div>
</div>

<!-- Home Button -->
<button id="home-btn" title="Reset view">&#8962;</button>

<script>
// ===== GEODATA (injected) =====
const GEODATA = ''' + geodata_raw + r''';

// ===== ERAS =====
const ERAS = [1900, 1920, 1924, 1936, 1991, 2024];
const ERA_NAMES = {
  1900: 'Russian Imperial Era',
  1920: 'Soviet Takeover',
  1924: 'National Delimitation',
  1936: 'Full SSR Status',
  1991: 'Independence',
  2024: 'Modern Era'
};

// ===== COLORS =====
const NEIGHBOR_STYLES = {
  RU:{fill:'#2d3748',name:'Russia'},
  CN:{fill:'#1a365d',name:'China'},
  IR:{fill:'#3d3028',name:'Iran'},
  AF:{fill:'#3d2c4a',name:'Afghanistan'},
  PK:{fill:'#2a3a2e',name:'Pakistan'},
  MN:{fill:'#2d3340',name:'Mongolia'},
  AZ:{fill:'#2a3340',name:'Azerbaijan'},
  GE:{fill:'#2e2a34',name:'Georgia'}
};

// Modern CA colors (used for 1936/1991/2024)
const CA_COLORS = {KZ:'#E07A5F',UZ:'#81B29A',TM:'#F2CC8F',KG:'#3D85C6',TJ:'#9B72CF'};

// Neighbor label positions (visual center within clipped bounds)
const NEIGHBOR_LABEL_POS = {
  RU:[52.5,68], CN:[40,82], IR:[34,55], AF:[34.5,67],
  PK:[32,69], MN:[48,88], AZ:[40.5,48.5], GE:[42,44.3]
};

// ===== ERA ENTITY CONFIG =====
// For 1936/1991/2024 — define what entities show on the map
const ERA_ENTITIES = {
  1936: {
    KZ_SSR:{code:'KZ',color:'#E07A5F',name:'Kazakh SSR',subtitle:'Union Republic since 1936',center:[48,67]},
    UZ_SSR:{code:'UZ',color:'#81B29A',name:'Uzbek SSR',subtitle:'Union Republic since 1924',center:[41.3,64.5]},
    TM_SSR:{code:'TM',color:'#F2CC8F',name:'Turkmen SSR',subtitle:'Union Republic since 1924',center:[39,59.5]},
    KG_SSR:{code:'KG',color:'#3D85C6',name:'Kirghiz SSR',subtitle:'Union Republic since 1936',center:[41.5,74.5]},
    TJ_SSR:{code:'TJ',color:'#9B72CF',name:'Tajik SSR',subtitle:'Union Republic since 1929',center:[38.8,70.8]}
  },
  1991: {
    KZ:{code:'KZ',color:'#E07A5F',name:'Republic of Kazakhstan',subtitle:'Independence: Dec 16, 1991',center:[48,67]},
    UZ:{code:'UZ',color:'#81B29A',name:'Republic of Uzbekistan',subtitle:'Independence: Sep 1, 1991',center:[41.3,64.5]},
    TM:{code:'TM',color:'#F2CC8F',name:'Republic of Turkmenistan',subtitle:'Independence: Oct 27, 1991',center:[39,59.5]},
    KG:{code:'KG',color:'#3D85C6',name:'Republic of Kyrgyzstan',subtitle:'Independence: Aug 31, 1991',center:[41.5,74.5]},
    TJ:{code:'TJ',color:'#9B72CF',name:'Republic of Tajikistan',subtitle:'Independence: Sep 9, 1991',center:[38.8,70.8]}
  },
  2024: {
    KZ:{code:'KZ',color:'#E07A5F',name:'Kazakhstan',subtitle:'',center:[48,67]},
    UZ:{code:'UZ',color:'#81B29A',name:'Uzbekistan',subtitle:'',center:[41.3,64.5]},
    TM:{code:'TM',color:'#F2CC8F',name:'Turkmenistan',subtitle:'',center:[39,59.5]},
    KG:{code:'KG',color:'#3D85C6',name:'Kyrgyzstan',subtitle:'',center:[41.5,74.5]},
    TJ:{code:'TJ',color:'#9B72CF',name:'Tajikistan',subtitle:'',center:[38.8,70.8]}
  }
};

// Historical entity label centers (1900/1920/1924 come from geodata keys)
const HIST_LABEL_POS = {
  // 1900
  TURKESTAN:[40.5,66], BUKHARA:[38.8,67], KHIVA:[42,59.5], STEPPE:[49,62],
  // 1920
  TURKESTAN_ASSR:[40.5,66], BUKHARA_PSR:[38.8,67], KHOREZM_PSR:[42,59.5], KIRGHIZ_ASSR:[49,62],
  // 1924
  UZ_SSR:[40,67], TM_SSR:[39,59.5], KARA_KIRGHIZ:[41.5,74.5], KZ_ASSR:[48,67]
};

// ===== INFO PANEL DATA PER ERA =====
const INFO_DATA = {
  1936: {
    KZ_SSR:{pop:'6.1M',area:'2,724,900 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'},
    UZ_SSR:{pop:'6.3M',area:'448,978 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'},
    TM_SSR:{pop:'1.3M',area:'491,210 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'},
    KG_SSR:{pop:'1.5M',area:'199,951 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'},
    TJ_SSR:{pop:'1.5M',area:'143,100 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'}
  },
  1991: {
    KZ:{pop:'16.5M',area:'2,724,900 km\u00b2',gdp:'~$120B',currency:'Soviet Ruble \u2192 Tenge (1993)'},
    UZ:{pop:'20.7M',area:'448,978 km\u00b2',gdp:'~$60B',currency:"Soviet Ruble \u2192 So'm (1993)"},
    TM:{pop:'3.7M',area:'491,210 km\u00b2',gdp:'~$18B',currency:'Soviet Ruble \u2192 Manat (1993)'},
    KG:{pop:'4.4M',area:'199,951 km\u00b2',gdp:'~$12B',currency:'Soviet Ruble \u2192 Som (1993)'},
    TJ:{pop:'5.3M',area:'143,100 km\u00b2',gdp:'~$8B',currency:'Soviet Ruble \u2192 Somoni (2000)'}
  },
  2024: {
    KZ:{pop:'19.8M',area:'2,724,900 km\u00b2',gdp:'$604B',currency:'Tenge (\u20b8)'},
    UZ:{pop:'36.0M',area:'448,978 km\u00b2',gdp:'$301B',currency:"So'm"},
    TM:{pop:'6.5M',area:'491,210 km\u00b2',gdp:'$112B',currency:'Manat (m)'},
    KG:{pop:'7.1M',area:'199,951 km\u00b2',gdp:'$43B',currency:'Som'},
    TJ:{pop:'10.1M',area:'143,100 km\u00b2',gdp:'$46B',currency:'Somoni (SM)'}
  },
  1900: {
    TURKESTAN:{pop:'~6M',area:'~1,707,000 km\u00b2',gdp:'\u2014',currency:'Russian Ruble'},
    BUKHARA:{pop:'~2.5M',area:'~203,000 km\u00b2',gdp:'\u2014',currency:'Tanga (Bukharan)'},
    KHIVA:{pop:'~800K',area:'~62,000 km\u00b2',gdp:'\u2014',currency:'Tilla (Khivan)'},
    STEPPE:{pop:'~4M',area:'~2,400,000 km\u00b2',gdp:'\u2014',currency:'Russian Ruble'}
  },
  1920: {
    TURKESTAN_ASSR:{pop:'~5.5M',area:'~1,707,000 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'},
    BUKHARA_PSR:{pop:'~2M',area:'~203,000 km\u00b2',gdp:'\u2014',currency:'Bukharan Ruble'},
    KHOREZM_PSR:{pop:'~600K',area:'~62,000 km\u00b2',gdp:'\u2014',currency:'Khorezmian Ruble'},
    KIRGHIZ_ASSR:{pop:'~4.5M',area:'~2,400,000 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'}
  },
  1924: {
    UZ_SSR:{pop:'~5M',area:'~590,000 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'},
    TM_SSR:{pop:'~1M',area:'~491,000 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'},
    KARA_KIRGHIZ:{pop:'~1M',area:'~199,000 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'},
    KZ_ASSR:{pop:'~6M',area:'~2,724,000 km\u00b2',gdp:'\u2014',currency:'Soviet Ruble'}
  }
};

// ===== COMPLETE CITY DATABASE =====
const CITIES = {
  tashkent:{lat:41.299,lng:69.240,
    names:{1900:'Tashkent',1920:'Tashkent',1924:'Tashkent',1936:'Tashkent',1991:'Tashkent',2024:'Tashkent'},
    tier:{1900:0,1920:0,1924:1,1936:0,1991:0,2024:0}},
  almaty:{lat:43.238,lng:76.946,
    names:{1900:'Verny',1920:'Verny',1924:'Alma-Ata',1936:'Alma-Ata',1991:'Almaty',2024:'Almaty'},
    tier:{1900:1,1920:1,1924:1,1936:1,1991:1,2024:1}},
  bishkek:{lat:42.874,lng:74.569,
    names:{1900:'Pishpek',1920:'Pishpek',1924:'Pishpek',1936:'Frunze',1991:'Bishkek',2024:'Bishkek'},
    tier:{1900:2,1920:2,1924:2,1936:0,1991:0,2024:0}},
  dushanbe:{lat:38.560,lng:68.774,
    names:{1900:'Dyushambe',1920:'Dyushambe',1924:'Dyushambe',1936:'Stalinabad',1991:'Dushanbe',2024:'Dushanbe'},
    tier:{1900:4,1920:4,1924:3,1936:0,1991:0,2024:0}},
  astana:{lat:51.169,lng:71.449,
    names:{1900:'Akmolinsk',1920:'Akmolinsk',1924:'Akmolinsk',1936:'Akmolinsk',1991:'Tselinograd',2024:'Astana'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:2,2024:0}},
  ashgabat:{lat:37.960,lng:58.326,
    names:{1900:'Ashkhabad',1920:'Poltoratsk',1924:'Ashkhabad',1936:'Ashkhabad',1991:'Ashgabat',2024:'Ashgabat'},
    tier:{1900:1,1920:1,1924:0,1936:0,1991:0,2024:0}},
  bukhara:{lat:39.768,lng:64.421,
    names:{1900:'Bukhara',1920:'Bukhara',1924:'Bukhara',1936:'Bukhara',1991:'Bukhara',2024:'Bukhara'},
    tier:{1900:0,1920:0,1924:1,1936:1,1991:1,2024:1}},
  khiva:{lat:41.378,lng:60.364,
    names:{1900:'Khiva',1920:'Khiva',1924:'Khiva',1936:'Khiva',1991:'Khiva',2024:'Khiva'},
    tier:{1900:0,1920:0,1924:3,1936:3,1991:3,2024:3}},
  samarkand:{lat:39.654,lng:66.960,
    names:{1900:'Samarkand',1920:'Samarkand',1924:'Samarkand',1936:'Samarkand',1991:'Samarkand',2024:'Samarkand'},
    tier:{1900:1,1920:1,1924:0,1936:1,1991:1,2024:1}},
  khujand:{lat:40.282,lng:69.629,
    names:{1900:'Khodjent',1920:'Khodjent',1924:'Khodjent',1936:'Leninabad',1991:'Khujand',2024:'Khujand'},
    tier:{1900:2,1920:2,1924:2,1936:1,1991:1,2024:1}},
  mary:{lat:37.594,lng:61.831,
    names:{1900:'Merv',1920:'Merv',1924:'Mary',1936:'Mary',1991:'Mary',2024:'Mary'},
    tier:{1900:2,1920:2,1924:2,1936:2,1991:2,2024:2}},
  turkmenbashi:{lat:40.049,lng:52.960,
    names:{1900:'Krasnovodsk',1920:'Krasnovodsk',1924:'Krasnovodsk',1936:'Krasnovodsk',1991:'Krasnovodsk',2024:'Turkmenbashi'},
    tier:{1900:2,1920:2,1924:3,1936:3,1991:3,2024:3}},
  atyrau:{lat:47.105,lng:51.876,
    names:{1900:'Guryev',1920:'Guryev',1924:'Guryev',1936:'Guryev',1991:'Atyrau',2024:'Atyrau'},
    tier:{1900:3,1920:3,1924:2,1936:2,1991:2,2024:2}},
  semey:{lat:50.411,lng:80.228,
    names:{1900:'Semipalatinsk',1920:'Semipalatinsk',1924:'Semipalatinsk',1936:'Semipalatinsk',1991:'Semipalatinsk',2024:'Semey'},
    tier:{1900:2,1920:2,1924:3,1936:3,1991:3,2024:3}},
  turkmenabat:{lat:39.073,lng:63.572,
    names:{1900:'Chardzhou',1920:'Chardzhou',1924:'Chardzhou',1936:'Chardzhou',1991:'Chardzhou',2024:'Turkmenabat'},
    tier:{1900:2,1920:2,1924:2,1936:2,1991:2,2024:2}},
  nukus:{lat:42.462,lng:59.603,
    names:{1900:'Nukus',1920:'Nukus',1924:'Nukus',1936:'Nukus',1991:'Nukus',2024:'Nukus'},
    tier:{1900:3,1920:3,1924:2,1936:2,1991:2,2024:2}},
  kokand:{lat:40.528,lng:70.943,
    names:{1900:'Kokand',1920:'Kokand',1924:'Kokand',1936:'Kokand',1991:'Kokand',2024:'Kokand'},
    tier:{1900:1,1920:2,1924:3,1936:3,1991:3,2024:3}},
  namangan:{lat:41.000,lng:71.672,
    names:{1900:'Namangan',1920:'Namangan',1924:'Namangan',1936:'Namangan',1991:'Namangan',2024:'Namangan'},
    tier:{1900:2,1920:2,1924:2,1936:1,1991:1,2024:1}},
  andijan:{lat:40.783,lng:72.344,
    names:{1900:'Andijan',1920:'Andijan',1924:'Andijan',1936:'Andijan',1991:'Andijan',2024:'Andijan'},
    tier:{1900:2,1920:2,1924:2,1936:2,1991:2,2024:2}},
  fergana:{lat:40.384,lng:71.789,
    names:{1900:'New Margilan',1920:'New Margilan',1924:'Fergana',1936:'Fergana',1991:'Fergana',2024:'Fergana'},
    tier:{1900:2,1920:2,1924:2,1936:2,1991:2,2024:2}},
  shymkent:{lat:42.315,lng:69.597,
    names:{1900:'Chimkent',1920:'Chimkent',1924:'Chimkent',1936:'Chimkent',1991:'Shymkent',2024:'Shymkent'},
    tier:{1900:2,1920:2,1924:1,1936:1,1991:1,2024:1}},
  karaganda:{lat:49.802,lng:73.102,
    names:{1900:'Karaganda',1920:'Karaganda',1924:'Karaganda',1936:'Karaganda',1991:'Karaganda',2024:'Karaganda'},
    tier:{1900:4,1920:4,1924:3,1936:2,1991:2,2024:2}},
  aktobe:{lat:50.300,lng:57.210,
    names:{1900:'Aktyubinsk',1920:'Aktyubinsk',1924:'Aktyubinsk',1936:'Aktyubinsk',1991:'Aktobe',2024:'Aktobe'},
    tier:{1900:3,1920:3,1924:3,1936:2,1991:2,2024:2}},
  osh:{lat:40.530,lng:72.802,
    names:{1900:'Osh',1920:'Osh',1924:'Osh',1936:'Osh',1991:'Osh',2024:'Osh'},
    tier:{1900:2,1920:2,1924:2,1936:2,1991:2,2024:2}},
  navoi:{lat:40.103,lng:65.379,
    names:{1900:'Kermine',1920:'Kermine',1924:'Kermine',1936:'Kermine',1991:'Navoi',2024:'Navoi'},
    tier:{1900:4,1920:4,1924:4,1936:4,1991:3,2024:3}},
  karshi:{lat:38.861,lng:65.798,
    names:{1900:'Karshi',1920:'Karshi',1924:'Karshi',1936:'Karshi',1991:'Karshi',2024:'Karshi'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  urgench:{lat:41.551,lng:60.632,
    names:{1900:'Urgench',1920:'Urgench',1924:'Urgench',1936:'Urgench',1991:'Urgench',2024:'Urgench'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  jizzakh:{lat:40.116,lng:67.842,
    names:{1900:'Jizzakh',1920:'Jizzakh',1924:'Jizzakh',1936:'Jizzakh',1991:'Jizzakh',2024:'Jizzakh'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  termez:{lat:37.224,lng:67.278,
    names:{1900:'Termez',1920:'Termez',1924:'Termez',1936:'Termez',1991:'Termez',2024:'Termez'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  jalalabad:{lat:40.933,lng:73.002,
    names:{1900:'Jalal-Abad',1920:'Jalal-Abad',1924:'Jalal-Abad',1936:'Jalal-Abad',1991:'Jalal-Abad',2024:'Jalal-Abad'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  karakol:{lat:42.491,lng:78.390,
    names:{1900:'Karakol',1920:'Karakol',1924:'Karakol',1936:'Przhevalsk',1991:'Karakol',2024:'Karakol'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  kulob:{lat:38.543,lng:69.784,
    names:{1900:'Kulyab',1920:'Kulyab',1924:'Kulyab',1936:'Kulyab',1991:'Kulob',2024:'Kulob'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  bokhtar:{lat:37.836,lng:68.781,
    names:{1900:'Kurgan-Tyube',1920:'Kurgan-Tyube',1924:'Kurgan-Tyube',1936:'Kurgan-Tyube',1991:'Kurgan-Tyube',2024:'Bokhtar'},
    tier:{1900:4,1920:4,1924:4,1936:3,1991:3,2024:3}},
  istaravshan:{lat:39.914,lng:69.004,
    names:{1900:'Ura-Tyube',1920:'Ura-Tyube',1924:'Ura-Tyube',1936:'Ura-Tyube',1991:'Istaravshan',2024:'Istaravshan'},
    tier:{1900:4,1920:4,1924:4,1936:4,1991:4,2024:4}},
  khorog:{lat:37.536,lng:71.513,
    names:{1900:'Khorog',1920:'Khorog',1924:'Khorog',1936:'Khorog',1991:'Khorog',2024:'Khorog'},
    tier:{1900:4,1920:4,1924:4,1936:3,1991:3,2024:3}},
  panjakent:{lat:39.490,lng:67.608,
    names:{1900:'Panjikent',1920:'Panjikent',1924:'Panjikent',1936:'Panjikent',1991:'Panjakent',2024:'Panjakent'},
    tier:{1900:4,1920:4,1924:4,1936:4,1991:4,2024:4}},
  pavlodar:{lat:52.287,lng:76.954,
    names:{1900:'Pavlodar',1920:'Pavlodar',1924:'Pavlodar',1936:'Pavlodar',1991:'Pavlodar',2024:'Pavlodar'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  kostanay:{lat:53.214,lng:63.632,
    names:{1900:'Kostanay',1920:'Kostanay',1924:'Kostanay',1936:'Kostanay',1991:'Kostanay',2024:'Kostanay'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  oral:{lat:51.233,lng:51.366,
    names:{1900:'Uralsk',1920:'Uralsk',1924:'Uralsk',1936:'Uralsk',1991:'Oral',2024:'Oral'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  petropavl:{lat:54.867,lng:69.149,
    names:{1900:'Petropavlovsk',1920:'Petropavlovsk',1924:'Petropavlovsk',1936:'Petropavlovsk',1991:'Petropavl',2024:'Petropavl'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  kyzylorda:{lat:44.853,lng:65.509,
    names:{1900:'Perovsk',1920:'Perovsk',1924:'Kzyl-Orda',1936:'Kzyl-Orda',1991:'Kyzylorda',2024:'Kyzylorda'},
    tier:{1900:3,1920:3,1924:2,1936:2,1991:3,2024:3}},
  taraz:{lat:42.900,lng:71.366,
    names:{1900:'Aulie-Ata',1920:'Aulie-Ata',1924:'Aulie-Ata',1936:'Mirzoyan',1991:'Taraz',2024:'Taraz'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  aktau:{lat:43.650,lng:51.147,
    names:{1900:'Fort Alexandrovsky',1920:'Fort Alexandrovsky',1924:'Fort Shevchenko',1936:'Fort Shevchenko',1991:'Aktau',2024:'Aktau'},
    tier:{1900:4,1920:4,1924:4,1936:4,1991:3,2024:3}},
  turkestan:{lat:43.301,lng:68.252,
    names:{1900:'Turkestan',1920:'Turkestan',1924:'Turkestan',1936:'Turkestan',1991:'Turkestan',2024:'Turkestan'},
    tier:{1900:2,1920:2,1924:3,1936:4,1991:4,2024:4}},
  ustkamenogorsk:{lat:49.948,lng:82.628,
    names:{1900:'Ust-Kamenogorsk',1920:'Ust-Kamenogorsk',1924:'Ust-Kamenogorsk',1936:'Ust-Kamenogorsk',1991:'Ust-Kamenogorsk',2024:'Oskemen'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  dashoguz:{lat:41.836,lng:59.967,
    names:{1900:'Dashkhovuz',1920:'Dashkhovuz',1924:'Dashkhovuz',1936:'Tashauz',1991:'Dashoguz',2024:'Dashoguz'},
    tier:{1900:3,1920:3,1924:3,1936:3,1991:3,2024:3}},
  balkanabat:{lat:39.510,lng:54.367,
    names:{1900:'Jebel',1920:'Jebel',1924:'Nebit-Dag',1936:'Nebit-Dag',1991:'Balkanabat',2024:'Balkanabat'},
    tier:{1900:4,1920:4,1924:4,1936:4,1991:4,2024:4}},
  naryn:{lat:41.429,lng:75.991,
    names:{1900:'Naryn',1920:'Naryn',1924:'Naryn',1936:'Naryn',1991:'Naryn',2024:'Naryn'},
    tier:{1900:4,1920:4,1924:4,1936:4,1991:4,2024:4}},
  talas:{lat:42.516,lng:72.243,
    names:{1900:'Talas',1920:'Talas',1924:'Talas',1936:'Talas',1991:'Talas',2024:'Talas'},
    tier:{1900:4,1920:4,1924:4,1936:4,1991:4,2024:4}},
  batken:{lat:40.063,lng:70.819,
    names:{1900:'Batken',1920:'Batken',1924:'Batken',1936:'Batken',1991:'Batken',2024:'Batken'},
    tier:{1900:4,1920:4,1924:4,1936:4,1991:4,2024:4}}
};

// ===== WATER LABELS =====
const WATER_LABELS = [
  {name:'Caspian Sea',lat:42.0,lng:50.5,cls:'water-label-lg'},
  {name:'Aral Sea',lat:45.0,lng:59.5,cls:'water-label-sm'},
  {name:'Lake Balkhash',lat:46.5,lng:74.5,cls:'water-label-sm'},
  {name:'Issyk-Kul',lat:42.45,lng:77.2,cls:'water-label-sm'}
];

// ===== STATE =====
let currentEra = 2024;
let caLayer = null;
let neighborLayer = null;
let entityLabels = [];
let neighborLabels = [];
let cityMarkers = [];
let highlightedKey = null;

// ===== MAP INIT =====
const map = L.map('map', {
  center: [42.0, 64.0],
  zoom: 5,
  minZoom: 5,
  maxZoom: 14,
  maxBounds: L.latLngBounds(L.latLng(30, 44), L.latLng(56, 90)),
  maxBoundsViscosity: 1.0,
  zoomControl: false,
  renderer: L.svg()
});

L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png', {
  attribution:'&copy; OSM &copy; CARTO',
  subdomains:'abcd',maxZoom:19
}).addTo(map);

L.control.scale({position:'bottomleft',imperial:false}).addTo(map);

// ===== NEIGHBORS (static — same in all eras) =====
function renderNeighbors() {
  if (neighborLayer) map.removeLayer(neighborLayer);
  neighborLabels.forEach(m => map.removeLayer(m));
  neighborLabels = [];

  const features = Object.entries(GEODATA.neighbors).map(([code, geom]) => ({
    type: 'Feature',
    properties: { code },
    geometry: geom
  }));

  neighborLayer = L.geoJSON({type:'FeatureCollection',features}, {
    style: f => {
      const s = NEIGHBOR_STYLES[f.properties.code];
      return {
        fillColor: s ? s.fill : '#222',
        fillOpacity: 0.6,
        color: '#4a5568',
        weight: 1.5
      };
    },
    interactive: false,
    renderer: L.svg()
  }).addTo(map);

  // Neighbor labels
  Object.entries(NEIGHBOR_STYLES).forEach(([code, s]) => {
    const pos = NEIGHBOR_LABEL_POS[code];
    if (!pos) return;
    let displayName = s.name;
    if (currentEra === 1991 && code === 'RU') displayName = 'Russian Federation';
    const icon = L.divIcon({
      className: 'entity-label entity-label-neighbor',
      html: displayName,
      iconSize: null
    });
    const m = L.marker(pos, {icon, interactive:false}).addTo(map);
    neighborLabels.push(m);
  });
}

// ===== CA ENTITIES (change per era) =====
function getEraEntities(era) {
  // For 1900, 1920, 1924: use historical data from GEODATA
  if (GEODATA.historical[era]) {
    const hist = GEODATA.historical[era];
    return Object.entries(hist).map(([key, entity]) => ({
      key,
      geometry: entity.geometry,
      color: entity.color,
      name: entity.name,
      subtitle: entity.subtitle,
      center: HIST_LABEL_POS[key] || [42, 64]
    }));
  }
  // For 1936, 1991, 2024: use modern geo with era-specific metadata
  const entDef = ERA_ENTITIES[era];
  if (!entDef) return [];
  return Object.entries(entDef).map(([key, ent]) => ({
    key,
    geometry: GEODATA.modern[ent.code],
    color: ent.color,
    name: ent.name,
    subtitle: ent.subtitle,
    center: ent.center
  }));
}

function renderCA() {
  if (caLayer) map.removeLayer(caLayer);
  entityLabels.forEach(m => map.removeLayer(m));
  entityLabels = [];

  const entities = getEraEntities(currentEra);
  const features = entities.map(e => ({
    type: 'Feature',
    properties: { key: e.key, color: e.color, name: e.name, subtitle: e.subtitle },
    geometry: e.geometry
  }));

  caLayer = L.geoJSON({type:'FeatureCollection',features}, {
    style: f => ({
      fillColor: f.properties.color,
      fillOpacity: f.properties.key === highlightedKey ? 0.65 : 0.5,
      color: f.properties.key === highlightedKey ? '#fff' : 'rgba(255,255,255,0.35)',
      weight: f.properties.key === highlightedKey ? 2.5 : 1.5
    }),
    onEachFeature: (f, layer) => {
      layer.on('mouseover', () => {
        highlightedKey = f.properties.key;
        caLayer.setStyle(feat => ({
          fillColor: feat.properties.color,
          fillOpacity: feat.properties.key === highlightedKey ? 0.65 : 0.5,
          color: feat.properties.key === highlightedKey ? '#fff' : 'rgba(255,255,255,0.35)',
          weight: feat.properties.key === highlightedKey ? 2.5 : 1.5
        }));
      });
      layer.on('mouseout', () => {
        highlightedKey = null;
        caLayer.setStyle(feat => ({
          fillColor: feat.properties.color,
          fillOpacity: 0.5,
          color: 'rgba(255,255,255,0.35)',
          weight: 1.5
        }));
      });
      layer.on('click', () => showInfoPanel(f.properties.key));
    },
    renderer: L.svg()
  }).addTo(map);

  // Entity labels
  entities.forEach(e => {
    let html = e.name;
    if (e.subtitle) html += '<span class="sub">' + e.subtitle + '</span>';
    const icon = L.divIcon({
      className: 'entity-label entity-label-ca',
      html,
      iconSize: null
    });
    const m = L.marker(e.center, {icon, interactive:false}).addTo(map);
    entityLabels.push(m);
  });
}

// ===== INFO PANEL =====
function showInfoPanel(key) {
  const eraData = INFO_DATA[currentEra];
  if (!eraData || !eraData[key]) return;
  const data = eraData[key];

  // Get entity name
  let name = key;
  const entities = getEraEntities(currentEra);
  const ent = entities.find(e => e.key === key);
  if (ent) name = ent.name;

  const panel = document.getElementById('info-panel');
  document.getElementById('info-name').textContent = name;
  document.getElementById('info-subtitle').textContent = ent ? (ent.subtitle || '') : '';
  document.getElementById('info-pop').textContent = data.pop;
  document.getElementById('info-area').textContent = data.area;
  document.getElementById('info-gdp').textContent = data.gdp;
  document.getElementById('info-currency').textContent = data.currency;
  panel.classList.add('visible');
}

function closeInfoPanel() {
  document.getElementById('info-panel').classList.remove('visible');
}

// ===== LEGEND =====
function buildLegend() {
  const caDiv = document.getElementById('legend-ca');
  const nbDiv = document.getElementById('legend-neighbors');
  const caTitle = document.getElementById('legend-ca-title');
  caDiv.innerHTML = '';
  nbDiv.innerHTML = '';

  const entities = getEraEntities(currentEra);

  // Set section title based on era
  if (currentEra <= 1924) caTitle.textContent = 'Political Entities';
  else if (currentEra === 1936) caTitle.textContent = 'Soviet Republics';
  else if (currentEra === 1991) caTitle.textContent = 'New Republics';
  else caTitle.textContent = 'Countries';

  entities.forEach(e => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<div class="legend-swatch" style="background:'+e.color+'"></div><span>'+e.name+'</span>';
    item.addEventListener('click', () => {
      map.flyTo(e.center, 6, {duration:1.2});
      showInfoPanel(e.key);
    });
    caDiv.appendChild(item);
  });

  Object.entries(NEIGHBOR_STYLES).forEach(([code, s]) => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    let dn = s.name;
    if (currentEra === 1991 && code === 'RU') dn = 'Russian Federation';
    item.innerHTML = '<div class="legend-swatch" style="background:'+s.fill+'"></div><span>'+dn+'</span>';
    item.addEventListener('click', () => {
      const pos = NEIGHBOR_LABEL_POS[code];
      if (pos) map.flyTo(pos, 6, {duration:1.2});
    });
    nbDiv.appendChild(item);
  });
}

// ===== WATER LABELS =====
const waterMarkers = [];
WATER_LABELS.forEach(w => {
  const icon = L.divIcon({
    className:'water-label '+w.cls,
    html:w.name,
    iconSize:null
  });
  waterMarkers.push(L.marker([w.lat,w.lng],{icon,interactive:false}).addTo(map));
});

// ===== CITIES =====
function tierMinZoom(t) {
  if (t === 0) return 0; // capital — always visible
  if (t === 1) return 5;
  if (t === 2) return 6;
  if (t === 3) return 7;
  return 8;
}

function renderCities() {
  cityMarkers.forEach(m => map.removeLayer(m));
  cityMarkers = [];
  const z = map.getZoom();

  Object.values(CITIES).forEach(city => {
    const t = city.tier[currentEra];
    if (t === undefined || z < tierMinZoom(t)) return;
    const name = city.names[currentEra] || '';
    if (!name) return;
    const isCap = (t === 0);
    const icon = L.divIcon({
      className:'city-marker',
      html:'<div class="city-dot'+(isCap?' capital':'')+'"></div><div class="city-name'+(isCap?' capital-name':'')+'">'+name+'</div>',
      iconSize:[90,28],
      iconAnchor:[45,6]
    });
    cityMarkers.push(L.marker([city.lat,city.lng],{icon,interactive:false}).addTo(map));
  });
}

map.on('zoomend', renderCities);

// ===== TIMELINE =====
const trackEl = document.getElementById('timeline-track');
const labelsEl = document.getElementById('timeline-labels');
const yearEl = document.getElementById('timeline-year');
const eraEl = document.getElementById('timeline-era');
const fillEl = document.getElementById('timeline-fill');

// Build dots
ERAS.forEach((era, i) => {
  const dot = document.createElement('div');
  dot.className = 'timeline-dot' + (era === currentEra ? ' active' : '');
  dot.dataset.era = era;
  dot.title = era + ' \u2014 ' + ERA_NAMES[era];
  dot.addEventListener('click', () => switchEra(era));
  trackEl.appendChild(dot);

  const label = document.createElement('span');
  label.textContent = era;
  labelsEl.appendChild(label);
});

function updateTimelineFill() {
  const idx = ERAS.indexOf(currentEra);
  const pct = ERAS.length > 1 ? (idx / (ERAS.length - 1)) * 100 : 0;
  fillEl.style.width = pct + '%';
}

function switchEra(era) {
  if (era === currentEra) return;
  currentEra = era;

  // Update dots
  document.querySelectorAll('.timeline-dot').forEach(d => {
    d.classList.toggle('active', parseInt(d.dataset.era) === era);
  });
  yearEl.textContent = era;
  eraEl.textContent = ERA_NAMES[era] || '';
  updateTimelineFill();

  // Fade out, swap, fade in
  const overlayPane = document.querySelector('.leaflet-overlay-pane');
  if (overlayPane) {
    overlayPane.style.opacity = '0';
    setTimeout(() => {
      renderCA();
      renderNeighbors();
      renderCities();
      buildLegend();
      closeInfoPanel();
      overlayPane.style.opacity = '1';
    }, 350);
  } else {
    renderCA();
    renderNeighbors();
    renderCities();
    buildLegend();
    closeInfoPanel();
  }
}

// Keyboard nav
document.addEventListener('keydown', e => {
  const idx = ERAS.indexOf(currentEra);
  if (e.key === 'ArrowRight' && idx < ERAS.length - 1) switchEra(ERAS[idx + 1]);
  if (e.key === 'ArrowLeft' && idx > 0) switchEra(ERAS[idx - 1]);
});

// ===== HOME BUTTON =====
document.getElementById('home-btn').addEventListener('click', () => {
  map.flyTo([42.0, 64.0], 5, {duration:1});
  closeInfoPanel();
});

// ===== INITIAL RENDER =====
renderNeighbors();
renderCA();
renderCities();
buildLegend();
updateTimelineFill();
</script>
</body>
</html>'''

# Write the HTML file
with open(OUTPUT_PATH, 'w') as f:
    f.write(html)

fsize = os.path.getsize(OUTPUT_PATH)
print(f"HTML written to {OUTPUT_PATH} ({fsize/1024:.1f} KB)")
