# Data provenance

| Artifact | Source | Notes |
|----------|--------|-------|
| `raw/BangaloreHouseRentDtls.csv` | [Bangalore House Rent Details](https://www.kaggle.com/datasets/csunnikrishnan/bangalore-house-rent-details-1bhk-2bhk-3bhk) (Kaggle) | Area × BHK aggregates (`AvgRent`, min/max bands); not committed |
| `locality_coords.json` | Synthetic centroid lookup | Expand rows as needed for CSV coverage |
| `processed/blr_rentals.jsonl` | Generated | Run `python ingest/normalize_and_enrich.py` |

License reference for dataset: CC0 / Public Domain per dataset page (verify before redistribution).
