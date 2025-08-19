import pandas as pd, numpy as np

def compute_basic_labels(price_df: pd.DataFrame, event_ts: pd.Timestamp):
    price_df = price_df.sort_values("datetime_utc").reset_index(drop=True)
    before = price_df[price_df["datetime_utc"] <= event_ts].tail(1)
    after_30 = price_df[price_df["datetime_utc"] >= event_ts + pd.Timedelta("30m")].head(1)
    after_1h = price_df[price_df["datetime_utc"] >= event_ts + pd.Timedelta("60m")].head(1)
    after_1d = price_df[price_df["datetime_utc"] >= event_ts + pd.Timedelta("1D")].head(1)
    if before.empty: return None
    p0 = before["close"].iloc[0]
    def ret(row):
        if row is None or row.empty: return np.nan
        return float(row["close"].iloc[0] / p0 - 1.0)
    ret_30m = ret(after_30); ret_1h = ret(after_1h); ret_1d = ret(after_1d)
    idx = price_df[price_df["datetime_utc"] == before["datetime_utc"].iloc[0]].index[0]
    win = price_df.iloc[max(0, idx-20):idx]
    vol_mean = win["volume"].mean() if not win.empty else np.nan
    vol_z = float((win["volume"].iloc[-1] - vol_mean) / (vol_mean+1e-9)) if not win.empty else np.nan
    direction = 0 if np.isnan(ret_1h) else (1 if ret_1h > 0 else -1 if ret_1h < 0 else 0)
    impact_level = int(abs(ret_1h) >= 0.015) + int(abs(ret_1h) >= 0.03)
    price_df["don20_hi"] = price_df["close"].rolling(20).max()
    last_close = price_df.loc[idx, "close"]
    last_don_hi = price_df.loc[idx, "don20_hi"]
    breakout_flag = bool(last_close >= last_don_hi) if not np.isnan(last_don_hi) else False
    return {
        "gap_pct": np.nan,
        "ret_30m": ret_30m,
        "ret_1h": ret_1h,
        "ret_1d": ret_1d,
        "ret_5d": np.nan,
        "abnormal_ret_1h": np.nan,
        "vol_zscore_30m": vol_z,
        "direction": direction,
        "impact_level": impact_level,
        "breakout_flag": breakout_flag
    }
