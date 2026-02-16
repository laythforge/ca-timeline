#!/usr/bin/env python3
"""
STEP 1: Generate geodata.json with simplified country boundaries.
- CA countries: simplify tolerance=0.02
- Neighbor countries: simplify tolerance=0.1, clipped to box(44,30,90,56)
"""
import json
import os
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
from shapely.validation import make_valid

ROOT_DIR = os.path.dirname(__file__)
COUNTRIES_DIR = os.path.join(ROOT_DIR, "node_modules", "world-geojson", "countries")
OUTPUT_PATH = os.path.join(ROOT_DIR, "geodata.json")

CA_COUNTRIES = {
    "kazakhstan": "KZ",
    "uzbekistan": "UZ",
    "turkmenistan": "TM",
    "kyrgyzstan": "KG",
    "tajikistan": "TJ",
}

NEIGHBOR_COUNTRIES = {
    "russia": "RU",
    "china": "CN",
    "iran": "IR",
    "afghanistan": "AF",
    "pakistan": "PK",
    "mongolia": "MN",
    "azerbaijan": "AZ",
    "georgia": "GE",
}

CLIP_BOX = box(44, 30, 90, 56)  # (minx, miny, maxx, maxy) = (lon_min, lat_min, lon_max, lat_max)


def load_country(name):
    """Load GeoJSON FeatureCollection and merge all features into one geometry."""
    path = os.path.join(COUNTRIES_DIR, f"{name}.json")
    with open(path) as f:
        data = json.load(f)

    if data["type"] == "FeatureCollection":
        geoms = [make_valid(shape(feat["geometry"])) for feat in data["features"]]
        merged = unary_union(geoms)
    else:
        merged = make_valid(shape(data["geometry"]))

    return make_valid(merged)


def process_country(name, code, is_ca):
    """Process a single country: simplify and optionally clip."""
    geom = load_country(name)

    if is_ca:
        simplified = geom.simplify(0.02, preserve_topology=True)
    else:
        simplified = geom.simplify(0.1, preserve_topology=True)
        clipped = simplified.intersection(CLIP_BOX)
        if clipped.is_empty:
            print(f"  WARNING: {name} is empty after clipping!")
            return None
        simplified = clipped

    feature = {
        "type": "Feature",
        "properties": {
            "name": name.capitalize() if name != "kyrgyzstan" else "Kyrgyzstan",
            "code": code,
            "isCA": is_ca,
        },
        "geometry": mapping(simplified),
    }
    return feature


def main():
    features = []

    # Process CA countries
    print("Processing Central Asian countries (tolerance=0.02)...")
    for name, code in CA_COUNTRIES.items():
        print(f"  {name}")
        feat = process_country(name, code, is_ca=True)
        if feat:
            # Fix capitalization for multi-word names
            feat["properties"]["name"] = name.replace("_", " ").title()
            features.append(feat)

    # Process neighbor countries
    print("Processing neighbor countries (tolerance=0.1, clipped)...")
    for name, code in NEIGHBOR_COUNTRIES.items():
        print(f"  {name}")
        feat = process_country(name, code, is_ca=False)
        if feat:
            feat["properties"]["name"] = name.replace("_", " ").title()
            features.append(feat)

    geodata = {
        "type": "FeatureCollection",
        "features": features,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(geodata, f)

    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"\nDone! Saved {len(features)} countries to {OUTPUT_PATH}")
    print(f"File size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
