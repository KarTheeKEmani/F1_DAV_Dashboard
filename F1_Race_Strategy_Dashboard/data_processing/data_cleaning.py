import re
from typing import Optional, Any
import numpy as np
import pandas as pd


def parse_timedelta_to_seconds(val) -> Optional[float]:
    """Converts timedelta strings like '0 days 00:01:33.996000' or float/int to seconds."""
    if pd.isna(val) or val is None or val == "":
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    
    val_str = str(val).strip()
    if val_str.lower() in ["nan", "none", "nat", "\\n"]:
        return np.nan

    try:
        # Standard pandas to_timedelta
        td = pd.to_timedelta(val_str)
        return td.total_seconds()
    except Exception:
        pass

    # Regex fallback for mm:ss.sss or ss.sss
    m = re.match(r"(?:(\d+):)?(\d+)(?:\.(\d+))?", val_str)
    if m:
        mins = float(m.group(1)) if m.group(1) else 0.0
        secs = float(m.group(2)) if m.group(2) else 0.0
        frac = float("0." + m.group(3)) if m.group(3) else 0.0
        return mins * 60.0 + secs + frac

    return np.nan


def format_seconds_to_laptime(seconds: Optional[float]) -> str:
    """Formats float seconds into standard F1 timing display (e.g. 1:29.845 or 24.120s)."""
    if pd.isna(seconds) or seconds is None or seconds <= 0:
        return "N/A"
    
    mins = int(seconds // 60)
    secs = seconds % 60
    if mins > 0:
        return f"{mins}:{secs:06.3f}"
    return f"{secs:06.3f}s"


def clean_compound_name(compound: Any) -> str:
    """Normalizes compound names to canonical F1 labels."""
    if pd.isna(compound) or compound is None:
        return "UNKNOWN"
    c_str = str(compound).strip().upper()
    if "SOFT" in c_str:
        return "SOFT"
    elif "MEDIUM" in c_str:
        return "MEDIUM"
    elif "HARD" in c_str:
        return "HARD"
    elif "INTER" in c_str:
        return "INTERMEDIATE"
    elif "WET" in c_str:
        return "WET"
    return c_str if c_str else "UNKNOWN"


def clean_laps_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and enriches lap-by-lap timing records."""
    df = df.copy()

    # Time fields conversion
    time_cols = ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "PitInTime", "PitOutTime"]
    for col in time_cols:
        if col in df.columns:
            sec_col = f"{col}Sec"
            df[sec_col] = df[col].apply(parse_timedelta_to_seconds)

    # Clean Compound
    if "Compound" in df.columns:
        df["Compound"] = df["Compound"].apply(clean_compound_name)
    else:
        df["Compound"] = "UNKNOWN"

    # Numeric casts
    for num_col in ["LapNumber", "Stint", "TyreLife", "SpeedI1", "SpeedI2", "SpeedFL", "SpeedST", "DriverNumber"]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    # Pit Lap Flag
    df["IsPitLap"] = False
    if "PitInTime" in df.columns:
        df["IsPitLap"] = df["PitInTime"].notna()
    elif "IsPitLap" in df.columns:
        df["IsPitLap"] = df["IsPitLap"].astype(bool)

    # Outlier Lap Detection (Safety Car, Yellow Flag, or Pit In/Out laps)
    # An outlier lap is typically > 115% of median lap time for that driver/race, or has PitIn/PitOut
    if "LapTimeSec" in df.columns:
        # Calculate median pace per round and driver
        group_keys = [c for c in ["RoundNumber", "Driver"] if c in df.columns]
        if group_keys:
            df["DriverMedianLapSec"] = df.groupby(group_keys)["LapTimeSec"].transform("median")
            outlier_cond = (df["LapTimeSec"] > df["DriverMedianLapSec"] * 1.15) | df["IsPitLap"]
            if "Sector1TimeSec" in df.columns:
                outlier_cond = outlier_cond | (df["Sector1TimeSec"].isna())
            df["IsOutlierLap"] = outlier_cond
        else:
            df["IsOutlierLap"] = df["IsPitLap"]
    else:
        df["IsOutlierLap"] = False

    return df


def clean_results_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans race classification and results records."""
    df = df.copy()

    for col in ["Position", "GridPosition", "Points", "DriverNumber", "RoundNumber"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Positions Gained / Lost
    if "Position" in df.columns and "GridPosition" in df.columns:
        df["PositionsGained"] = df["GridPosition"] - df["Position"]

    if "Time" in df.columns:
        df["TimeSec"] = df["Time"].apply(parse_timedelta_to_seconds)

    if "Status" not in df.columns:
        df["Status"] = "Finished"

    return df


def clean_pitstops_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans Ergast pit stop records."""
    df = df.copy()

    # duration can be float or string
    if "duration" in df.columns:
        df["DurationSec"] = pd.to_numeric(df["duration"], errors="coerce")
        # In case duration is MM:SS.sss
        mask_nan = df["DurationSec"].isna()
        if mask_nan.any():
            df.loc[mask_nan, "DurationSec"] = df.loc[mask_nan, "duration"].apply(parse_timedelta_to_seconds)
    elif "milliseconds" in df.columns:
        df["DurationSec"] = pd.to_numeric(df["milliseconds"], errors="coerce") / 1000.0

    # Filter out extreme outliers (e.g. red flag pit stop > 120s or garage repairs)
    # Stationary pit stops in F1 are typically 1.8s - 35.0s
    if "DurationSec" in df.columns:
        df["IsCleanPitStop"] = (df["DurationSec"] >= 1.5) & (df["DurationSec"] <= 45.0)

    for col in ["raceId", "driverId", "stop", "lap"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
