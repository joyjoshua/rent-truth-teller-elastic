"""Median rent by micro_market: map + chart for Streamlit."""

from __future__ import annotations

import json
import os
from html import escape
from pathlib import Path

import folium
import pandas as pd
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[1]


def _es_client() -> Elasticsearch | None:
    load_dotenv(ROOT / ".env")
    url = os.getenv("ES_URL")
    key = os.getenv("ES_API_KEY")
    if not url or not key:
        return None
    return Elasticsearch(url, api_key=key)


def _baseline_index() -> str:
    return (os.getenv("ES_INDEX_BASELINE") or "blr-rentals").strip()


def load_coords() -> dict[str, dict]:
    path = ROOT / "data" / "locality_coords.json"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fetch_median_by_micro_market(client: Elasticsearch, index: str) -> pd.DataFrame:
    query = f"""
        FROM {index}
        | LIMIT 100000
        | STATS median_rent = MEDIAN(rent_inr),
                listing_count = COUNT(*)
          BY micro_market
        | SORT median_rent DESC
    """
    resp = client.esql.query(query=query, format="json")
    rows = resp.get("values") or []
    cols = [c["name"] for c in resp.get("columns", [])]
    if not rows:
        return pd.DataFrame(columns=["micro_market", "median_rent", "listing_count"])
    return pd.DataFrame([dict(zip(cols, r)) for r in rows])


def assign_rent_tiers(median_rents: pd.Series) -> pd.Series:
    """Low / Mid / High tertiles for coloring."""
    valid = median_rents.dropna()
    if valid.empty:
        return pd.Series(dtype=str)
    if len(valid.unique()) < 2:
        return pd.Series(["Mid rent"] * len(median_rents), index=median_rents.index)
    q1 = valid.quantile(1 / 3)
    q2 = valid.quantile(2 / 3)

    def tier(v: object) -> str:
        fv = float(v)
        if fv <= q1:
            return "Lower rent"
        if fv <= q2:
            return "Mid rent"
        return "Higher rent"

    return median_rents.apply(tier)


TIER_STYLE = {
    "Lower rent": {"color": "#1e8449", "fill": "#27ae60"},
    "Mid rent": {"color": "#b7950b", "fill": "#f4d03f"},
    "Higher rent": {"color": "#922b21", "fill": "#e74c3c"},
}


def build_folium_map(df: pd.DataFrame) -> folium.Map:
    center_lat, center_lon = 12.9716, 77.5946
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="CartoDB positron")

    for _, row in df.iterrows():
        tier = row["tier"]
        style = TIER_STYLE.get(tier, TIER_STYLE["Mid rent"])
        rent = row["median_rent"]
        cnt = int(row["listing_count"])
        label = escape(str(row["micro_market"]))
        radius = max(6, min(28, 8 + cnt**0.5 * 2))

        tip = (
            f"<div style='font-size:13px'><b>{label}</b><br/>"
            f"Median rent: ₹{rent:,.0f}/mo<br/>"
            f"Listings (aggregate rows): {cnt}<br/>"
            f"<span style='color:#555'>{tier}</span></div>"
        )

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=radius,
            color=style["color"],
            weight=2,
            fill=True,
            fill_color=style["fill"],
            fill_opacity=0.72,
            tooltip=folium.Tooltip(tip, sticky=True),
        ).add_to(m)

    return m


def _render_rent_explorer_body(st_module) -> None:
    """Core map + charts (no wrapper)."""
    st = st_module
    st.caption(
        "Markers use **approximate locality centers** from `data/locality_coords.json`. "
        "Median rent comes from your **baseline Elasticsearch index** (aggregated rows)."
    )

    client = _es_client()
    if client is None:
        st.warning("Set `ES_URL` and `ES_API_KEY` in `.env` to load the map.")
        return

    idx = _baseline_index()
    try:
        df = fetch_median_by_micro_market(client, idx)
    except Exception as e:
        st.error(f"Could not query Elasticsearch: {e}")
        return

    if df.empty:
        st.info("No aggregate rows returned from ES|QL — index empty or field mismatch.")
        return

    coords = load_coords()
    rows = []
    for _, r in df.iterrows():
        mm = str(r["micro_market"])
        c = coords.get(mm)
        if not c:
            continue
        rows.append(
            {
                "micro_market": mm,
                "median_rent": float(r["median_rent"]),
                "listing_count": int(r["listing_count"]),
                "lat": float(c["lat"]),
                "lon": float(c["lon"]),
            }
        )

    merged = pd.DataFrame(rows)
    if merged.empty:
        st.warning(
            "No micro_markets matched coordinates in `locality_coords.json`. "
            "Expand that file or align names with `micro_market` in Elasticsearch."
        )
        chart_df = df.head(40).set_index("micro_market")[["median_rent"]]
        st.bar_chart(chart_df)
        return

    merged["tier"] = assign_rent_tiers(merged["median_rent"])

    col_map, col_legend = st.columns([3, 1])
    with col_map:
        st.markdown(
            "**Map** — greener ≈ lower median rent, redder ≈ higher (within this dataset). Hover tooltips show detail."
        )
        fmap = build_folium_map(merged)
        st_folium(fmap, width=None, height=420, returned_objects=[])

    with col_legend:
        st.markdown("**Legend**")
        for tier, spec in TIER_STYLE.items():
            st.markdown(
                f"<span style='display:inline-block;width:14px;height:14px;"
                f"background:{spec['fill']};border:2px solid {spec['color']};"
                f"border-radius:50%;vertical-align:middle;margin-right:6px'></span> {tier}",
                unsafe_allow_html=True,
            )

    st.markdown("**Top 15 areas by median rent**")
    top = merged.nlargest(15, "median_rent")[["micro_market", "median_rent"]].set_index(
        "micro_market"
    )
    st.bar_chart(top)

    st.markdown("**Table — matched areas**")
    show = merged.sort_values("median_rent", ascending=False)[
        ["micro_market", "median_rent", "listing_count", "tier"]
    ]
    st.dataframe(show, use_container_width=True, hide_index=True)


def render_rent_explorer(st_module, *, standalone: bool = False) -> None:
    """
    Map + charts. Use standalone=True when shown as its own screen (no expander).
    """
    st = st_module
    if standalone:
        st.subheader("🗺️ Bengaluru median rent — map & charts")
        _render_rent_explorer_body(st)
        return

    with st.expander("Bengaluru median rent by area — map & chart", expanded=False):
        _render_rent_explorer_body(st)
