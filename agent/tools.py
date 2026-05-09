"""Tool implementations — each function queries Elasticsearch."""

import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

es = Elasticsearch(
    os.getenv("ES_URL"),
    api_key=os.getenv("ES_API_KEY"),
)

INDEX = "blr-rentals"


def search_listings(query: str) -> dict:
    """Semantic search over listing descriptions using ELSER."""
    resp = es.search(
        index=INDEX,
        size=5,
        query={
            "semantic": {
                "field": "description_semantic",
                "query": query,
            }
        },
        source_includes=[
            "listing_id",
            "locality",
            "micro_market",
            "bhk",
            "furnishing",
            "rent_inr",
            "deposit_inr",
            "deposit_months",
            "area_sqft",
            "description",
            "source_url",
            "publisher",
        ],
    )
    hits = [hit["_source"] for hit in resp["hits"]["hits"]]
    total = resp["hits"]["total"]
    if isinstance(total, dict):
        total_val = total.get("value", 0)
    else:
        total_val = total
    return {"listings": hits, "total": total_val}


def get_price_benchmark(locality: str, bhk: int) -> dict:
    """ES|QL query: rent stats for a locality + BHK."""
    query = f"""
        FROM blr-rentals
        | WHERE micro_market == "{locality}" AND bhk == {bhk}
        | STATS median_rent = MEDIAN(rent_inr),
                p25_rent = PERCENTILE(rent_inr, 25),
                p75_rent = PERCENTILE(rent_inr, 75),
                avg_deposit_months = AVG(deposit_months),
                listing_count = COUNT(*)
    """
    resp = es.esql.query(query=query, format="json")
    rows = resp.get("values", [])
    columns = [c["name"] for c in resp.get("columns", [])]
    if rows:
        return dict(zip(columns, rows[0]))
    return {"error": f"No listings found for {bhk}BHK in {locality}"}


def check_deposit_norm(locality: str, bhk: int) -> dict:
    """ES|QL query: deposit statistics for a locality + BHK."""
    query = f"""
        FROM blr-rentals
        | WHERE micro_market == "{locality}" AND bhk == {bhk}
        | STATS median_deposit = MEDIAN(deposit_months),
                avg_deposit = AVG(deposit_months),
                max_deposit = MAX(deposit_months),
                median_rent = MEDIAN(rent_inr),
                listing_count = COUNT(*)
    """
    resp = es.esql.query(query=query, format="json")
    rows = resp.get("values", [])
    columns = [c["name"] for c in resp.get("columns", [])]
    if rows:
        return dict(zip(columns, rows[0]))
    return {"error": f"No listings found for {bhk}BHK in {locality}"}


def compare_neighbourhoods(area_a: str, area_b: str) -> dict:
    """ES|QL query: side-by-side comparison of two areas."""
    query = f"""
        FROM blr-rentals
        | WHERE micro_market == "{area_a}" OR micro_market == "{area_b}"
        | STATS median_rent = MEDIAN(rent_inr),
                median_deposit = MEDIAN(deposit_months),
                avg_sqft = AVG(area_sqft),
                listing_count = COUNT(*)
          BY micro_market
    """
    resp = es.esql.query(query=query, format="json")
    rows = resp.get("values", [])
    columns = [c["name"] for c in resp.get("columns", [])]
    results = [dict(zip(columns, row)) for row in rows]
    return {"comparison": results}


TOOL_DISPATCH = {
    "search_listings": lambda args: search_listings(args["query"]),
    "get_price_benchmark": lambda args: get_price_benchmark(args["locality"], args["bhk"]),
    "check_deposit_norm": lambda args: check_deposit_norm(args["locality"], args["bhk"]),
    "compare_neighbourhoods": lambda args: compare_neighbourhoods(args["area_a"], args["area_b"]),
}
