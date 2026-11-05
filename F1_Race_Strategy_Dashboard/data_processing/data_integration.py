import re
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

from config import DRIVER_CODE_TO_FULLNAME, TEAM_NAME_MAP


def normalize_team_series(s: pd.Series) -> pd.Series:
    """Standardizes constructor/team names across multiple Kaggle datasets."""
    return s.astype(str).str.strip().replace(TEAM_NAME_MAP)


def apply_global_filters(
    df: pd.DataFrame,
    filters: Dict[str, Any],
    sort_year_wise: bool = True,
    apply_compound: bool = False
) -> pd.DataFrame:
    """
    Universal multi-dataset filter and Year-wise sorter.
    Dynamically filters any DataFrame by selected Year, Team Name, Driver, Grand Prix,
    and optionally Tyre Compound, then sorts Year-wise.
    """
    if df is None or df.empty:
        return df

    out = df.copy()

    # 1. Year Filter
    sel_year = filters.get("selected_year", "All Years")
    if sel_year and str(sel_year) != "All Years":
        try:
            yr_val = int(str(sel_year).strip()[:4])
            for yc in ["Year", "year", "Season", "season"]:
                if yc in out.columns:
                    out = out[pd.to_numeric(out[yc], errors="coerce") == yr_val]
                    break
        except ValueError:
            pass

    # 2. Team / Constructor Filter
    sel_team = filters.get("selected_team", "All Teams")
    if sel_team and sel_team != "All Teams":
        team_cols = [c for c in ["TeamName", "Team", "Constructor", "team", "constructorName", "constructor"] if c in out.columns]
        if team_cols:
            tc = team_cols[0]
            norm_col = normalize_team_series(out[tc])
            norm_target = TEAM_NAME_MAP.get(sel_team, sel_team)
            mask = (norm_col.str.lower() == norm_target.lower()) | (
                norm_col.str.lower().str.contains(re.escape(sel_team.lower()), na=False)
            )
            out = out[mask]

    # 3. Driver Filter
    sel_drivers = filters.get("selected_drivers", ["All Drivers"])
    if isinstance(sel_drivers, str):
        sel_drivers = [sel_drivers]

    if sel_drivers and "All Drivers" not in sel_drivers:
        target_names = set()
        target_codes = set()
        for item in sel_drivers:
            item_str = str(item).strip()
            # Handle format "Max Verstappen (VER)" or "VER" or "Max Verstappen"
            m = re.match(r"^(.*?)\s*\(([A-Z]{3})\)$", item_str)
            if m:
                full_n, code_n = m.group(1).strip(), m.group(2).strip().upper()
                target_names.add(full_n.lower())
                target_codes.add(code_n)
            elif len(item_str) == 3 and item_str.isupper():
                target_codes.add(item_str)
                if item_str in DRIVER_CODE_TO_FULLNAME:
                    target_names.add(DRIVER_CODE_TO_FULLNAME[item_str].lower())
            else:
                target_names.add(item_str.lower())
                for k_code, v_name in DRIVER_CODE_TO_FULLNAME.items():
                    if v_name.lower() == item_str.lower():
                        target_codes.add(k_code)

        drv_cols = [
            c for c in [
                "FullName", "Driver", "Abbreviation", "driver", "driverName",
                "driver_name", "DriverCode", "code", "driver_code", "Winner", "winner_name"
            ]
            if c in out.columns
        ]
        if drv_cols:
            mask = pd.Series(False, index=out.index)
            for dc in drv_cols:
                s_str = out[dc].astype(str).str.strip()
                mask = mask | s_str.str.upper().isin(target_codes) | s_str.str.lower().isin(target_names)
            out = out[mask]

    # 4. Grand Prix / Event Filter
    sel_event = filters.get("selected_event", "All Events")
    if sel_event and sel_event != "All Events":
        ev_cols = [
            c for c in ["EventName", "Grand Prix", "grand_prix", "race_name", "Race Name", "name", "Circuit", "circuit_name"]
            if c in out.columns
        ]
        if ev_cols:
            ec = ev_cols[0]
            out = out[out[ec].astype(str).str.lower().str.contains(re.escape(sel_event.lower()), na=False)]

    # 5. Optional Tyre Compound Filter
    if apply_compound:
        sel_comp = filters.get("selected_compound", "ALL")
        if sel_comp and sel_comp != "ALL":
            comp_cols = [
                c for c in ["Compound", "Tire Compound", "tyre_compound", "compound", "StartingCompound", "starting_compound"]
                if c in out.columns
            ]
            if comp_cols:
                cc = comp_cols[0]
                out = out[out[cc].astype(str).str.upper() == sel_comp.upper()]

    # 6. Year-Wise Sorting
    if sort_year_wise and not out.empty:
        if "year_sort_desc" in filters:
            year_Order_asc = not bool(filters["year_sort_desc"])
        else:
            year_Order_asc = bool(filters.get("year_sort_ascending", False))
        sort_cols = []
        asc_flags = []
        for yc in ["Year", "year", "Season", "season"]:
            if yc in out.columns:
                sort_cols.append(yc)
                asc_flags.append(year_Order_asc)
                break
        for rc in ["RoundNumber", "Round", "round", "round_number"]:
            if rc in out.columns:
                sort_cols.append(rc)
                asc_flags.append(True)
                break
        for pc in ["Position", "finish_position", "position", "LapNumber", "lap_number"]:
            if pc in out.columns and pc not in sort_cols:
                sort_cols.append(pc)
                asc_flags.append(True)
                break
        if sort_cols:
            try:
                out = out.sort_values(sort_cols, ascending=asc_flags).reset_index(drop=True)
            except Exception:
                pass

    return out


def build_driver_strategy_summary(laps_df: pd.DataFrame, results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes tyre stints and pit stop strategies for each driver in each race.
    Supports both single-season and multi-season (Year) DataFrames without row multiplication.
    """
    if laps_df.empty or results_df.empty:
        return pd.DataFrame()

    has_year = ("Year" in laps_df.columns) and ("Year" in results_df.columns)
    join_keys = ["Year", "RoundNumber", "DriverNumber"] if has_year else ["RoundNumber", "DriverNumber"]

    # Ensure join keys exist
    if not set(join_keys).issubset(laps_df.columns) or not set(join_keys).issubset(results_df.columns):
        return pd.DataFrame()

    stint_group_keys = join_keys + ["Stint"]

    stint_summary = (
        laps_df.dropna(subset=["Stint"])
        .groupby(stint_group_keys)
        .agg(
            Compound=("Compound", lambda s: s.mode().iloc[0] if not s.empty else "UNKNOWN"),
            StintLength=("LapNumber", "count"),
            AvgStintLapSec=("LapTimeSec", "mean"),
            MinLapSec=("LapTimeSec", "min")
        )
        .reset_index()
    )

    if stint_summary.empty:
        return pd.DataFrame()

    def summarize_driver_race(group):
        group = group.sort_values("Stint")
        compounds = list(group["Compound"])
        stint_counts = len(compounds)
        strategy_str = " -> ".join(compounds)
        total_stint_laps = group["StintLength"].sum()
        pit_stops_count = max(0, stint_counts - 1)
        return pd.Series({
            "StintCount": stint_counts,
            "PitStopsCount": pit_stops_count,
            "CompoundSequence": strategy_str,
            "StartingCompound": compounds[0] if compounds else "UNKNOWN",
            "FinalCompound": compounds[-1] if compounds else "UNKNOWN",
            "StrategyType": f"{pit_stops_count}-Stop" if pit_stops_count <= 3 else "Multi-Stop",
            "TotalTrackLaps": total_stint_laps
        })

    race_strategies = (
        stint_summary.groupby(join_keys)
        .apply(summarize_driver_race)
        .reset_index()
    )

    merged = results_df.merge(
        race_strategies,
        on=join_keys,
        how="left"
    )

    clean_laps = laps_df[~laps_df.get("IsOutlierLap", False) & (laps_df["LapTimeSec"] > 0)]
    if not clean_laps.empty:
        pace_summary = (
            clean_laps.groupby(join_keys)["LapTimeSec"]
            .agg(CleanAvgLapSec="mean", FastestCleanLapSec="min", PaceStdDevSec="std")
            .reset_index()
        )
        merged = merged.merge(pace_summary, on=join_keys, how="left")

    return merged


def integrate_weather_with_races(results_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    """Attaches average ambient & track temperatures and rainfall flags to race results."""
    if weather_df.empty or results_df.empty:
        return results_df

    join_keys = ["Year", "RoundNumber"] if ("Year" in weather_df.columns and "Year" in results_df.columns) else ["RoundNumber"]
    if not set(join_keys).issubset(weather_df.columns) or not set(join_keys).issubset(results_df.columns):
        return results_df

    weather_agg = (
        weather_df.groupby(join_keys)
        .agg(
            AvgAirTemp=("AirTemp", "mean"),
            AvgTrackTemp=("TrackTemp", "mean"),
            MaxTrackTemp=("TrackTemp", "max"),
            AvgHumidity=("Humidity", "mean"),
            AvgWindSpeed=("WindSpeed", "mean"),
            RainfallRecorded=("Rainfall", lambda x: bool(x.any()))
        )
        .reset_index()
    )

    return results_df.merge(weather_agg, on=join_keys, how="left")


def compute_undercut_overcut_candidates(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies potential undercut and overcut attempts where two cars pitted within 1-3 laps
    of each other and swapped track position.
    """
    if laps_df.empty or "LapNumber" not in laps_df.columns or "IsPitLap" not in laps_df.columns:
        return pd.DataFrame()

    pit_laps = laps_df[laps_df["IsPitLap"].fillna(False)].copy()
    if pit_laps.empty:
        return pd.DataFrame()

    candidates = []
    group_cols = ["Year", "RoundNumber"] if "Year" in pit_laps.columns else ["RoundNumber"]

    for grp_key, r_df in pit_laps.groupby(group_cols):
        yr = grp_key[0] if isinstance(grp_key, tuple) else 2023
        rnd = grp_key[1] if isinstance(grp_key, tuple) else grp_key
        event_name = r_df["EventName"].iloc[0] if "EventName" in r_df.columns else f"Round {rnd}"
        drivers_pitted = r_df.sort_values("LapNumber")
        for i in range(len(drivers_pitted)):
            d1 = drivers_pitted.iloc[i]
            for j in range(i + 1, min(i + 4, len(drivers_pitted))):
                d2 = drivers_pitted.iloc[j]
                lap_diff = d2["LapNumber"] - d1["LapNumber"]
                if 1 <= lap_diff <= 3 and d1["Driver"] != d2["Driver"]:
                    candidates.append({
                        "Year": int(yr) if pd.notna(yr) else 2023,
                        "RoundNumber": int(rnd) if pd.notna(rnd) else 1,
                        "EventName": event_name,
                        "FirstPitter": d1["Driver"],
                        "FirstPitLap": int(d1["LapNumber"]),
                        "FirstCompound": d1.get("Compound", "UNKNOWN"),
                        "SecondPitter": d2["Driver"],
                        "SecondPitLap": int(d2["LapNumber"]),
                        "SecondCompound": d2.get("Compound", "UNKNOWN"),
                        "LapDelta": int(lap_diff),
                        "StrategyAttempt": "Undercut Attempt" if lap_diff >= 1 else "Overcut Attempt"
                    })

    out_df = pd.DataFrame(candidates)
    if not out_df.empty and "Year" in out_df.columns:
        out_df = out_df.sort_values(["Year", "RoundNumber", "FirstPitLap"], ascending=[False, True, True]).reset_index(drop=True)
    return out_df
