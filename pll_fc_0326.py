#!/usr/bin/env python3
"""pll_fc_0326.py

Forecast day x Category x Branch sales (Actual_DT) for March 2026 from:
  /Users/anhtrinh/Downloads/06 dev/pll-pe/pll-raw-sales.xlsx

Outputs CSV to same folder:
  /Users/anhtrinh/Downloads/06 dev/pll-pe/pll_fc_0326.csv

Dependencies:
  pip install pandas numpy openpyxl

Notes on business rules implemented:
- Closing rule: if BranchID×Category has no sales in Feb-2026 => forecast Mar-2026 = 0.
- Opening / renovation ramp: detect opening (first month with sales) and renovation-like spikes;
  exclude ramp months from YoY trend estimation to avoid inflated growth baselines.
- Weekend/weekday effect: learn per BranchID×Category weekend multiplier vs weekday from last 6 months.
- Holidays: create holiday flags (Tet pre-period, 30/4-1/5, 1/6, Trung thu, Christmas, New Year).
  (March 2026 has no major holiday in this list, but the framework is included.)
- L3M YoY trend: expected YoY for Mar-2026 is anchored to recent (Dec/Jan/Feb) YoY, with
  shrinkage (soft constraint) so it does not drift too far.
- Seasonality: month-of-year factors are estimated from history; March is adjusted vs February.

Output columns (daily forecast):
  Date, BranchID, Category, Fc_DT, Fc_GD, is_weekend, holiday_flags...
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd


# ===== Hardcoded IO (per request) =====
IN_PATH = Path("/Users/anhtrinh/Downloads/06 dev/pll-pe/pll-raw-sales.xlsx")
OUT_PATH = IN_PATH.parent / "pll_fc_0326.csv"
SHEET_NAME = "Actual_data"

FORECAST_MONTH = pd.Period("2026-03", freq="M")
LAST_MONTH = pd.Period("2026-02", freq="M")


# ===== Holiday dates (verified via web search snippets) =====
# Tet Day (Mồng 1 Tết)
TET_DAY = {
    2023: pd.Timestamp("2023-01-22"),
    2024: pd.Timestamp("2024-02-10"),
    2025: pd.Timestamp("2025-01-29"),
    2026: pd.Timestamp("2026-02-17"),
}

# Mid-Autumn (Trung thu / Rằm tháng 8)
MID_AUTUMN_DAY = {
    2023: pd.Timestamp("2023-09-29"),
    2024: pd.Timestamp("2024-09-17"),
    2025: pd.Timestamp("2025-10-06"),
    2026: pd.Timestamp("2026-09-25"),
}


def make_holiday_flags(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Return DataFrame indexed by dates with holiday flags."""
    cal = pd.DataFrame(index=dates)
    cal["is_newyear"] = (cal.index.month == 1) & (cal.index.day == 1)
    cal["is_christmas"] = (cal.index.month == 12) & (cal.index.day == 25)
    cal["is_304_15"] = ((cal.index.month == 4) & (cal.index.day == 30)) | ((cal.index.month == 5) & (cal.index.day == 1))
    cal["is_16"] = (cal.index.month == 6) & (cal.index.day == 1)

    # Tet pre-period: D-7..D-1 relative to Tet Day (D0)
    tet_pre = pd.Series(False, index=dates)
    for y, d0 in TET_DAY.items():
        pre = pd.date_range(d0 - pd.Timedelta(days=7), d0 - pd.Timedelta(days=1), freq="D")
        tet_pre.loc[tet_pre.index.intersection(pre)] = True
    cal["is_tet_pre"] = tet_pre.values

    mid = pd.Series(False, index=dates)
    for y, d in MID_AUTUMN_DAY.items():
        if d in dates:
            mid.loc[d] = True
    cal["is_midautumn"] = mid.values

    return cal.reset_index(names=["Date"])


def soft_anchor(log_target: float, log_raw: float, k: float = 0.35) -> float:
    """Softly anchor log_raw around log_target with smooth saturation (no hard cap).

    When |log_raw - log_target| >> k, the adjustment saturates to about +/-k.
    k=0.35 ~ allows ~ +/-42% move in multiplicative terms (exp(0.35)~1.42).
    """
    if not np.isfinite(log_target):
        return log_raw
    if not np.isfinite(log_raw):
        return log_target
    return float(log_target + k * math.tanh((log_raw - log_target) / k))


def robust_median(x: Iterable[float]) -> float:
    x = np.asarray(list(x), dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return float("nan")
    return float(np.median(x))


def robust_geo_mean(x: Iterable[float]) -> float:
    """Geometric mean with safety (expects ratios >0)."""
    x = np.asarray(list(x), dtype=float)
    x = x[np.isfinite(x) & (x > 0)]
    if len(x) == 0:
        return float("nan")
    return float(np.exp(np.mean(np.log(x))))


def winsorize(x: np.ndarray, p: float = 0.1) -> np.ndarray:
    x = x.copy()
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return x
    lo = np.quantile(x, p)
    hi = np.quantile(x, 1 - p)
    return np.clip(x, lo, hi)


@dataclass
class ComboInfo:
    branch: str
    category: str
    feb_sales: float
    aov: float
    weekend_mult: float
    weekday_mult: float
    season_factor: Dict[int, float]  # month -> factor
    l3m_yoy: float
    march_yoy_hist: float
    cat_l3m_yoy: float


def load_daily() -> pd.DataFrame:
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Input not found: {IN_PATH}")

    df = pd.read_excel(IN_PATH, sheet_name=SHEET_NAME)
    df = df.dropna(subset=["BranchID", "Date", "Category"]).copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).copy()

    for col in ["Actual_DT", "Actual_GD"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        df[col] = df[col].clip(lower=0.0)

    df["BranchID"] = df["BranchID"].astype(str)
    df["Category"] = df["Category"].astype(str)

    # daily agg
    daily = (
        df.groupby(["Date", "BranchID", "Category"], as_index=False)[["Actual_DT", "Actual_GD"]]
        .sum()
        .sort_values(["BranchID", "Category", "Date"])
        .reset_index(drop=True)
    )
    daily["ym"] = daily["Date"].dt.to_period("M")
    daily["dow"] = daily["Date"].dt.dayofweek
    daily["is_weekend"] = daily["dow"].isin([5, 6])
    return daily


def build_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    m = daily.groupby(["BranchID", "Category", "ym"], as_index=False)["Actual_DT"].sum()
    m = m.rename(columns={"Actual_DT": "DT"})

    # YoY merge
    m["ym_prev"] = m["ym"] - 12
    prev = m[["BranchID", "Category", "ym", "DT"]].rename(columns={"ym": "ym_prev", "DT": "DT_prev"})
    m = m.merge(prev, on=["BranchID", "Category", "ym_prev"], how="left")
    m["yoy"] = np.where(m["DT_prev"].fillna(0) > 0, m["DT"] / m["DT_prev"], np.nan)

    # Opening ramp: first month with DT>0
    pos = m[m["DT"] > 0].copy()
    first = pos.groupby(["BranchID", "Category"], as_index=False)["ym"].min().rename(columns={"ym": "first_ym"})
    m = m.merge(first, on=["BranchID", "Category"], how="left")
    m["is_opening_m1"] = m["ym"] == m["first_ym"]
    m["is_opening_m2"] = m["ym"] == (m["first_ym"] + 1)

    # Renovation-like spike: unusually high YoY AND unusually high DT
    m["is_reno_spike"] = False
    # Per combo thresholds
    for (b, c), g in m.groupby(["BranchID", "Category"], sort=False):
        idx = g.index
        dt = g["DT"].to_numpy(dtype=float)
        yoy = g["yoy"].to_numpy(dtype=float)
        if np.isfinite(dt).sum() < 6:
            continue
        dt_p75 = np.nanpercentile(dt, 75)
        # rolling median yoy for context
        yoy_med = pd.Series(yoy).rolling(12, min_periods=3).median().to_numpy()
        spike = (yoy > np.maximum(2.5, 2.0 * np.nan_to_num(yoy_med, nan=1.0))) & (dt > dt_p75)

        # Also catch big MoM spikes (when YoY unavailable)
        dt_med6 = pd.Series(dt).rolling(6, min_periods=3).median().to_numpy()
        mom_spike = (dt > 3.0 * np.nan_to_num(dt_med6, nan=0.0)) & (dt > dt_p75)

        spike = np.where(np.isfinite(yoy), spike, mom_spike)
        if spike.any():
            m.loc[idx, "is_reno_spike"] = spike

    # Ramp mask: opening m1/m2 or reno spike month and next month
    m["is_ramp"] = m["is_opening_m1"] | m["is_opening_m2"] | m["is_reno_spike"]
    # next month after reno spike treated as ramp as well
    m["is_ramp_next"] = False
    reno = m[m["is_reno_spike"]][["BranchID", "Category", "ym"]].copy()
    if len(reno) > 0:
        reno["ym"] = reno["ym"] + 1
        reno["is_ramp_next"] = True
        m = m.merge(reno, on=["BranchID", "Category", "ym"], how="left", suffixes=("", "_x"))
        m["is_ramp_next"] = m["is_ramp_next"].fillna(False)
        m["is_ramp"] = m["is_ramp"] | m["is_ramp_next"]

    return m


def compute_seasonality(monthly: pd.DataFrame) -> Tuple[Dict[Tuple[str, str], Dict[int, float]], Dict[str, Dict[int, float]]]:
    """Return seasonality factors by (branch,cat) and by cat.

    Factor definition (per year): month_DT / (year_total/12).
    Then take median across years, excluding ramp months.
    """
    tmp = monthly.copy()
    tmp = tmp[~tmp["is_ramp"]].copy()
    tmp["year"] = tmp["ym"].dt.year
    tmp["month"] = tmp["ym"].dt.month

    # year totals
    yt = tmp.groupby(["BranchID", "Category", "year"], as_index=False)["DT"].sum().rename(columns={"DT": "year_DT"})
    tmp = tmp.merge(yt, on=["BranchID", "Category", "year"], how="left")
    tmp["year_avg_month"] = tmp["year_DT"] / 12.0
    tmp["season_ratio"] = np.where(tmp["year_avg_month"] > 0, tmp["DT"] / tmp["year_avg_month"], np.nan)

    # combo seasonality
    combo_f = {}
    for (b, c), g in tmp.groupby(["BranchID", "Category"], sort=False):
        f = {}
        for mth, gg in g.groupby("month"):
            f[int(mth)] = robust_median(gg["season_ratio"].to_numpy())
        combo_f[(b, c)] = f

    # category-level fallback
    cat_f = {}
    for c, g in tmp.groupby(["Category"], sort=False):
        f = {}
        for mth, gg in g.groupby("month"):
            f[int(mth)] = robust_median(gg["season_ratio"].to_numpy())
        cat_f[str(c)] = f

    return combo_f, cat_f


def compute_weekpart_multipliers(daily: pd.DataFrame) -> Dict[Tuple[str, str], Tuple[float, float]]:
    """Compute (weekday_mult, weekend_mult) per combo from last 6 months.

    We compute ratio of day DT to that month's average DT/day, then take median by weekpart.
    """
    start = (LAST_MONTH - 5).to_timestamp(how="start")
    end = LAST_MONTH.to_timestamp(how="end")
    d = daily[(daily["Date"] >= start) & (daily["Date"] <= end)].copy()

    # month avg per day
    md = d.groupby(["BranchID", "Category", "ym"], as_index=False).agg(
        DT_m=("Actual_DT", "sum"),
        n_days=("Date", "nunique"),
    )
    md["avg_per_day"] = np.where(md["n_days"] > 0, md["DT_m"] / md["n_days"], np.nan)
    d = d.merge(md[["BranchID", "Category", "ym", "avg_per_day"]], on=["BranchID", "Category", "ym"], how="left")
    d["ratio"] = np.where(d["avg_per_day"] > 0, d["Actual_DT"] / d["avg_per_day"], np.nan)

    out: Dict[Tuple[str, str], Tuple[float, float]] = {}
    for (b, c), g in d.groupby(["BranchID", "Category"], sort=False):
        wk = robust_median(g.loc[~g["is_weekend"], "ratio"])
        we = robust_median(g.loc[g["is_weekend"], "ratio"])
        if not np.isfinite(wk):
            wk = 1.0
        if not np.isfinite(we):
            we = 1.8  # sensible default
        # ensure weekends >= weekdays (typical for PLL)
        we = max(we, wk)
        out[(b, c)] = (float(wk), float(we))
    return out


def compute_aov(daily: pd.DataFrame) -> Dict[Tuple[str, str], float]:
    """Average order value proxy from last 3 months: AOV = DT / GD."""
    start = (LAST_MONTH - 2).to_timestamp(how="start")
    end = LAST_MONTH.to_timestamp(how="end")
    d = daily[(daily["Date"] >= start) & (daily["Date"] <= end)].copy()
    g = d.groupby(["BranchID", "Category"], as_index=True).agg(DT=("Actual_DT", "sum"), GD=("Actual_GD", "sum"))
    aov = (g["DT"] / g["GD"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    # fallback to global if missing
    global_aov = float((g["DT"].sum() / max(g["GD"].sum(), 1.0)))
    out = {}
    for idx, v in aov.items():
        out[idx] = float(v) if np.isfinite(v) and v > 0 else global_aov
    return out


def compute_l3m_yoy(monthly: pd.DataFrame) -> Tuple[Dict[Tuple[str, str], float], Dict[str, float]]:
    """Compute L3M (Dec/Jan/Feb) YoY ratio per combo, excluding ramp months.

    Also returns category-level fallback (same window).
    """
    months = [pd.Period("2025-12"), pd.Period("2026-01"), pd.Period("2026-02")]
    m = monthly[monthly["ym"].isin(months)].copy()
    m = m[(~m["is_ramp"]) & (m["yoy"].notna()) & (m["yoy"] > 0)].copy()

    combo = {}
    for (b, c), g in m.groupby(["BranchID", "Category"], sort=False):
        y = winsorize(g["yoy"].to_numpy(dtype=float), p=0.1)
        combo[(b, c)] = robust_geo_mean(y)

    cat = {}
    for c, g in m.groupby(["Category"], sort=False):
        y = winsorize(g["yoy"].to_numpy(dtype=float), p=0.1)
        cat[str(c)] = robust_geo_mean(y)

    # global fallback
    if "__GLOBAL__" not in cat:
        y = winsorize(m["yoy"].to_numpy(dtype=float), p=0.1)
        cat["__GLOBAL__"] = robust_geo_mean(y)

    return combo, cat


def compute_march_yoy_hist(monthly: pd.DataFrame) -> Dict[Tuple[str, str], float]:
    """Historical March YoY ratios (March 2024 vs 2023, March 2025 vs 2024).

    Limited data -> use robust median; exclude ramp months.
    """
    march = monthly[monthly["ym"].dt.month == 3].copy()
    march = march[(~march["is_ramp"]) & march["yoy"].notna() & (march["yoy"] > 0)].copy()

    out = {}
    for (b, c), g in march.groupby(["BranchID", "Category"], sort=False):
        out[(b, c)] = robust_median(g["yoy"].to_numpy(dtype=float))
    return out


def forecast_monthly_dt(
    branch: str,
    category: str,
    monthly: pd.DataFrame,
    combo_season: Dict[Tuple[str, str], Dict[int, float]],
    cat_season: Dict[str, Dict[int, float]],
    l3m_yoy: Dict[Tuple[str, str], float],
    cat_l3m_yoy: Dict[str, float],
    march_yoy_hist: Dict[Tuple[str, str], float],
) -> float:
    """Return forecast monthly DT for FORECAST_MONTH."""
    key = (branch, category)

    # Closing rule: if Feb-2026 has no sales => 0
    feb = monthly[(monthly["BranchID"] == branch) & (monthly["Category"] == category) & (monthly["ym"] == LAST_MONTH)]
    feb_sales = float(feb["DT"].iloc[0]) if len(feb) else 0.0
    if feb_sales <= 0:
        return 0.0

    # Base: March-2025 (same month last year) if available
    base_row = monthly[(monthly["BranchID"] == branch) & (monthly["Category"] == category) & (monthly["ym"] == pd.Period("2025-03"))]
    base_march_2025 = float(base_row["DT"].iloc[0]) if len(base_row) else float("nan")

    # Get YoY components
    l3m = float(l3m_yoy.get(key, float("nan")))
    cat_l3m = float(cat_l3m_yoy.get(category, cat_l3m_yoy.get("__GLOBAL__", 1.0)))
    mh = float(march_yoy_hist.get(key, float("nan")))

    # Build raw expected YoY (log-space blend)
    parts = []
    weights = []

    if np.isfinite(l3m) and l3m > 0:
        parts.append(math.log(l3m))
        weights.append(0.55)
    if np.isfinite(mh) and mh > 0:
        parts.append(math.log(mh))
        weights.append(0.25)
    if np.isfinite(cat_l3m) and cat_l3m > 0:
        parts.append(math.log(cat_l3m))
        weights.append(0.20)

    if len(parts) == 0:
        log_raw = 0.0
        log_target = 0.0
    else:
        w = np.array(weights, dtype=float)
        w = w / w.sum()
        log_raw = float(np.sum(w * np.array(parts, dtype=float)))
        log_target = math.log(l3m) if np.isfinite(l3m) and l3m > 0 else float("nan")

    log_final = soft_anchor(log_target=log_target, log_raw=log_raw, k=0.35)
    yoy_final = float(np.exp(log_final))

    # Seasonality adjustment: March vs February
    sf_combo = combo_season.get(key, {})
    sf_cat = cat_season.get(category, {})

    def get_sf(month: int) -> float:
        v = sf_combo.get(month, float("nan"))
        if not np.isfinite(v):
            v = sf_cat.get(month, float("nan"))
        if not np.isfinite(v):
            v = 1.0
        return float(v)

    sf_mar = get_sf(3)
    sf_feb = get_sf(2)
    season_adj = sf_mar / sf_feb if sf_feb > 0 else 1.0

    # Main formula
    if np.isfinite(base_march_2025) and base_march_2025 > 0:
        fc = base_march_2025 * yoy_final
    else:
        # fallback: scale Feb-2026 by seasonality ratio
        fc = feb_sales * season_adj

    # Guardrails (non-hard): prevent absurd collapse if active
    # Use a gentle floor based on recent 3M average
    recent_months = [pd.Period("2025-12"), pd.Period("2026-01"), pd.Period("2026-02")]
    recent = monthly[(monthly["BranchID"] == branch) & (monthly["Category"] == category) & (monthly["ym"].isin(recent_months))]
    rmean = float(recent["DT"].mean()) if len(recent) else feb_sales
    if np.isfinite(rmean) and rmean > 0 and fc > 0:
        # smooth floor at 30% of recent mean
        floor = 0.3 * rmean
        fc = float(floor + (fc - floor) * (1.0 - math.exp(-max(fc, 0.0) / max(rmean, 1.0))))

    return float(max(fc, 0.0))


def distribute_daily(
    branch: str,
    category: str,
    monthly_fc: float,
    weekpart_mult: Tuple[float, float],
    cal: pd.DataFrame,
) -> pd.DataFrame:
    """Allocate monthly forecast into daily values for March 2026."""
    if monthly_fc <= 0:
        out = cal[["Date"]].copy()
        out["Fc_DT"] = 0.0
        return out

    weekday_mult, weekend_mult = weekpart_mult
    weights = np.where(cal["is_weekend"].to_numpy(), weekend_mult, weekday_mult).astype(float)

    # Holiday multipliers (kept modest by default; can be learned later)
    # For March, these flags are typically all False; but included for completeness.
    holiday_cols = ["is_tet_pre", "is_304_15", "is_16", "is_midautumn", "is_christmas", "is_newyear"]
    for col in holiday_cols:
        if col in cal.columns:
            # modest uplift on holiday days if present
            weights *= np.where(cal[col].to_numpy(), 1.25, 1.0)

    weights = np.clip(weights, 1e-9, None)
    weights = weights / weights.sum()

    out = cal[["Date"]].copy()
    out["Fc_DT"] = monthly_fc * weights
    return out


def main() -> None:
    daily = load_daily()
    monthly = build_monthly(daily)

    # Seasonality + multipliers + AOV
    combo_season, cat_season = compute_seasonality(monthly)
    weekpart = compute_weekpart_multipliers(daily)
    aov = compute_aov(daily)

    l3m_yoy, cat_l3m_yoy = compute_l3m_yoy(monthly)
    march_yoy_hist = compute_march_yoy_hist(monthly)

    # combos to forecast: all combos present historically
    combos = daily[["BranchID", "Category"]].drop_duplicates().sort_values(["BranchID", "Category"])

    # March 2026 calendar
    dates = pd.date_range(FORECAST_MONTH.to_timestamp(how="start"), FORECAST_MONTH.to_timestamp(how="end"), freq="D")
    cal = make_holiday_flags(dates)
    cal["dow"] = pd.to_datetime(cal["Date"]).dt.dayofweek
    cal["is_weekend"] = cal["dow"].isin([5, 6])

    rows = []

    # Precompute Feb sales per combo for closing rule & debug
    feb_sales_tbl = (
        monthly[monthly["ym"] == LAST_MONTH][["BranchID", "Category", "DT"]]
        .rename(columns={"DT": "Feb_DT"})
        .copy()
    )

    for br, cat in combos.itertuples(index=False, name=None):
        monthly_fc = forecast_monthly_dt(
            br,
            cat,
            monthly,
            combo_season,
            cat_season,
            l3m_yoy,
            cat_l3m_yoy,
            march_yoy_hist,
        )

        wk_mult = weekpart.get((br, cat), (1.0, 1.8))
        dist = distribute_daily(br, cat, monthly_fc, wk_mult, cal)
        dist["BranchID"] = br
        dist["Category"] = cat

        # Transactions forecast via AOV
        this_aov = float(aov.get((br, cat), 1.0))
        dist["Fc_GD"] = np.where(this_aov > 0, dist["Fc_DT"] / this_aov, 0.0)

        # add flags
        for col in ["is_weekend", "is_tet_pre", "is_304_15", "is_16", "is_midautumn", "is_christmas", "is_newyear"]:
            dist[col] = cal[col].values if col in cal.columns else False

        dist["Fc_DT"] = dist["Fc_DT"].round(0)
        dist["Fc_GD"] = dist["Fc_GD"].round(2)
        rows.append(dist)

    out = pd.concat(rows, ignore_index=True)

    # Join Feb sales for transparency
    out = out.merge(feb_sales_tbl, on=["BranchID", "Category"], how="left")
    out["Feb_DT"] = out["Feb_DT"].fillna(0.0)

    # Sort and write
    out = out.sort_values(["BranchID", "Category", "Date"]).reset_index(drop=True)
    out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Wrote: {OUT_PATH}")
    print(f"Rows: {len(out):,}")
    print("Example columns:", list(out.columns))


if __name__ == "__main__":
    main()
