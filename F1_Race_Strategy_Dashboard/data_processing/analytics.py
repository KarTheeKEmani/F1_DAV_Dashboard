from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd


def calculate_tyre_degradation(laps_df: pd.DataFrame, compound: Optional[str] = None) -> pd.DataFrame:
    """
    Estimates tyre degradation by calculating the slope of LapTimeSec vs TyreLife.
    Filters out outlier laps, pit in/out laps, and first laps to isolate true tyre wear.
    """
    if laps_df.empty or 'TyreLife' not in laps_df.columns or 'LapTimeSec' not in laps_df.columns:
        return pd.DataFrame()

    # Filter for clean, representative green-flag laps
    clean = laps_df[
        (~laps_df.get('IsOutlierLap', False)) &
        (laps_df['TyreLife'] > 1) &
        (laps_df['TyreLife'] < 45) &
        (laps_df['LapTimeSec'] > 50) &
        (laps_df['LapTimeSec'] < 140)
    ].copy()

    if compound and compound != "ALL":
        clean = clean[clean['Compound'] == compound]

    if clean.empty:
        return pd.DataFrame()

    results = []
    # Calculate degradation rate per compound
    for comp, group in clean.groupby('Compound'):
        if len(group) < 15:
            continue
        # Linear regression slope: seconds per lap
        x = group['TyreLife'].values
        y = group['LapTimeSec'].values
        slope, intercept = np.polyfit(x, y, 1)
        r_corr = np.corrcoef(x, y)[0, 1] if len(x) > 2 else 0.0

        results.append({
            'Compound': comp,
            'SampleLaps': len(group),
            'DegradationSecPerLap': round(float(slope), 4),
            'BaseLapTimeSec': round(float(intercept), 3),
            'Correlation': round(float(r_corr), 3),
            'MedianTyreLife': round(float(group['TyreLife'].median()), 1),
            'MaxTyreLife': int(group['TyreLife'].max())
        })

    return pd.DataFrame(results)


def calculate_pitstop_strategy_impact(strategy_summary_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes statistical relationships between pit stop counts, stint strategies,
    and race finishing positions.
    """
    if strategy_summary_df.empty:
        return {}

    valid = strategy_summary_df.dropna(subset=['Position', 'PitStopsCount']).copy()
    valid['Position'] = pd.to_numeric(valid['Position'], errors='coerce')
    valid = valid[valid['Position'].notna() & (valid['Position'] > 0)]

    if valid.empty:
        return {}

    # Correlation
    corr = valid['PitStopsCount'].corr(valid['Position'])

    # Position stats by strategy type
    strat_perf = (
        valid.groupby('StrategyType')
        .agg(
            DriverCount=('DriverNumber', 'count'),
            AvgFinishingPosition=('Position', 'mean'),
            MedianPosition=('Position', 'median'),
            PodiumsCount=('Position', lambda p: (p <= 3).sum()),
            WinsCount=('Position', lambda p: (p == 1).sum()),
            PointsScored=('Points', 'sum') if 'Points' in valid.columns else ('Position', 'count')
        )
        .reset_index()
    )

    # Strategy by starting tyre compound
    starting_perf = (
        valid.groupby('StartingCompound')
        .agg(
            Count=('DriverNumber', 'count'),
            AvgPosition=('Position', 'mean'),
            Podiums=('Position', lambda p: (p <= 3).sum()),
            Wins=('Position', lambda p: (p == 1).sum())
        )
        .reset_index()
    )

    return {
        'correlation_pitstops_position': round(float(corr), 3) if not np.isnan(corr) else 0.0,
        'strategy_performance': strat_perf,
        'starting_compound_performance': starting_perf,
        'total_evaluated_drivers': len(valid)
    }


def compute_pitstop_team_rankings(pitstops_df: pd.DataFrame, results_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Ranks team/driver pit crews by median duration, fastest pit stops, and consistency."""
    if pitstops_df.empty:
        return pd.DataFrame()

    clean_ps = pitstops_df.copy()
    if 'IsCleanPitStop' in clean_ps.columns:
        clean_ps = clean_ps[clean_ps['IsCleanPitStop']]

    if 'DurationSec' not in clean_ps.columns:
        return pd.DataFrame()

    clean_ps = clean_ps.dropna(subset=['DurationSec'])
    if clean_ps.empty:
        return pd.DataFrame()

    group_col = 'code' if 'code' in clean_ps.columns else 'driverId'
    agg_dict = {
        'TotalStops': ('DurationSec', 'count'),
        'FastestStopSec': ('DurationSec', 'min'),
        'MedianStopSec': ('DurationSec', 'median'),
        'AvgStopSec': ('DurationSec', 'mean'),
        'StdDevSec': ('DurationSec', 'std')
    }
    if 'constructorName' in clean_ps.columns:
        agg_dict['Constructor'] = ('constructorName', lambda s: s.dropna().mode().iloc[0] if not s.dropna().empty else 'Multiple')

    summary = clean_ps.groupby(group_col).agg(**agg_dict).reset_index()
    summary = summary.sort_values('MedianStopSec').reset_index(drop=True)
    summary['Rank'] = summary.index + 1
    return summary


def calculate_driver_consistency(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes driver lap time consistency (standard deviation and coefficient of variation)
    on clean representative laps.
    """
    if laps_df.empty or 'LapTimeSec' not in laps_df.columns:
        return pd.DataFrame()

    clean = laps_df[
        (~laps_df.get('IsOutlierLap', False)) &
        (laps_df['LapTimeSec'] > 50) &
        (laps_df['LapTimeSec'] < 140)
    ].copy()

    if clean.empty:
        return pd.DataFrame()

    metrics = (
        clean.groupby(['Driver', 'Team'])['LapTimeSec']
        .agg(
            TotalLaps='count',
            MedianLapSec='median',
            MeanLapSec='mean',
            StdDevSec='std',
            BestLapSec='min'
        )
        .reset_index()
    )

    # Coefficient of variation (CV = std / mean * 100)
    metrics['ConsistencyCV'] = (metrics['StdDevSec'] / metrics['MeanLapSec'] * 100).round(2)
    metrics = metrics.sort_values('ConsistencyCV').reset_index(drop=True)
    return metrics


def calculate_teammate_comparison(results_df: pd.DataFrame) -> pd.DataFrame:
    """Calculates head-to-head qualifying and race finishing positions between teammates."""
    if results_df.empty or 'TeamName' not in results_df.columns:
        return pd.DataFrame()

    results = []
    for team, group in results_df.groupby('TeamName'):
        drivers = group['Abbreviation'].unique()
        if len(drivers) == 2:
            d1, d2 = drivers[0], drivers[1]
            races_common = group.groupby('RoundNumber').filter(lambda r: len(r['Abbreviation'].unique()) == 2)
            
            d1_wins = 0
            d2_wins = 0
            d1_points = group[group['Abbreviation'] == d1]['Points'].sum()
            d2_points = group[group['Abbreviation'] == d2]['Points'].sum()

            for rnd, r_grp in races_common.groupby('RoundNumber'):
                p1_row = r_grp[r_grp['Abbreviation'] == d1]
                p2_row = r_grp[r_grp['Abbreviation'] == d2]
                if not p1_row.empty and not p2_row.empty:
                    p1 = p1_row['Position'].iloc[0]
                    p2 = p2_row['Position'].iloc[0]
                    if not pd.isna(p1) and not pd.isna(p2):
                        if p1 < p2:
                            d1_wins += 1
                        elif p2 < p1:
                            d2_wins += 1

            results.append({
                'Team': team,
                'Driver1': d1,
                'Driver2': d2,
                'Driver1_Wins': d1_wins,
                'Driver2_Wins': d2_wins,
                'Driver1_Points': d1_points,
                'Driver2_Points': d2_points,
                'TotalCommonRaces': d1_wins + d2_wins
            })

    return pd.DataFrame(results)


def simulate_race_strategy(
    total_laps: int = 57,
    strategies: Optional[Any] = None,
    base_lap_sec: float = 93.0,
    pit_loss_sec: float = 21.5,
    deg_slopes: Optional[Dict[str, float]] = None,
    compound_offsets: Optional[Dict[str, float]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Simulates lap-by-lap race progression and total race time for competing tyre strategies.
    Accounts for compound base pace deltas, tyre wear degradation, and pit-lane time loss.
    Supports both keyword arguments and positional (total_laps, base_lap_sec, pit_loss_sec).
    Returns (lap_progression_df, strategy_summary_df).
    """
    # Handle positional calls like simulate_race_strategy(57, 92.5, 21.5)
    if isinstance(strategies, (int, float)):
        pit_loss_sec = float(base_lap_sec) if base_lap_sec != 93.0 else pit_loss_sec
        base_lap_sec = float(strategies)
        strategies = None

    if deg_slopes is None:
        deg_slopes = {"SOFT": 0.115, "MEDIUM": 0.065, "HARD": 0.038, "INTERMEDIATE": 0.050, "WET": 0.040}
    if compound_offsets is None:
        compound_offsets = {"SOFT": -1.0, "MEDIUM": -0.5, "HARD": 0.0, "INTERMEDIATE": 2.5, "WET": 5.0}

    if strategies is None:
        strategies = [
            {
                "name": "1-Stop: Medium -> Hard",
                "stints": [
                    {"compound": "MEDIUM", "laps": int(total_laps * 0.40)},
                    {"compound": "HARD", "laps": total_laps - int(total_laps * 0.40)}
                ]
            },
            {
                "name": "2-Stop: Soft -> Medium -> Hard",
                "stints": [
                    {"compound": "SOFT", "laps": int(total_laps * 0.25)},
                    {"compound": "MEDIUM", "laps": int(total_laps * 0.35)},
                    {"compound": "HARD", "laps": total_laps - int(total_laps * 0.25) - int(total_laps * 0.35)}
                ]
            },
            {
                "name": "2-Stop: Medium -> Hard -> Soft",
                "stints": [
                    {"compound": "MEDIUM", "laps": int(total_laps * 0.35)},
                    {"compound": "HARD", "laps": int(total_laps * 0.40)},
                    {"compound": "SOFT", "laps": total_laps - int(total_laps * 0.35) - int(total_laps * 0.40)}
                ]
            }
        ]

    lap_records = []
    summary_records = []

    for strat in strategies:
        strat_name = strat["name"]
        stints = strat["stints"]
        current_lap = 1
        cum_time = 0.0
        pit_stops_count = max(0, len(stints) - 1)

        for stint_idx, stint in enumerate(stints):
            comp = stint["compound"].upper()
            stint_laps = stint["laps"]
            slope = deg_slopes.get(comp, 0.05)
            offset = compound_offsets.get(comp, 0.0)

            for tyre_age in range(1, stint_laps + 1):
                if current_lap > total_laps:
                    break
                # Lap time model: base + offset + degradation
                lap_time = base_lap_sec + offset + (tyre_age * slope)
                # Fuel burn-off effect: car gets ~0.032s faster per lap as fuel is consumed
                fuel_advantage = (current_lap - 1) * 0.032
                net_lap_time = lap_time - fuel_advantage

                # If this is the in-lap of a stint before another stint, add pit loss
                is_pit_lap = (tyre_age == stint_laps and stint_idx < len(stints) - 1)
                effective_time = net_lap_time + (pit_loss_sec if is_pit_lap else 0.0)
                cum_time += effective_time

                lap_records.append({
                    "Strategy": strat_name,
                    "LapNumber": current_lap,
                    "Stint": stint_idx + 1,
                    "Compound": comp,
                    "TyreAge": tyre_age,
                    "LapTimeSec": round(net_lap_time, 3),
                    "CumulativeTimeSec": round(cum_time, 2),
                    "IsPitLap": is_pit_lap
                })
                current_lap += 1

        summary_records.append({
            "Strategy": strat_name,
            "TotalPitStops": pit_stops_count,
            "TotalRaceTimeSec": round(cum_time, 2),
            "AvgLapTimeSec": round(cum_time / total_laps, 3)
        })

    lap_df = pd.DataFrame(lap_records)
    summary_df = pd.DataFrame(summary_records).sort_values("TotalRaceTimeSec").reset_index(drop=True)
    best_time = summary_df["TotalRaceTimeSec"].min()
    summary_df["DeltaToFastestSec"] = (summary_df["TotalRaceTimeSec"] - best_time).round(2)
    summary_df["Rank"] = summary_df.index + 1

    return lap_df, summary_df


def analyze_safety_car_and_red_flags(
    safety_cars_df: pd.DataFrame,
    red_flags_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Analyzes historical Safety Car deployments (380 events) and Red Flag stoppages (103 events)
    from the Kaggle F1 Race Events dataset.
    """
    out: Dict[str, Any] = {
        "total_safety_cars": len(safety_cars_df),
        "total_red_flags": len(red_flags_df),
        "avg_sc_full_laps": 0.0,
        "causes_breakdown": pd.DataFrame(),
        "sc_by_decade": pd.DataFrame(),
    }
    if not safety_cars_df.empty:
        if "FullLaps" in safety_cars_df.columns:
            out["avg_sc_full_laps"] = round(float(safety_cars_df["FullLaps"].dropna().mean()), 2)
        if "Cause" in safety_cars_df.columns:
            causes = (
                safety_cars_df["Cause"]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .value_counts()
                .head(10)
                .reset_index()
            )
            causes.columns = ["Cause", "Deployments"]
            out["causes_breakdown"] = causes
        if "Year" in safety_cars_df.columns:
            sc_yr = safety_cars_df.dropna(subset=["Year"]).copy()
            sc_yr["Decade"] = (sc_yr["Year"].astype(int) // 10 * 10).astype(str) + "s"
            by_dec = sc_yr.groupby("Decade").agg(
                Deployments=("Race", "count"),
                AvgLaps=("FullLaps", "mean")
            ).reset_index()
            out["sc_by_decade"] = by_dec

    return out


def analyze_multi_year_strategy_warehouse(
    combined_df: pd.DataFrame,
    strategy_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Computes multi-season (2021-2024 & 1950-2024) strategy insights across the 26,499-row
    combined warehouse and 80,767-row Kaggle strategy dataset.
    """
    out: Dict[str, Any] = {
        "grid_to_finish": pd.DataFrame(),
        "pitstops_vs_finish_multiyear": pd.DataFrame(),
        "season_compound_pace": pd.DataFrame(),
    }

    if not combined_df.empty and {"grid", "position"}.issubset(combined_df.columns):
        valid_gf = combined_df.dropna(subset=["grid", "position"]).copy()
        valid_gf = valid_gf[(valid_gf["grid"] >= 1) & (valid_gf["grid"] <= 20) & (valid_gf["position"] >= 1)]
        if not valid_gf.empty:
            gf_summary = (
                valid_gf.groupby("grid")
                .agg(
                    Races=("position", "count"),
                    AvgFinish=("position", "mean"),
                    WinRatePct=("position", lambda s: round((s == 1).mean() * 100, 2)),
                    PodiumRatePct=("position", lambda s: round((s <= 3).mean() * 100, 2)),
                )
                .reset_index()
            )
            out["grid_to_finish"] = gf_summary

        if "pit_stops" in combined_df.columns:
            valid_ps = combined_df.dropna(subset=["pit_stops", "position"]).copy()
            valid_ps = valid_ps[(valid_ps["pit_stops"] >= 1) & (valid_ps["pit_stops"] <= 5)]
            if not valid_ps.empty:
                ps_summary = (
                    valid_ps.groupby("pit_stops")
                    .agg(
                        DriverRaces=("position", "count"),
                        AvgFinish=("position", "mean"),
                        AvgPoints=("points", "mean"),
                        AvgSafetyCarLaps=("safety_car_laps", "mean") if "safety_car_laps" in valid_ps.columns else ("position", "count"),
                    )
                    .reset_index()
                )
                out["pitstops_vs_finish_multiyear"] = ps_summary

    if not strategy_df.empty and {"Year", "Compound", "LapTimeSec"}.issubset(strategy_df.columns):
        clean_s = strategy_df[
            (strategy_df["LapTimeSec"] > 55) &
            (strategy_df["LapTimeSec"] < 135) &
            (strategy_df["Compound"].isin(["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]))
        ]
        if not clean_s.empty:
            comp_pace = (
                clean_s.groupby(["Year", "Compound"])
                .agg(
                    LapsCount=("LapTimeSec", "count"),
                    MeanLapSec=("LapTimeSec", "mean"),
                    MedianLapSec=("LapTimeSec", "median"),
                    MeanTyreLife=("TyreLife", "mean") if "TyreLife" in clean_s.columns else ("LapTimeSec", "count"),
                )
                .reset_index()
            )
            out["season_compound_pace"] = comp_pace

    return out


def analyze_all_time_drivers_and_podiums(
    drivers_career_df: pd.DataFrame,
    podiums_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Computes historical driver efficiency leaders (868 drivers) and podium winners (1950-2026).
    """
    out: Dict[str, Any] = {
        "top_winners_career": pd.DataFrame(),
        "podium_leaders_1950_2026": pd.DataFrame(),
        "top_circuits_hosted": pd.DataFrame(),
    }

    if not drivers_career_df.empty and "Race_Wins" in drivers_career_df.columns:
        top_w = (
            drivers_career_df[drivers_career_df["Race_Starts"] >= 15]
            .sort_values(["Race_Wins", "Pole_Positions", "Podiums"], ascending=False)
            .head(25)
            .copy()
        )
        for rate_col in ["Win_Rate", "Pole_Rate", "Podium_Rate"]:
            if rate_col in top_w.columns:
                top_w[f"{rate_col}_Pct"] = (top_w[rate_col] * 100).round(1)
        out["top_winners_career"] = top_w

    if not podiums_df.empty and "Winner" in podiums_df.columns:
        winners = podiums_df["Winner"].value_counts().head(15).reset_index()
        winners.columns = ["Driver", "GrandPrixWins"]
        out["podium_leaders_1950_2026"] = winners

        if "Circuit" in podiums_df.columns:
            circuits = podiums_df["Circuit"].value_counts().head(15).reset_index()
            circuits.columns = ["Circuit", "PodiumRacesHosted"]
            out["top_circuits_hosted"] = circuits

    return out
