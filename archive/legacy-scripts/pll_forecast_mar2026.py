#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Forecast daily sales by BRANCHID x Category for March 2026.

Input (hardcoded):  /Users/anhtrinh/Downloads/06 dev/pll-pe/pll-raw-sales.xlsx
Output (hardcoded): /Users/anhtrinh/Downloads/06 dev/pll-pe/pll_fc_0326.csv

Dependencies: pandas, numpy, openpyxl

Modeling notes (robust + rule-based):
- Closing rule: if combo had no sales in Feb-2026 => forecast 0 for Mar-2026.
- Opening / renovation boost handling:
  * detect opening month (first non-zero month)
  * detect renovation-like spikes (robust z-score on monthly sales)
  * normalize boosted months while computing YoY trend
- L3M YoY trend guides level (softly compressed, no hard cap).
- Weekend/weekday effect from recent behavior.
- Holiday effects for requested holiday groups.
- Seasonality index (month-of-year), with mild prior favoring summer > winter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd


# =========================
# Hardcoded paths
# =========================
INPUT_XLSX = "/Users/anhtrinh/Downloads/06 dev/pll-pe/pll-raw-sales.xlsx"
OUTPUT_CSV = "/Users/anhtrinh/Downloads/06 dev/pll-pe/pll_fc_0326.csv"

TRAIN_END = pd.Timestamp("2026-02-28")
FC_START = pd.Timestamp("2026-03-01")
FC_END = pd.Timestamp("2026-03-31")


# =========================
# Holiday calendar (2023-2026)
# - Tet dates from timeanddate.com holiday pages
# - Trung Thu dates from web sources for Mid-Autumn (15th day lunar month 8)
# =========================
TET_DAY = {
    2023: pd.Timestamp("2023-01-22"),
    2024: pd.Timestamp("2024-02-10"),
    2025: pd.Timestamp("2025-01-29"),
    2026: pd.Timestamp("2026-02-17"),
}

TRUNG_THU_DAY = {
    2023: pd.Timestamp("2023-09-29"),
    2024: pd.Timestamp("2024-09-17"),
    2025: pd.Timestamp("2025-10-06"),
    2026: pd.Timestamp("2026-09-25"),
}


# =========================
# Utilities
# =========================
def to_month_start(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s).dt.to_period("M").dt.to_timestamp()


def robust_median(x: pd.Series, default: float = 1.0) -> float:
    x = pd.to_numeric(x, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if len(x) == 0:
        return default
    return float(np.median(x.values))


def mad(arr: np.ndarray) -> float:
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return np.nan
    med = np.median(arr)
    return float(np.median(np.abs(arr - med)))


def soft_compress_ratio(r: float) -> float:
    """Softly compress extreme ratios without hard clipping."""
    r = max(r, 1e-6)
    return float(np.exp(np.tanh(np.log(r))))


def shrink(value: float, anchor: float, n: int, k: float = 8.0) -> float:
    """Empirical-Bayes style shrinkage to anchor when sample size is small."""
    w = n / (n + k)
    return float(w * value + (1.0 - w) * anchor)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapper = {c.lower().strip(): c for c in df.columns}

    def pick(*names: str) -> str:
        for n in names:
            if n.lower() in mapper:
                return mapper[n.lower()]
        raise KeyError(f"Missing expected column among: {names}")

    out = pd.DataFrame()
    out["BRANCHID"] = df[pick("BRANCHID", "BranchID", "branchid")]
    out["Category"] = df[pick("Category", "category")]
    out["Date"] = df[pick("Date", "date")]
    out["Actual_DT"] = df[pick("Actual_DT", "actual_dt", "DT", "Sales")]
    out["Actual_GD"] = df[pick("Actual_GD", "actual_gd", "GD", "Transactions")]
    return out


def holiday_flags(dates: pd.Series) -> pd.DataFrame:
    d = pd.to_datetime(dates)
    out = pd.DataFrame(index=np.arange(len(d)))

    # Tet pre-period D-7..D-1 before Tet day each year
    tet_pre = pd.Series(False, index=d.index)
    for y, tet in TET_DAY.items():
        start = tet - pd.Timedelta(days=7)
        end = tet - pd.Timedelta(days=1)
        tet_pre = tet_pre | ((d >= start) & (d <= end))
    out["is_tet_pre"] = tet_pre.values

    # Fixed-date holidays
    out["is_304_15"] = ((d.dt.month == 4) & (d.dt.day == 30)) | ((d.dt.month == 5) & (d.dt.day == 1))
    out["is_children_16"] = (d.dt.month == 6) & (d.dt.day == 1)
    out["is_christmas"] = (d.dt.month == 12) & (d.dt.day == 25)
    out["is_new_year"] = (d.dt.month == 1) & (d.dt.day == 1)

    # Trung Thu by year-specific Gregorian date
    trung_thu_dates = pd.to_datetime(list(TRUNG_THU_DAY.values()))
    out["is_trung_thu"] = d.isin(trung_thu_dates).values

    return out


def build_holiday_label(flag_row: pd.Series) -> str:
    for k in ["is_tet_pre", "is_304_15", "is_children_16", "is_trung_thu", "is_christmas", "is_new_year"]:
        if bool(flag_row.get(k, False)):
            return k
    return "none"


def detect_renovation_events(monthly: pd.DataFrame) -> pd.DataFrame:
    """
    Detect renovation-like outliers on monthly sales by combo via robust z-score
    against prior history. Returns monthly with columns:
    [BRANCHID, Category, month, is_opening_month, is_renovation_event, is_boost_window]
    """
    m = monthly.sort_values(["BRANCHID", "Category", "month"]).copy()
    m["is_opening_month"] = False
    m["is_renovation_event"] = False

    out_parts = []
    for (b, c), g in m.groupby(["BRANCHID", "Category"], sort=False):
        g = g.copy().reset_index(drop=True)

        # Opening month = first month with positive sales
        pos_idx = np.where(g["monthly_dt"].values > 0)[0]
        if len(pos_idx) > 0:
            g.loc[pos_idx[0], "is_opening_month"] = True

        # Renovation-like spike detection
        vals = g["monthly_dt"].values.astype(float)
        reno_flags = np.zeros(len(g), dtype=bool)
        for i in range(len(g)):
            hist = vals[:i]
            hist = hist[np.isfinite(hist)]
            hist = hist[hist > 0]
            if hist.size < 6:
                continue

            med = np.median(hist)
            mdev = mad(hist)
            scale = 1.4826 * mdev if (mdev and np.isfinite(mdev) and mdev > 0) else np.std(hist)
            if not np.isfinite(scale) or scale <= 1e-9:
                continue

            z = (vals[i] - med) / scale
            ratio = vals[i] / max(med, 1.0)

            # Transient spike preference: month i much higher than neighbor median
            neigh = []
            if i - 1 >= 0:
                neigh.append(vals[i - 1])
            if i + 1 < len(g):
                neigh.append(vals[i + 1])
            neigh_med = np.median([x for x in neigh if np.isfinite(x)]) if neigh else med
            trans_ratio = vals[i] / max(neigh_med, 1.0)

            if (z >= 3.5 and ratio >= 1.8 and trans_ratio >= 1.4):
                reno_flags[i] = True

        g["is_renovation_event"] = reno_flags

        # Boost window for normalization: event month + next 2 months
        g["is_boost_window"] = False
        event_idx = np.where((g["is_opening_month"] | g["is_renovation_event"]).values)[0]
        for ei in event_idx:
            g.loc[(g.index >= ei) & (g.index <= ei + 2), "is_boost_window"] = True

        out_parts.append(g)

    return pd.concat(out_parts, ignore_index=True)


def build_combo_features(hist: pd.DataFrame):
    """
    Build robust combo-level features:
    - month-level table with boost flags
    - L3M YoY (normalized)
    - DOW factors
    - seasonality factors
    """

    # Monthly aggregation
    m = (
        hist.groupby(["BRANCHID", "Category", pd.Grouper(key="Date", freq="MS")], as_index=False)
        .agg(monthly_dt=("Actual_DT", "sum"), monthly_gd=("Actual_GD", "sum"))
        .rename(columns={"Date": "month"})
    )

    # Ensure complete monthly grid for stability
    combos = hist[["BRANCHID", "Category"]].drop_duplicates()
    month_range = pd.date_range(hist["Date"].min().to_period("M").to_timestamp(), TRAIN_END.to_period("M").to_timestamp(), freq="MS")
    full_m = combos.assign(key=1).merge(pd.DataFrame({"month": month_range, "key": 1}), on="key", how="outer").drop(columns=["key"])
    m = full_m.merge(m, on=["BRANCHID", "Category", "month"], how="left")
    m[["monthly_dt", "monthly_gd"]] = m[["monthly_dt", "monthly_gd"]].fillna(0.0)

    m = detect_renovation_events(m)

    # Normalize boost months for YoY trend extraction
    # mild dampening, not removal
    m["norm_factor"] = 1.0 + 0.60 * m["is_boost_window"].astype(float)
    m["monthly_dt_norm"] = m["monthly_dt"] / m["norm_factor"]

    # YoY monthly ratio
    m_prev = m[["BRANCHID", "Category", "month", "monthly_dt_norm"]].copy()
    m_prev["month"] = m_prev["month"] + pd.DateOffset(years=1)
    m = m.merge(
        m_prev.rename(columns={"monthly_dt_norm": "monthly_dt_norm_ly"}),
        on=["BRANCHID", "Category", "month"],
        how="left",
    )
    m["yoy_raw"] = np.where(m["monthly_dt_norm_ly"] > 0, m["monthly_dt_norm"] / m["monthly_dt_norm_ly"], np.nan)

    # L3M YoY at combo level (for forecast month context, use Dec/Jan/Feb up to 2026-02)
    ref_months = pd.to_datetime(["2025-12-01", "2026-01-01", "2026-02-01"])
    l3m = m[m["month"].isin(ref_months)].copy()

    # Category/global anchors
    cat_anchor = (
        l3m.groupby("Category", as_index=False)["yoy_raw"]
        .agg(lambda x: robust_median(pd.Series(x), default=1.0))
        .rename(columns={"yoy_raw": "cat_yoy_anchor"})
    )
    global_anchor = robust_median(l3m["yoy_raw"], default=1.0)

    combo_yoy = (
        l3m.groupby(["BRANCHID", "Category"])["yoy_raw"]
        .agg(
            combo_yoy_raw=lambda x: robust_median(pd.Series(x), default=np.nan),
            n=lambda x: int(pd.Series(x).notna().sum()),
        )
        .reset_index()
    )

    combo_yoy = combo_yoy.merge(cat_anchor, on="Category", how="left")
    combo_yoy["cat_yoy_anchor"] = combo_yoy["cat_yoy_anchor"].fillna(global_anchor)
    combo_yoy["combo_yoy_raw"] = combo_yoy["combo_yoy_raw"].fillna(combo_yoy["cat_yoy_anchor"])

    combo_yoy["yoy_shrunk"] = [
        shrink(v, a, n=n, k=8.0)
        for v, a, n in zip(combo_yoy["combo_yoy_raw"], combo_yoy["cat_yoy_anchor"], combo_yoy["n"])
    ]
    combo_yoy["trend_factor"] = combo_yoy["yoy_shrunk"].apply(soft_compress_ratio)

    # DOW factor: robust ratio to overall mean over recent 180 days
    recent_start = TRAIN_END - pd.Timedelta(days=179)
    d_recent = hist[(hist["Date"] >= recent_start) & (hist["Date"] <= TRAIN_END)].copy()
    d_recent["dow"] = d_recent["Date"].dt.weekday

    overall = (
        d_recent.groupby(["BRANCHID", "Category"], as_index=False)["Actual_DT"]
        .mean()
        .rename(columns={"Actual_DT": "mean_dt"})
    )

    dow = (
        d_recent.groupby(["BRANCHID", "Category", "dow"], as_index=False)["Actual_DT"]
        .median()
        .rename(columns={"Actual_DT": "dow_med_dt"})
    )
    dow = dow.merge(overall, on=["BRANCHID", "Category"], how="left")
    dow["dow_factor"] = np.where(dow["mean_dt"] > 0, dow["dow_med_dt"] / dow["mean_dt"], 1.0)

    # fallback by category-dow
    dow_cat = (
        d_recent.groupby(["Category", "dow"], as_index=False)["Actual_DT"]
        .median()
        .rename(columns={"Actual_DT": "cat_dow_med_dt"})
    )
    cat_mean = (
        d_recent.groupby(["Category"], as_index=False)["Actual_DT"]
        .mean()
        .rename(columns={"Actual_DT": "cat_mean_dt"})
    )
    dow_cat = dow_cat.merge(cat_mean, on="Category", how="left")
    dow_cat["cat_dow_factor"] = np.where(dow_cat["cat_mean_dt"] > 0, dow_cat["cat_dow_med_dt"] / dow_cat["cat_mean_dt"], 1.0)

    # Seasonality factor by month-of-year (combo + category fallback)
    hist["month"] = hist["Date"].dt.month
    season_combo = (
        hist.groupby(["BRANCHID", "Category", "month"], as_index=False)["Actual_DT"]
        .median()
        .rename(columns={"Actual_DT": "m_med"})
    )
    base_combo = (
        hist.groupby(["BRANCHID", "Category"], as_index=False)["Actual_DT"]
        .median()
        .rename(columns={"Actual_DT": "combo_med"})
    )
    season_combo = season_combo.merge(base_combo, on=["BRANCHID", "Category"], how="left")
    season_combo["season_factor"] = np.where(season_combo["combo_med"] > 0, season_combo["m_med"] / season_combo["combo_med"], 1.0)

    season_cat = (
        hist.groupby(["Category", "month"], as_index=False)["Actual_DT"]
        .median()
        .rename(columns={"Actual_DT": "cat_m_med"})
    )
    base_cat = (
        hist.groupby(["Category"], as_index=False)["Actual_DT"]
        .median()
        .rename(columns={"Actual_DT": "cat_med"})
    )
    season_cat = season_cat.merge(base_cat, on="Category", how="left")
    season_cat["cat_season_factor"] = np.where(season_cat["cat_med"] > 0, season_cat["cat_m_med"] / season_cat["cat_med"], 1.0)

    # Mild global prior: summer > winter
    # (only matters as slight multiplicative prior; data still dominates)
    summer_months = {5, 6, 7, 8}
    winter_months = {11, 12, 1, 2}
    month_prior = {m: 1.0 for m in range(1, 13)}
    for mm in summer_months:
        month_prior[mm] = 1.05
    for mm in winter_months:
        month_prior[mm] = 0.95

    month_prior_df = pd.DataFrame({"month": list(month_prior.keys()), "month_prior": list(month_prior.values())})

    # Holiday effects from historical lifts
    h = hist.copy()
    hf = holiday_flags(h["Date"])
    h = pd.concat([h.reset_index(drop=True), hf.reset_index(drop=True)], axis=1)
    h["holiday_label"] = h[["is_tet_pre", "is_304_15", "is_children_16", "is_trung_thu", "is_christmas", "is_new_year"]].apply(build_holiday_label, axis=1)

    # Baseline non-holiday mean by combo,dow
    h["dow"] = h["Date"].dt.weekday
    base_non_h = (
        h[h["holiday_label"] == "none"].groupby(["BRANCHID", "Category", "dow"], as_index=False)["Actual_DT"]
        .median()
        .rename(columns={"Actual_DT": "base_non_h"})
    )
    hh = h[h["holiday_label"] != "none"].merge(base_non_h, on=["BRANCHID", "Category", "dow"], how="left")
    hh["lift"] = np.where(hh["base_non_h"] > 0, hh["Actual_DT"] / hh["base_non_h"], np.nan)

    holiday_combo = (
        hh.groupby(["BRANCHID", "Category", "holiday_label"])["lift"]
        .agg(
            lift_raw=lambda x: robust_median(pd.Series(x), default=np.nan),
            n=lambda x: int(pd.Series(x).notna().sum()),
        )
        .reset_index()
    )
    holiday_cat = (
        hh.groupby(["Category", "holiday_label"], as_index=False)["lift"]
        .agg(lambda x: robust_median(pd.Series(x), default=1.0))
        .rename(columns={"lift": "lift_cat"})
    )
    global_h_lift = (
        hh.groupby(["holiday_label"], as_index=False)["lift"]
        .agg(lambda x: robust_median(pd.Series(x), default=1.0))
        .rename(columns={"lift": "lift_global"})
    )

    holiday_combo = holiday_combo.merge(holiday_cat, on=["Category", "holiday_label"], how="left")
    holiday_combo = holiday_combo.merge(global_h_lift, on=["holiday_label"], how="left")
    holiday_combo["anchor"] = holiday_combo["lift_cat"].fillna(holiday_combo["lift_global"]).fillna(1.0)
    holiday_combo["lift_raw"] = holiday_combo["lift_raw"].fillna(holiday_combo["anchor"])
    holiday_combo["holiday_factor"] = [
        shrink(v, a, n=n, k=6.0) for v, a, n in zip(holiday_combo["lift_raw"], holiday_combo["anchor"], holiday_combo["n"])
    ]

    # AOV for DT<->GD conversion
    pos = hist[(hist["Actual_DT"] > 0) & (hist["Actual_GD"] > 0)].copy()
    pos["aov"] = pos["Actual_DT"] / pos["Actual_GD"]
    aov_combo = (
        pos.groupby(["BRANCHID", "Category"], as_index=False)["aov"]
        .median()
        .rename(columns={"aov": "aov_combo"})
    )
    aov_cat = (
        pos.groupby(["Category"], as_index=False)["aov"]
        .median()
        .rename(columns={"aov": "aov_cat"})
    )
    aov_global = robust_median(pos["aov"], default=1.0)

    # Bundle outputs in wide objects for merge in forecast stage
    dow_out = dow[["BRANCHID", "Category", "dow", "dow_factor"]].copy()
    dow_cat_out = dow_cat[["Category", "dow", "cat_dow_factor"]].copy()
    season_combo_out = season_combo[["BRANCHID", "Category", "month", "season_factor"]].copy()
    season_cat_out = season_cat[["Category", "month", "cat_season_factor"]].copy()
    holiday_out = holiday_combo[["BRANCHID", "Category", "holiday_label", "holiday_factor"]].copy()

    meta = {
        "dow_cat": dow_cat_out,
        "season_cat": season_cat_out,
        "holiday_cat": holiday_cat,
        "holiday_global": global_h_lift,
        "aov_cat": aov_cat,
        "aov_global": aov_global,
        "month_prior": month_prior_df,
    }

    return m, combo_yoy, dow_out, season_combo_out, holiday_out, aov_combo, meta


def main() -> None:
    # 1) Load and clean
    raw = pd.read_excel(INPUT_XLSX, engine="openpyxl")
    df = normalize_columns(raw)

    # Parse + clean
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["BRANCHID"] = df["BRANCHID"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip()

    for col in ["Actual_DT", "Actual_GD"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Date", "BRANCHID", "Category"])
    df = df[(df["BRANCHID"] != "") & (df["Category"] != "")]

    df[["Actual_DT", "Actual_GD"]] = df[["Actual_DT", "Actual_GD"]].fillna(0.0)

    # Keep only training span up to end of Feb-2026
    hist = df[df["Date"] <= TRAIN_END].copy()

    # Aggregate in case duplicates exist
    hist = (
        hist.groupby(["BRANCHID", "Category", "Date"], as_index=False)
        .agg(Actual_DT=("Actual_DT", "sum"), Actual_GD=("Actual_GD", "sum"))
    )

    # 2) Feature tables
    monthly_flags, combo_yoy, dow_factor, season_factor, holiday_factor, aov_combo, meta = build_combo_features(hist)

    # Closing rule set from Feb-2026
    feb = hist[(hist["Date"] >= pd.Timestamp("2026-02-01")) & (hist["Date"] <= pd.Timestamp("2026-02-28"))]
    feb_sales = (
        feb.groupby(["BRANCHID", "Category"], as_index=False)["Actual_DT"]
        .sum()
        .rename(columns={"Actual_DT": "feb_sales"})
    )

    # Combos to forecast = combos seen historically
    combos = hist[["BRANCHID", "Category"]].drop_duplicates().copy()
    combos = combos.merge(feb_sales, on=["BRANCHID", "Category"], how="left")
    combos["feb_sales"] = combos["feb_sales"].fillna(0.0)
    combos["is_closed_rule"] = combos["feb_sales"] <= 0

    # Build forecast grid
    fc_dates = pd.date_range(FC_START, FC_END, freq="D")
    fc = combos.assign(key=1).merge(pd.DataFrame({"Date": fc_dates, "key": 1}), on="key", how="outer").drop(columns=["key"])

    # Last-year same-day base
    ly = hist[["BRANCHID", "Category", "Date", "Actual_DT", "Actual_GD"]].copy()
    ly["Date"] = ly["Date"] + pd.DateOffset(years=1)
    ly = ly.rename(columns={"Actual_DT": "ly_dt", "Actual_GD": "ly_gd"})
    fc = fc.merge(ly, on=["BRANCHID", "Category", "Date"], how="left")
    fc[["ly_dt", "ly_gd"]] = fc[["ly_dt", "ly_gd"]].fillna(0.0)

    # Trend factor (L3M YoY)
    fc = fc.merge(combo_yoy[["BRANCHID", "Category", "trend_factor", "yoy_shrunk"]], on=["BRANCHID", "Category"], how="left")
    fc["trend_factor"] = fc["trend_factor"].fillna(1.0)
    fc["yoy_shrunk"] = fc["yoy_shrunk"].fillna(1.0)

    # DOW adjustments
    fc["dow"] = fc["Date"].dt.weekday
    fc["ly_dow"] = (fc["Date"] - pd.DateOffset(years=1)).dt.weekday

    fc = fc.merge(
        dow_factor.rename(columns={"dow": "dow_fc", "dow_factor": "dow_factor_fc"}),
        left_on=["BRANCHID", "Category", "dow"],
        right_on=["BRANCHID", "Category", "dow_fc"],
        how="left",
    ).drop(columns=["dow_fc"])

    fc = fc.merge(
        dow_factor.rename(columns={"dow": "dow_ly", "dow_factor": "dow_factor_ly"}),
        left_on=["BRANCHID", "Category", "ly_dow"],
        right_on=["BRANCHID", "Category", "dow_ly"],
        how="left",
    ).drop(columns=["dow_ly"])

    # category fallback for missing combo DOW
    dow_cat = meta["dow_cat"]
    fc = fc.merge(
        dow_cat.rename(columns={"dow": "dow_fc", "cat_dow_factor": "cat_dow_factor_fc"}),
        left_on=["Category", "dow"],
        right_on=["Category", "dow_fc"],
        how="left",
    ).drop(columns=["dow_fc"])
    fc = fc.merge(
        dow_cat.rename(columns={"dow": "dow_ly", "cat_dow_factor": "cat_dow_factor_ly"}),
        left_on=["Category", "ly_dow"],
        right_on=["Category", "dow_ly"],
        how="left",
    ).drop(columns=["dow_ly"])

    fc["dow_factor_fc"] = fc["dow_factor_fc"].fillna(fc["cat_dow_factor_fc"]).fillna(1.0)
    fc["dow_factor_ly"] = fc["dow_factor_ly"].fillna(fc["cat_dow_factor_ly"]).fillna(1.0)
    fc["dow_adj"] = np.where(fc["dow_factor_ly"] > 0, fc["dow_factor_fc"] / fc["dow_factor_ly"], 1.0)

    # Seasonality adjustments
    fc["month"] = fc["Date"].dt.month
    fc = fc.merge(season_factor, on=["BRANCHID", "Category", "month"], how="left")
    fc = fc.merge(meta["season_cat"], on=["Category", "month"], how="left")
    fc = fc.merge(meta["month_prior"], on="month", how="left")

    fc["season_factor"] = fc["season_factor"].fillna(fc["cat_season_factor"]).fillna(1.0)
    fc["month_prior"] = fc["month_prior"].fillna(1.0)
    fc["season_adj"] = fc["season_factor"] * fc["month_prior"]

    # Holiday adjustments
    hfc = holiday_flags(fc["Date"])
    fc = pd.concat([fc.reset_index(drop=True), hfc.reset_index(drop=True)], axis=1)
    fc["holiday_label"] = fc[["is_tet_pre", "is_304_15", "is_children_16", "is_trung_thu", "is_christmas", "is_new_year"]].apply(build_holiday_label, axis=1)

    fc = fc.merge(holiday_factor, on=["BRANCHID", "Category", "holiday_label"], how="left")

    # Category/global fallback
    h_cat = meta["holiday_cat"].rename(columns={"lift_cat": "holiday_cat_factor"})
    h_glb = meta["holiday_global"].rename(columns={"lift_global": "holiday_global_factor"})
    fc = fc.merge(h_cat, on=["Category", "holiday_label"], how="left")
    fc = fc.merge(h_glb, on=["holiday_label"], how="left")

    fc["holiday_factor"] = fc["holiday_factor"].fillna(fc["holiday_cat_factor"]).fillna(fc["holiday_global_factor"]).fillna(1.0)

    # Core forecast
    # start from LY same-day and scale by trend/calendar effects
    fc["forecast_dt_raw"] = fc["ly_dt"] * fc["trend_factor"] * fc["dow_adj"] * fc["season_adj"] * fc["holiday_factor"]

    # Fallback where LY is zero: use recent 28-day median daily level
    recent_28_start = TRAIN_END - pd.Timedelta(days=27)
    recent28 = hist[(hist["Date"] >= recent_28_start) & (hist["Date"] <= TRAIN_END)].copy()
    base28 = (
        recent28.groupby(["BRANCHID", "Category"], as_index=False)["Actual_DT"]
        .median()
        .rename(columns={"Actual_DT": "base28"})
    )
    fc = fc.merge(base28, on=["BRANCHID", "Category"], how="left")
    fc["base28"] = fc["base28"].fillna(0.0)

    use_fallback = (fc["ly_dt"] <= 0)
    fc.loc[use_fallback, "forecast_dt_raw"] = (
        fc.loc[use_fallback, "base28"]
        * fc.loc[use_fallback, "trend_factor"]
        * fc.loc[use_fallback, "dow_factor_fc"]
        * fc.loc[use_fallback, "season_adj"]
        * fc.loc[use_fallback, "holiday_factor"]
    )

    # Non-negative and round
    fc["Forecast_DT"] = np.maximum(fc["forecast_dt_raw"], 0.0)

    # Closing rule override
    fc.loc[fc["is_closed_rule"], "Forecast_DT"] = 0.0

    # Forecast GD via robust AOV
    fc = fc.merge(aov_combo, on=["BRANCHID", "Category"], how="left")
    fc = fc.merge(meta["aov_cat"], on=["Category"], how="left")
    fc["aov_use"] = fc["aov_combo"].fillna(fc["aov_cat"]).fillna(meta["aov_global"]).replace(0, np.nan)
    fc["Forecast_GD"] = np.where(fc["aov_use"].notna() & (fc["aov_use"] > 0), fc["Forecast_DT"] / fc["aov_use"], 0.0)
    fc.loc[fc["is_closed_rule"], "Forecast_GD"] = 0.0

    # tidy + output columns
    fc["Date"] = pd.to_datetime(fc["Date"]).dt.date
    fc["is_weekend"] = pd.to_datetime(fc["Date"]).dt.weekday >= 5

    out_cols = [
        "Date",
        "BRANCHID",
        "Category",
        "Forecast_DT",
        "Forecast_GD",
        "is_closed_rule",
        "trend_factor",
        "yoy_shrunk",
        "dow_adj",
        "season_adj",
        "holiday_label",
        "holiday_factor",
        "ly_dt",
        "base28",
    ]

    out = fc[out_cols].copy()
    out["Forecast_DT"] = out["Forecast_DT"].round(0)
    out["Forecast_GD"] = out["Forecast_GD"].round(0)

    out = out.sort_values(["Date", "BRANCHID", "Category"]).reset_index(drop=True)
    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"Done. Output rows: {len(out):,}")
    print(f"Saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
