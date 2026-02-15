#!/usr/bin/env python3
"""
STEP 2: Generate the full Central Asia interactive timeline map HTML.
Reads geodata.json and embeds it into the HTML file.
All file writing done via Python file I/O.
"""
import json

GEODATA_PATH = "/home/user/geodata.json"
OUTPUT_PATH = "/home/user/central-asia-map.html"

# Read geodata
with open(GEODATA_PATH) as f:
    geodata_content = f.read()

html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Central Asia — Interactive Timeline Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
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

/* Glassmorphism mixin */
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
  font-family:var(--font-serif);font-size:1.5rem;font-weight:700;
  margin-bottom:4px;color:var(--text-primary);
}
#info-panel .subtitle{
  font-size:0.8rem;color:var(--text-secondary);margin-bottom:14px;
  font-style:italic;
}
#info-panel .stats{display:grid;grid-template-columns:1fr 1fr;gap:10px}
#info-panel .stat-item{display:flex;flex-direction:column}
#info-panel .stat-label{font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em}
#info-panel .stat-value{font-size:1rem;font-weight:600;color:var(--text-primary);margin-top:2px}
#info-panel .close-btn{
  position:absolute;top:10px;right:14px;background:none;border:none;
  color:var(--text-secondary);cursor:pointer;font-size:1.2rem;line-height:1;
}
#info-panel .close-btn:hover{color:var(--text-primary)}

/* Legend */
#legend{
  position:absolute;top:16px;left:16px;z-index:1000;
  padding:16px 18px;max-height:calc(100vh - 120px);overflow-y:auto;
}
#legend h3{
  font-family:var(--font-serif);font-size:1.1rem;font-weight:600;
  margin-bottom:10px;color:var(--text-primary);
}
#legend .legend-section{margin-bottom:10px}
#legend .legend-section-title{
  font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;
  color:var(--text-muted);margin-bottom:6px;
}
.legend-item{
  display:flex;align-items:center;gap:8px;padding:4px 6px;
  border-radius:6px;cursor:pointer;transition:background 0.2s;
  font-size:0.82rem;color:var(--text-secondary);
}
.legend-item:hover{background:rgba(255,255,255,0.06);color:var(--text-primary)}
.legend-swatch{
  width:14px;height:14px;border-radius:3px;flex-shrink:0;
  border:1px solid rgba(255,255,255,0.12);
}

/* Timeline */
#timeline{
  position:absolute;bottom:20px;left:50%;transform:translateX(-50%);z-index:1000;
  padding:16px 28px 20px;width:520px;max-width:calc(100vw - 32px);
  text-align:center;
}
#timeline h4{
  font-family:var(--font-serif);font-size:0.95rem;font-weight:600;
  margin-bottom:10px;color:var(--text-primary);
}
#timeline-slider{
  -webkit-appearance:none;appearance:none;width:100%;height:6px;
  border-radius:3px;background:rgba(255,255,255,0.08);outline:none;
  cursor:pointer;
}
#timeline-slider::-webkit-slider-thumb{
  -webkit-appearance:none;appearance:none;width:20px;height:20px;
  border-radius:50%;background:var(--accent);cursor:pointer;
  border:2px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.4);
  transition:transform 0.15s;
}
#timeline-slider::-webkit-slider-thumb:hover{transform:scale(1.2)}
#timeline-slider::-moz-range-thumb{
  width:20px;height:20px;border-radius:50%;background:var(--accent);
  cursor:pointer;border:2px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.4);
}
#timeline-labels{
  display:flex;justify-content:space-between;margin-top:8px;
  font-size:0.72rem;color:var(--text-muted);
}
#timeline-year{
  font-family:var(--font-serif);font-size:1.6rem;font-weight:700;
  color:var(--accent);margin-bottom:2px;
}
#timeline-era{font-size:0.75rem;color:var(--text-secondary);margin-bottom:10px}
#timeline-tooltip{
  font-size:0.7rem;color:#F2CC8F;margin-top:6px;
  opacity:0;transition:opacity 0.3s;
}
#timeline-tooltip.visible{opacity:1}

/* Home button */
#home-btn{
  position:absolute;top:80px;left:62px;z-index:1000;
  width:34px;height:34px;border-radius:6px;
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
  color:rgba(100,160,210,0.55);font-weight:400;
  white-space:nowrap;pointer-events:none;
}
.water-label-lg{font-size:13px;letter-spacing:0.15em}
.water-label-sm{font-size:11px;letter-spacing:0.1em}

/* Country labels on map */
.country-label{
  font-family:var(--font-serif);font-weight:700;
  white-space:nowrap;pointer-events:none;text-align:center;
}
.country-label-ca{font-size:13px;color:rgba(230,237,243,0.8);text-shadow:0 1px 4px rgba(0,0,0,0.7)}
.country-label-neighbor{font-size:11px;color:rgba(139,148,158,0.6)}
.country-label .sub{
  display:block;font-family:var(--font-sans);font-weight:400;
  font-size:9px;color:rgba(139,148,158,0.6);margin-top:1px;
  font-style:italic;
}

/* City markers */
.city-marker{pointer-events:none;text-align:center}
.city-dot{
  width:6px;height:6px;border-radius:50%;
  background:rgba(230,237,243,0.85);border:1px solid rgba(0,0,0,0.4);
  margin:0 auto 2px;
}
.city-dot.capital{
  width:8px;height:8px;background:#F2CC8F;
  border:1.5px solid rgba(0,0,0,0.5);
  box-shadow:0 0 6px rgba(242,204,143,0.4);
}
.city-name{
  font-family:var(--font-sans);font-size:10px;
  color:rgba(230,237,243,0.75);white-space:nowrap;
  text-shadow:0 1px 3px rgba(0,0,0,0.8);
}
.city-name.capital-name{font-weight:600;font-size:11px;color:rgba(242,204,143,0.9)}

/* Leaflet overrides */
.leaflet-control-zoom{display:none}
.leaflet-control-scale-line{
  background:var(--glass-bg)!important;
  border-color:rgba(255,255,255,0.15)!important;
  color:var(--text-secondary)!important;
  font-family:var(--font-sans)!important;font-size:10px!important;
  backdrop-filter:blur(8px);
}
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
    <div class="stat-item"><span class="stat-label">GDP</span><span class="stat-value" id="info-gdp"></span></div>
    <div class="stat-item"><span class="stat-label">Currency</span><span class="stat-value" id="info-currency"></span></div>
  </div>
</div>

<!-- Legend -->
<div id="legend" class="glass">
  <h3>Central Asia</h3>
  <div class="legend-section">
    <div class="legend-section-title">CA Countries</div>
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
  <input type="range" id="timeline-slider" min="1800" max="2024" value="2024" step="1">
  <div id="timeline-labels"><span>1800</span><span>1900</span><span>1991</span><span>2024</span></div>
  <div id="timeline-tooltip">Coming soon — only 1991 &amp; 2024 available</div>
</div>

<!-- Home Button -->
<button id="home-btn" title="Reset view">&#8962;</button>

<script>
// ========== GEODATA ==========
const GEO = ''' + geodata_content + ''';

// ========== CONFIG ==========
const CA_COLORS = {KZ:'#E07A5F',UZ:'#81B29A',TM:'#F2CC8F',KG:'#3D85C6',TJ:'#9B72CF'};
const NEIGHBOR_COLORS = {RU:'#2d3748',CN:'#1a365d',IR:'#4a3728',AF:'#3d2c4a',PK:'#2d4a3e',MN:'#3d3a28',AZ:'#2a3d4a',GE:'#3a2d3d'};
const ALL_COLORS = Object.assign({}, CA_COLORS, NEIGHBOR_COLORS);

const DEFAULT_CENTER = [42, 64];
const DEFAULT_ZOOM = 5;
const BOUNDS = L.latLngBounds([30,44],[56,90]);

// ========== COUNTRY DATA ==========
const COUNTRY_DATA = {
  KZ: {
    name: 'Kazakhstan',
    center: [48.0, 67.0],
    2024: {pop:'19.8M', area:'2,724,900 km\\u00b2', gdp:'$259.3B', currency:'Tenge (KZT)'},
    1991: {pop:'16.5M', area:'2,724,900 km\\u00b2', gdp:'$25.0B', currency:'Soviet Ruble'},
    independence:'Dec 16, 1991'
  },
  UZ: {
    name: 'Uzbekistan',
    center: [41.3, 64.5],
    2024: {pop:'36.0M', area:'448,978 km\\u00b2', gdp:'$90.4B', currency:'Som (UZS)'},
    1991: {pop:'20.7M', area:'448,978 km\\u00b2', gdp:'$14.0B', currency:'Soviet Ruble'},
    independence:'Sep 1, 1991'
  },
  TM: {
    name: 'Turkmenistan',
    center: [39.0, 59.5],
    2024: {pop:'6.5M', area:'488,100 km\\u00b2', gdp:'$59.9B', currency:'Manat (TMT)'},
    1991: {pop:'3.7M', area:'488,100 km\\u00b2', gdp:'$6.0B', currency:'Soviet Ruble'},
    independence:'Oct 27, 1991'
  },
  KG: {
    name: 'Kyrgyzstan',
    center: [41.5, 74.5],
    2024: {pop:'7.1M', area:'199,951 km\\u00b2', gdp:'$12.3B', currency:'Som (KGS)'},
    1991: {pop:'4.4M', area:'199,951 km\\u00b2', gdp:'$2.7B', currency:'Soviet Ruble'},
    independence:'Aug 31, 1991'
  },
  TJ: {
    name: 'Tajikistan',
    center: [38.8, 70.8],
    2024: {pop:'10.1M', area:'143,100 km\\u00b2', gdp:'$12.0B', currency:'Somoni (TJS)'},
    1991: {pop:'5.3M', area:'143,100 km\\u00b2', gdp:'$2.5B', currency:'Soviet Ruble'},
    independence:'Sep 9, 1991'
  },
  RU: {name:'Russia', center:[52,68]},
  CN: {name:'China', center:[40,82]},
  IR: {name:'Iran', center:[35,55]},
  AF: {name:'Afghanistan', center:[35,67]},
  PK: {name:'Pakistan', center:[33,70]},
  MN: {name:'Mongolia', center:[48,88]},
  AZ: {name:'Azerbaijan', center:[40.5,48]},
  GE: {name:'Georgia', center:[42,44.5]}
};

// ========== CITIES ==========
const CITIES = [
  // Capitals
  {name:'Astana', name1991:'Tselinograd', lat:51.16,lng:71.43, country:'KZ', tier:'capital'},
  {name:'Tashkent', lat:41.30,lng:69.28, country:'UZ', tier:'capital'},
  {name:'Ashgabat', lat:37.95,lng:58.38, country:'TM', tier:'capital'},
  {name:'Bishkek', name1991:'Frunze', lat:42.87,lng:74.59, country:'KG', tier:'capital'},
  {name:'Dushanbe', lat:38.56,lng:68.77, country:'TJ', tier:'capital'},
  // Tier 1 — z5
  {name:'Almaty', lat:43.24,lng:76.95, country:'KZ', tier:1},
  {name:'Samarkand', lat:39.65,lng:66.96, country:'UZ', tier:1},
  {name:'Bukhara', lat:39.77,lng:64.42, country:'UZ', tier:1},
  {name:'Shymkent', lat:42.32,lng:69.60, country:'KZ', tier:1},
  {name:'Namangan', lat:41.00,lng:71.67, country:'UZ', tier:1},
  // Tier 2 — z6
  {name:'Karaganda', lat:49.80,lng:73.10, country:'KZ', tier:2},
  {name:'Aktobe', lat:50.30,lng:57.21, country:'KZ', tier:2},
  {name:'Khujand', name1991:'Leninabad', lat:40.28,lng:69.63, country:'TJ', tier:2},
  {name:'Osh', lat:40.53,lng:72.80, country:'KG', tier:2},
  {name:'Nukus', lat:42.46,lng:59.60, country:'UZ', tier:2},
  {name:'Fergana', lat:40.38,lng:71.79, country:'UZ', tier:2},
  {name:'Mary', lat:37.60,lng:61.83, country:'TM', tier:2},
  // Tier 3 — z7
  {name:'Atyrau', name1991:'Guryev', lat:47.12,lng:51.92, country:'KZ', tier:3},
  {name:'Semey', name1991:'Semipalatinsk', lat:50.41,lng:80.23, country:'KZ', tier:3},
  {name:'Kostanay', lat:53.21,lng:63.63, country:'KZ', tier:3},
  {name:'Pavlodar', lat:52.29,lng:76.95, country:'KZ', tier:3},
  {name:'Turkmenabat', name1991:'Chardzhou', lat:39.07,lng:63.58, country:'TM', tier:3},
  {name:'Andijan', lat:40.78,lng:72.34, country:'UZ', tier:3},
  {name:'Navoi', lat:40.10,lng:65.38, country:'UZ', tier:3},
  {name:'Urgench', lat:41.55,lng:60.63, country:'UZ', tier:3},
  {name:'Kulob', lat:38.54,lng:69.78, country:'TJ', tier:3},
  {name:'Karakol', lat:42.49,lng:78.39, country:'KG', tier:3},
  // Tier 4 — z8
  {name:'Taraz', lat:42.90,lng:71.37, country:'KZ', tier:4},
  {name:'Oral', lat:51.23,lng:51.37, country:'KZ', tier:4},
  {name:'Aktau', lat:43.65,lng:51.15, country:'KZ', tier:4},
  {name:'Petropavl', lat:54.87,lng:69.15, country:'KZ', tier:4},
  {name:'Kyzylorda', lat:44.85,lng:65.51, country:'KZ', tier:4},
  {name:'Turkestan', lat:43.30,lng:68.25, country:'KZ', tier:4},
  {name:'Termez', lat:37.22,lng:67.28, country:'UZ', tier:4},
  {name:'Karshi', lat:38.86,lng:65.80, country:'UZ', tier:4},
  {name:'Jizzakh', lat:40.12,lng:67.84, country:'UZ', tier:4},
  {name:'Dashoguz', lat:41.84,lng:59.97, country:'TM', tier:4},
  {name:'Balkanabat', lat:39.51,lng:54.37, country:'TM', tier:4},
  {name:'Turkmenbashi', lat:40.05,lng:52.97, country:'TM', tier:4},
  {name:'Jalal-Abad', lat:40.93,lng:73.00, country:'KG', tier:4},
  {name:'Istaravshan', lat:39.91,lng:69.00, country:'TJ', tier:4},
  {name:'Bokhtar', lat:37.84,lng:68.78, country:'TJ', tier:4}
];

// ========== WATER LABELS ==========
const WATER_LABELS = [
  {name:'Caspian Sea', lat:42.5,lng:50.5, cls:'water-label-lg'},
  {name:'Aral Sea', lat:45.0,lng:59.5, cls:'water-label-sm'},
  {name:'Lake Balkhash', lat:46.5,lng:74.5, cls:'water-label-sm'},
  {name:'Issyk-Kul', lat:42.5,lng:77.2, cls:'water-label-sm'}
];

// ========== STATE ==========
let currentYear = 2024;
let geoLayer = null;
let cityMarkers = [];
let countryLabels = [];
let highlightedCode = null;

// ========== MAP INIT ==========
const map = L.map('map', {
  center: DEFAULT_CENTER,
  zoom: DEFAULT_ZOOM,
  maxBounds: BOUNDS,
  maxBoundsViscosity: 1.0,
  minZoom: 4,
  maxZoom: 10,
  zoomControl: false,
  preferCanvas: false,
  renderer: L.svg()
});

L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap &copy; CARTO',
  subdomains: 'abcd',
  maxZoom: 19
}).addTo(map);

L.control.scale({position:'bottomleft', imperial:false}).addTo(map);

// ========== GEOJSON LAYER ==========
function getStyle(feature) {
  const code = feature.properties.code;
  const isCA = feature.properties.isCA;
  const isHighlighted = (code === highlightedCode);
  return {
    fillColor: ALL_COLORS[code] || '#333',
    fillOpacity: isCA ? (isHighlighted ? 0.65 : 0.45) : (isHighlighted ? 0.45 : 0.25),
    color: isHighlighted ? '#fff' : (isCA ? 'rgba(255,255,255,0.3)' : 'rgba(255,255,255,0.12)'),
    weight: isHighlighted ? 2.5 : (isCA ? 1.5 : 0.8),
  };
}

function onEachFeature(feature, layer) {
  const code = feature.properties.code;
  layer.on('mouseover', function() {
    highlightedCode = code;
    geoLayer.setStyle(getStyle);
  });
  layer.on('mouseout', function() {
    highlightedCode = null;
    geoLayer.setStyle(getStyle);
  });
  layer.on('click', function() {
    showInfoPanel(code);
  });
}

geoLayer = L.geoJSON(GEO, {
  style: getStyle,
  onEachFeature: onEachFeature,
  renderer: L.svg()
}).addTo(map);

// ========== INFO PANEL ==========
function showInfoPanel(code) {
  const cd = COUNTRY_DATA[code];
  if (!cd || !cd[currentYear]) return;
  const data = cd[currentYear];
  const panel = document.getElementById('info-panel');
  document.getElementById('info-name').textContent = getCountryDisplayName(code);
  const sub = document.getElementById('info-subtitle');
  if (cd.independence && currentYear === 1991) {
    sub.textContent = 'Independence: ' + cd.independence;
  } else if (cd.independence) {
    sub.textContent = 'Independent since ' + cd.independence;
  } else {
    sub.textContent = '';
  }
  document.getElementById('info-pop').textContent = data.pop;
  document.getElementById('info-area').textContent = data.area;
  document.getElementById('info-gdp').textContent = data.gdp;
  document.getElementById('info-currency').textContent = data.currency;
  panel.classList.add('visible');
}

function closeInfoPanel() {
  document.getElementById('info-panel').classList.remove('visible');
}

function getCountryDisplayName(code) {
  const cd = COUNTRY_DATA[code];
  if (!cd) return code;
  if (currentYear === 1991 && cd.independence) {
    return 'Republic of ' + cd.name;
  }
  if (currentYear === 1991 && code === 'RU') {
    return 'Russian Federation';
  }
  return cd.name;
}

// ========== LEGEND ==========
function buildLegend() {
  const caDiv = document.getElementById('legend-ca');
  const nbDiv = document.getElementById('legend-neighbors');
  caDiv.innerHTML = '';
  nbDiv.innerHTML = '';
  Object.keys(CA_COLORS).forEach(code => {
    const cd = COUNTRY_DATA[code];
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<div class="legend-swatch" style="background:'+CA_COLORS[code]+'"></div>'+cd.name;
    item.addEventListener('click', () => {
      const c = cd.center;
      map.flyTo(c, 6, {duration: 1.2});
      showInfoPanel(code);
    });
    caDiv.appendChild(item);
  });
  Object.keys(NEIGHBOR_COLORS).forEach(code => {
    const cd = COUNTRY_DATA[code];
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<div class="legend-swatch" style="background:'+NEIGHBOR_COLORS[code]+'"></div>'+cd.name;
    item.addEventListener('click', () => {
      const c = cd.center;
      map.flyTo(c, 6, {duration: 1.2});
    });
    nbDiv.appendChild(item);
  });
}
buildLegend();

// ========== WATER LABELS ==========
WATER_LABELS.forEach(w => {
  const icon = L.divIcon({
    className: 'water-label ' + w.cls,
    html: w.name,
    iconSize: null
  });
  L.marker([w.lat, w.lng], {icon, interactive:false}).addTo(map);
});

// ========== COUNTRY LABELS ==========
function renderCountryLabels() {
  countryLabels.forEach(m => map.removeLayer(m));
  countryLabels = [];

  Object.keys(COUNTRY_DATA).forEach(code => {
    const cd = COUNTRY_DATA[code];
    const isCA = !!CA_COLORS[code];
    let labelHtml = getCountryDisplayName(code);
    if (currentYear === 1991 && cd.independence) {
      labelHtml += '<span class="sub">Ind. ' + cd.independence + '</span>';
    }
    const icon = L.divIcon({
      className: 'country-label ' + (isCA ? 'country-label-ca' : 'country-label-neighbor'),
      html: labelHtml,
      iconSize: null
    });
    const marker = L.marker(cd.center, {icon, interactive:false}).addTo(map);
    countryLabels.push(marker);
  });
}
renderCountryLabels();

// ========== CITIES ==========
function getCityName(city) {
  if (currentYear === 1991 && city.name1991) return city.name1991;
  return city.name;
}

function tierMinZoom(tier) {
  if (tier === 'capital') return 0;
  if (tier === 1) return 5;
  if (tier === 2) return 6;
  if (tier === 3) return 7;
  if (tier === 4) return 8;
  return 9;
}

function renderCities() {
  cityMarkers.forEach(m => map.removeLayer(m));
  cityMarkers = [];
  const z = map.getZoom();

  CITIES.forEach(city => {
    if (z < tierMinZoom(city.tier)) return;
    const isCap = city.tier === 'capital';
    const displayName = getCityName(city);
    const icon = L.divIcon({
      className: 'city-marker',
      html: '<div class="city-dot'+(isCap?' capital':'')+'"></div><div class="city-name'+(isCap?' capital-name':'')+'">'+displayName+'</div>',
      iconSize: [80, 28],
      iconAnchor: [40, 6]
    });
    const marker = L.marker([city.lat, city.lng], {icon, interactive:false}).addTo(map);
    cityMarkers.push(marker);
  });
}
renderCities();
map.on('zoomend', renderCities);

// ========== TIMELINE ==========
const slider = document.getElementById('timeline-slider');
const yearEl = document.getElementById('timeline-year');
const eraEl = document.getElementById('timeline-era');
const tooltipEl = document.getElementById('timeline-tooltip');

const ACTIVE_YEARS = [1991, 2024];
const ERA_NAMES = {
  1991: 'Soviet Dissolution',
  2024: 'Modern Era'
};

function snapToNearest(val) {
  let closest = ACTIVE_YEARS[0];
  let minDist = Math.abs(val - closest);
  ACTIVE_YEARS.forEach(y => {
    const d = Math.abs(val - y);
    if (d < minDist) { minDist = d; closest = y; }
  });
  return closest;
}

slider.addEventListener('input', function() {
  const raw = parseInt(this.value);
  const snapped = snapToNearest(raw);
  const isActive = ACTIVE_YEARS.includes(raw);

  yearEl.textContent = raw;

  if (!isActive && raw !== snapped) {
    tooltipEl.classList.add('visible');
    tooltipEl.textContent = 'Coming soon \\u2014 snap to ' + snapped;
  } else {
    tooltipEl.classList.remove('visible');
  }
});

slider.addEventListener('change', function() {
  const raw = parseInt(this.value);
  const snapped = snapToNearest(raw);
  this.value = snapped;
  setYear(snapped);
});

function setYear(year) {
  currentYear = year;
  yearEl.textContent = year;
  eraEl.textContent = ERA_NAMES[year] || '';
  tooltipEl.classList.remove('visible');

  // Crossfade: animate opacity
  const mapPane = document.querySelector('.leaflet-overlay-pane');
  if (mapPane) {
    mapPane.style.transition = 'opacity 0.4s ease';
    mapPane.style.opacity = '0.3';
    setTimeout(() => {
      renderCountryLabels();
      renderCities();
      closeInfoPanel();
      mapPane.style.opacity = '1';
    }, 400);
  } else {
    renderCountryLabels();
    renderCities();
    closeInfoPanel();
  }
}

// ========== HOME BUTTON ==========
document.getElementById('home-btn').addEventListener('click', function() {
  map.flyTo(DEFAULT_CENTER, DEFAULT_ZOOM, {duration: 1});
  closeInfoPanel();
});
</script>
</body>
</html>'''

# Write the HTML file
with open(OUTPUT_PATH, 'w') as f:
    f.write(html)

import os
size = os.path.getsize(OUTPUT_PATH)
print(f"HTML written to {OUTPUT_PATH} ({size/1024:.1f} KB)")
