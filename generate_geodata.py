#!/usr/bin/env python3
"""
STEP 1: Generate geodata.json with modern borders, neighbor borders,
and historical approximate polygons for 1900, 1920, 1924 eras.
"""
import json
import os
from shapely.geometry import shape, box, mapping, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import make_valid

COUNTRIES_DIR = "/home/user/ca-timeline/node_modules/world-geojson/countries"
OUTPUT_PATH = "/home/user/geodata.json"

CA_COUNTRIES = ["kazakhstan", "uzbekistan", "turkmenistan", "kyrgyzstan", "tajikistan"]
CA_CODES = {"kazakhstan": "KZ", "uzbekistan": "UZ", "turkmenistan": "TM",
            "kyrgyzstan": "KG", "tajikistan": "TJ"}

NEIGHBOR_COUNTRIES = {"russia": "RU", "china": "CN", "iran": "IR",
                      "afghanistan": "AF", "pakistan": "PK", "mongolia": "MN",
                      "azerbaijan": "AZ", "georgia": "GE"}

CLIP_BOX = box(44, 28, 92, 57)


def load_country(name):
    path = os.path.join(COUNTRIES_DIR, f"{name}.json")
    with open(path) as f:
        data = json.load(f)
    if data["type"] == "FeatureCollection":
        geoms = [make_valid(shape(feat["geometry"])) for feat in data["features"]]
        merged = unary_union(geoms)
    else:
        merged = make_valid(shape(data["geometry"]))
    return make_valid(merged)


def simplify_and_map(geom, tolerance):
    s = geom.simplify(tolerance, preserve_topology=True)
    s = make_valid(s)
    return mapping(s)


def main():
    # Load all modern CA borders
    print("Loading modern borders...")
    modern = {}
    for name in CA_COUNTRIES:
        code = CA_CODES[name]
        geom = load_country(name)
        modern[code] = geom
        print(f"  {code}: loaded")

    # Process modern CA borders (tolerance=0.015)
    modern_geo = {}
    for code, geom in modern.items():
        modern_geo[code] = simplify_and_map(geom, 0.015)
        print(f"  {code}: simplified")

    # Process neighbors
    print("Loading and processing neighbors...")
    neighbors_geo = {}
    large_neighbors = {"russia", "china"}
    for name, code in NEIGHBOR_COUNTRIES.items():
        geom = load_country(name)
        tol = 0.08 if name in large_neighbors else 0.04
        simplified = geom.simplify(tol, preserve_topology=True)
        clipped = make_valid(simplified).intersection(CLIP_BOX)
        if clipped.is_empty:
            print(f"  WARNING: {name} empty after clip!")
            continue
        neighbors_geo[code] = mapping(make_valid(clipped))
        print(f"  {code}: done (tol={tol})")

    # =============================================
    # HISTORICAL POLYGONS
    # =============================================
    print("Generating historical polygons...")

    KZ = modern["KZ"]
    UZ = modern["UZ"]
    TM = modern["TM"]
    KG = modern["KG"]
    TJ = modern["TJ"]

    all_ca = make_valid(unary_union([KZ, UZ, TM, KG, TJ]))

    # --- 1900: Russian Imperial Era ---
    print("  1900: Russian Imperial Era...")

    # Emirate of Bukhara: southern UZ + most of TJ (except Khujand area)
    # Bukhara controlled: Bukhara, Karshi, Shahrisabz, Guzar, Denau, Hisar,
    # Kulyab, Karategin, Darvaz (most of modern TJ south of Khujand)
    # Northern boundary ~40.2N in UZ (below Samarkand which was Russian),
    # but extends through all of TJ except the very north
    bukhara_uz_box = box(63, 36.5, 70, 40.3)
    bukhara_uz_part = make_valid(UZ.intersection(bukhara_uz_box))

    # Tajikistan part: everything except the Khujand (Sughd) northern strip
    tj_north_box = box(68, 40.0, 72, 41.5)
    tj_north = make_valid(TJ.intersection(tj_north_box))
    bukhara_tj_part = make_valid(TJ.difference(tj_north_box))

    bukhara_emirate = make_valid(unary_union([bukhara_uz_part, bukhara_tj_part]))
    # Clean up any slivers
    if bukhara_emirate.area < 0.01:
        print("    WARNING: Bukhara emirate very small, adjusting...")
        bukhara_uz_box = box(62, 36, 71, 40.5)
        bukhara_uz_part = make_valid(UZ.intersection(bukhara_uz_box))
        bukhara_tj_part = make_valid(TJ.difference(box(68, 40.2, 72, 42)))
        bukhara_emirate = make_valid(unary_union([bukhara_uz_part, bukhara_tj_part]))

    print(f"    Bukhara emirate area: {bukhara_emirate.area:.2f}")

    # Khanate of Khiva: NW Uzbekistan (Karakalpakstan + Khorezm) + strip of N Turkmenistan
    khiva_box = box(55.5, 40.0, 62.5, 44.5)
    khiva_uz = make_valid(UZ.intersection(khiva_box))
    khiva_tm_box = box(56, 40, 62, 42.5)
    khiva_tm = make_valid(TM.intersection(khiva_tm_box))
    khiva_khanate = make_valid(unary_union([khiva_uz, khiva_tm]))
    print(f"    Khiva khanate area: {khiva_khanate.area:.2f}")

    # Semirechye (SE Kazakhstan) — part of Russian Turkestan
    semirechye_box = box(67, 40, 81, 46)
    semirechye = make_valid(KZ.intersection(semirechye_box))
    print(f"    Semirechye area: {semirechye.area:.2f}")

    # Russian Turkestan: KG + (TM minus Khiva area) + (UZ minus Bukhara minus Khiva)
    #   + N Tajikistan (Khujand) + Semirechye
    tm_minus_khiva = make_valid(TM.difference(khiva_khanate))
    uz_minus_bukhara_khiva = make_valid(UZ.difference(bukhara_emirate).difference(khiva_khanate))

    russian_turkestan = make_valid(unary_union([
        KG, tm_minus_khiva, uz_minus_bukhara_khiva, tj_north, semirechye
    ]))
    print(f"    Russian Turkestan area: {russian_turkestan.area:.2f}")

    # Kazakh Steppe: Kazakhstan minus Semirechye
    kazakh_steppe = make_valid(KZ.difference(semirechye))
    print(f"    Kazakh Steppe area: {kazakh_steppe.area:.2f}")

    # Verify coverage: all 4 entities should roughly cover all_ca
    hist_1900_union = make_valid(unary_union([
        russian_turkestan, bukhara_emirate, khiva_khanate, kazakh_steppe
    ]))
    coverage = hist_1900_union.area / all_ca.area * 100
    print(f"    1900 coverage: {coverage:.1f}% of total CA area")

    historical = {}

    # 1900
    historical["1900"] = {
        "TURKESTAN": {
            "geometry": simplify_and_map(russian_turkestan, 0.025),
            "color": "#8B4513",
            "name": "Russian Turkestan",
            "subtitle": "Governor-Generalship, est. 1867"
        },
        "BUKHARA": {
            "geometry": simplify_and_map(bukhara_emirate, 0.025),
            "color": "#DAA520",
            "name": "Emirate of Bukhara",
            "subtitle": "Russian Protectorate since 1868"
        },
        "KHIVA": {
            "geometry": simplify_and_map(khiva_khanate, 0.025),
            "color": "#4682B4",
            "name": "Khanate of Khiva",
            "subtitle": "Russian Protectorate since 1873"
        },
        "STEPPE": {
            "geometry": simplify_and_map(kazakh_steppe, 0.025),
            "color": "#CD853F",
            "name": "Kazakh Steppe",
            "subtitle": "Russian Empire \u2014 Steppe regions"
        }
    }

    # 1920: Same polygons, different names/colors
    print("  1920: Soviet Takeover...")
    historical["1920"] = {
        "TURKESTAN_ASSR": {
            "geometry": simplify_and_map(russian_turkestan, 0.025),
            "color": "#C0392B",
            "name": "Turkestan ASSR",
            "subtitle": "Autonomous SSR within RSFSR, est. 1918"
        },
        "BUKHARA_PSR": {
            "geometry": simplify_and_map(bukhara_emirate, 0.025),
            "color": "#E74C3C",
            "name": "Bukharan PSR",
            "subtitle": "People's Soviet Republic, est. 1920"
        },
        "KHOREZM_PSR": {
            "geometry": simplify_and_map(khiva_khanate, 0.025),
            "color": "#F39C12",
            "name": "Khorezm PSR",
            "subtitle": "People's Soviet Republic, est. 1920"
        },
        "KIRGHIZ_ASSR": {
            "geometry": simplify_and_map(kazakh_steppe, 0.025),
            "color": "#E67E22",
            "name": "Kirghiz ASSR",
            "subtitle": "Later renamed Kazakh ASSR, est. 1920"
        }
    }

    # 1924: National Delimitation
    print("  1924: National Delimitation...")
    # Uzbek SSR = modern UZ + modern TJ combined
    uzbek_ssr_1924 = make_valid(unary_union([UZ, TJ]))
    # Turkmen SSR = modern TM
    turkmen_ssr_1924 = TM
    # Kara-Kirghiz AO = modern KG
    kara_kirghiz_1924 = KG
    # Kazakh ASSR = modern KZ (+ Karakalpakstan was initially here but approximation)
    kazakh_assr_1924 = KZ

    historical["1924"] = {
        "UZ_SSR": {
            "geometry": simplify_and_map(uzbek_ssr_1924, 0.015),
            "color": "#81B29A",
            "name": "Uzbek SSR",
            "subtitle": "Est. Oct 27, 1924 \u00b7 Includes Tajik ASSR"
        },
        "TM_SSR": {
            "geometry": simplify_and_map(turkmen_ssr_1924, 0.015),
            "color": "#F2CC8F",
            "name": "Turkmen SSR",
            "subtitle": "Est. Oct 27, 1924"
        },
        "KARA_KIRGHIZ": {
            "geometry": simplify_and_map(kara_kirghiz_1924, 0.015),
            "color": "#3D85C6",
            "name": "Kara-Kirghiz AO",
            "subtitle": "Autonomous Oblast within RSFSR"
        },
        "KZ_ASSR": {
            "geometry": simplify_and_map(kazakh_assr_1924, 0.015),
            "color": "#E07A5F",
            "name": "Kazakh ASSR",
            "subtitle": "Autonomous SSR within RSFSR"
        }
    }

    # 1936, 1991, 2024 use modern borders — stored as modern_geo already

    # Build output
    output = {
        "modern": modern_geo,
        "neighbors": neighbors_geo,
        "historical": historical
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f)

    fsize = os.path.getsize(OUTPUT_PATH)
    print(f"\nSaved to {OUTPUT_PATH} ({fsize/1024:.1f} KB)")
    print(f"  Modern: {len(modern_geo)} countries")
    print(f"  Neighbors: {len(neighbors_geo)} countries")
    print(f"  Historical periods: {list(historical.keys())}")
    for period, entities in historical.items():
        print(f"    {period}: {list(entities.keys())}")


if __name__ == "__main__":
    main()
