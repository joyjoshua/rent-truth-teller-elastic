import csv
import hashlib
import json
import os
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = Path(os.getenv("BLR_RAW_CSV", str(ROOT / "data/raw/BangaloreHouseRentDtls.csv")))
OUTPUT_JSONL = ROOT / "data/processed/blr_rentals.jsonl"
COORDS_FILE = ROOT / "data/locality_coords.json"

SOURCE_URL = "https://www.kaggle.com/datasets/csunnikrishnan/bangalore-house-rent-details-1bhk-2bhk-3bhk"
PUBLISHER = "Kaggle (csunnikrishnan)"
LICENSE = "CC0 / Public Domain"

with COORDS_FILE.open(encoding="utf-8") as f:
    COORDS = json.load(f)

ZONE_MAP = {
    "Koramangala": "South Bengaluru",
    "HSR Layout": "South Bengaluru",
    "BTM Layout": "South Bengaluru",
    "JP Nagar": "South Bengaluru",
    "Jayanagar": "South Bengaluru",
    "Bannerghatta Road": "South Bengaluru",
    "Banashankari": "South Bengaluru",
    "Basavanagudi": "South Bengaluru",
    "Bommanahalli": "South Bengaluru",
    "Indiranagar": "East Bengaluru",
    "Whitefield": "East Bengaluru",
    "Marathahalli": "East Bengaluru",
    "KR Puram": "East Bengaluru",
    "Old Airport Road": "East Bengaluru",
    "Mahadevapura": "East Bengaluru",
    "Bellandur": "East Bengaluru",
    "Sarjapur": "East Bengaluru",
    "Electronic City": "South-East Bengaluru",
    "Hebbal": "North Bengaluru",
    "Yelahanka": "North Bengaluru",
    "Hennur": "North Bengaluru",
    "Thanisandra": "North Bengaluru",
    "RT Nagar": "North Bengaluru",
    "Rajajinagar": "West Bengaluru",
    "Malleshwaram": "West Bengaluru",
    "Vijayanagar": "West Bengaluru",
    "Nagarbhavi": "West Bengaluru",
    "Yeshwanthpur": "West Bengaluru",
    "Sadashivanagar": "Central Bengaluru",
    "Cunningham Road": "Central Bengaluru",
}

FURNISHING_OPTIONS = ["unfurnished", "semi-furnished", "fully-furnished"]
FURNISHING_WEIGHTS = [0.3, 0.5, 0.2]

_BHK_RE = re.compile(r"(\d+)\s*BHK", re.IGNORECASE)
_LAKH_RE = re.compile(r"([\d.]+)\s*[Ll]")


def parse_inr_price(raw: object) -> int | None:
    if raw is None:
        return None
    s = str(raw).strip().replace(",", "")
    low = s.lower()
    if low in ("", "nan", "none", "-"):
        return None
    m = _LAKH_RE.search(low)
    if m:
        try:
            return int(round(float(m.group(1)) * 100_000))
        except ValueError:
            return None
    try:
        return int(round(float(low)))
    except ValueError:
        return None


def parse_avg_rent(raw: object) -> float | None:
    if raw is None:
        return None
    s = str(raw).strip().replace(",", "")
    low = s.lower()
    if low in ("", "nan", "none", "-"):
        return None
    try:
        return float(low)
    except ValueError:
        return None


def infer_rent_inr(row: dict) -> tuple[int | None, str]:
    """
    Primary: AvgRent. Fallback: midpoint of MinPrice/MaxPrice, then single bound.
    Returns (rent_inr or None, provenance tag for stable hashing).
    """
    avg = parse_avg_rent(row.get("AvgRent"))
    if avg is not None and avg > 0:
        return int(round(avg)), "avg"

    min_p = parse_inr_price(row.get("MinPrice"))
    max_p = parse_inr_price(row.get("MaxPrice"))
    if min_p and max_p and min_p > 0 and max_p > 0:
        lo, hi = sorted((min_p, max_p))
        return int(round((lo + hi) / 2)), "mid_min_max"
    if min_p and min_p > 0:
        return min_p, "min_only"
    if max_p and max_p > 0:
        return max_p, "max_only"
    return None, "none"


def parse_bhk(house_type: str) -> int | None:
    if not house_type:
        return None
    m = _BHK_RE.search(house_type.strip())
    if not m:
        return None
    return int(m.group(1))


def find_micro_market(raw_locality: str) -> str:
    raw_lower = raw_locality.strip().lower()
    if "krishnarajapura" in raw_lower:
        return "KR Puram"
    raw_lower = raw_lower.replace("electronics city", "electronic city")
    for market in COORDS:
        if market.lower() in raw_lower:
            return market
    return raw_locality.strip().title()


def generate_deposit(rent: int) -> tuple[int, int]:
    if random.random() < 0.85:
        months = random.choice([2, 2, 2, 3, 3])
    else:
        months = random.choice([5, 6, 7, 8, 10])
    return rent * months, months


def random_date_last_90_days() -> str:
    days_ago = random.randint(0, 90)
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def generate_description(
    bhk: int,
    furnishing: str,
    micro_market: str,
    area_sqft: int | None,
    locality_label: str,
    band_sentence: str,
) -> str:
    adjectives = ["Spacious", "Well-maintained", "Bright", "Airy", "Cozy", "Modern"]
    features = [
        "with parking",
        "near metro",
        "gated community",
        "with power backup",
        "close to schools",
        "near IT parks",
        "with garden view",
        "in a quiet lane",
        "near shopping mall",
    ]
    adj = random.choice(adjectives)
    feat = random.choice(features)
    area_str = f"{area_sqft} sqft " if area_sqft else ""
    core = (
        f"{adj} {bhk}BHK {furnishing} rental segment {area_str}in {micro_market} ({locality_label}) {feat}. "
        f"Derived from area-level rent aggregates in public Bengaluru rental data."
    )
    if band_sentence:
        core = core + " " + band_sentence
    return core


def price_band_sentence(min_p: int | None, max_p: int | None) -> str:
    if min_p and max_p and min_p > 0 and max_p > 0:
        lo, hi = (min_p, max_p) if min_p <= max_p else (max_p, min_p)
        return f"Observed asking range in source rows roughly ₹{lo:,}–₹{hi:,}."
    if min_p and min_p > 0:
        return f"Minimum band around ₹{min_p:,}."
    if max_p and max_p > 0:
        return f"Upper band around ₹{max_p:,}."
    return ""


def main() -> None:
    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    if not INPUT_CSV.is_file():
        raise SystemExit(f"Missing input CSV: {INPUT_CSV}")

    with INPUT_CSV.open("r", encoding="utf-8") as infile, OUTPUT_JSONL.open(
        "w", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        for row in reader:
            raw_locality = (row.get("Locality") or row.get("locality") or "").strip()
            house_type = row.get("HouseType") or row.get("house_type") or ""
            bhk = parse_bhk(house_type)
            rent, rent_src = infer_rent_inr(row)
            if bhk is None or rent is None:
                continue

            min_p = parse_inr_price(row.get("MinPrice"))
            max_p = parse_inr_price(row.get("MaxPrice"))

            micro_market = find_micro_market(raw_locality)
            furnishing = random.choices(FURNISHING_OPTIONS, FURNISHING_WEIGHTS)[0]
            deposit, dep_months = generate_deposit(rent)
            coords = COORDS.get(micro_market, {})
            zone = ZONE_MAP.get(micro_market, "Bengaluru")

            lat = coords.get("lat", 12.97) + random.uniform(-0.005, 0.005)
            lon = coords.get("lon", 77.59) + random.uniform(-0.005, 0.005)

            band_sentence = price_band_sentence(min_p, max_p)
            doc_id = hashlib.sha256(
                f"{SOURCE_URL}:{raw_locality}:{house_type}:{rent}:{rent_src}:{min_p}:{max_p}".encode()
            ).hexdigest()[:16]

            doc = {
                "listing_id": f"KG-BLR-{count:05d}",
                "locality": raw_locality,
                "micro_market": micro_market,
                "zone": zone,
                "bhk": bhk,
                "furnishing": furnishing,
                "rent_inr": rent,
                "deposit_inr": int(deposit),
                "deposit_months": round(dep_months, 2),
                "area_sqft": None,
                "rent_per_sqft": None,
                "listed_date": random_date_last_90_days(),
                "description": generate_description(
                    bhk,
                    furnishing,
                    micro_market,
                    None,
                    raw_locality,
                    band_sentence,
                ),
                "location": {"lat": round(lat, 6), "lon": round(lon, 6)},
                "source_url": SOURCE_URL,
                "publisher": PUBLISHER,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "license": LICENSE,
                "doc_id": doc_id,
            }
            outfile.write(json.dumps(doc) + "\n")
            count += 1

    print(f"Wrote {count} enriched listings to {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()
