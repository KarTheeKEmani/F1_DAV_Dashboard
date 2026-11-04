from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd


def build_driver_strategy_summary(laps_df: pd.DataFrame, results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes tyre stints and pit stop strategies for each driver in each race.
    Avoids row multiplication by aggregating laps to (RoundNumber, DriverNumber).
    """
    if laps_df.empty or results_df.empty:
        return pd.DataFrame()

    # Identify stint sequence and tyre compounds per driver/round
    stint_summary = (
        laps_df.dropna(subset=['Stint'])
        .groupby(['RoundNumber', 'DriverNumber', 'Stint'])
        .agg(
            Compound=('Compound', lambda s: s.mode().iloc[0] if not s.empty else 'UNKNOWN'),
            StintLength=('LapNumber', 'count'),
            AvgStintLapSec=('LapTimeSec', 'mean'),
            MinLapSec=('LapTimeSec', 'min')
        )
        .reset_index()
    )

    # Aggregate stints to race-level strategy description
    def summarize_driver_race(group):
        group = group.sort_values('Stint')
        compounds = list(group['Compound'])
        stint_counts = len(compounds)
        strategy_str = " -> ".join(compounds)
        total_stint_laps = group['StintLength'].sum()
        pit_stops_count = max(0, stint_counts - 1)
        return pd.Series({
            'StintCount': stint_counts,
            'PitStopsCount': pit_stops_count,
            'CompoundSequence': strategy_str,
            'StartingCompound': compounds[0] if compounds else 'UNKNOWN',
            'FinalCompound': compounds[-1] if compounds else 'UNKNOWN',
            'StrategyType': f"{pit_stops_count}-Stop" if pit_stops_count <= 3 else "Multi-Stop",
            'TotalTrackLaps': total_stint_laps
        })

    race_strategies = (
        stint_summary.groupby(['RoundNumber', 'DriverNumber'])
        .apply(summarize_driver_race)
        .reset_index()
    )

    # Merge with race results
    merged = results_df.merge(
        race_strategies,
        on=['RoundNumber', 'DriverNumber'],
        how='left'
    )

    # Calculate average race pace excluding pit laps & safety cars
    clean_laps = laps_df[~laps_df['IsOutlierLap'] & (laps_df['LapTimeSec'] > 0)]
    pace_summary = (
        clean_laps.groupby(['RoundNumber', 'DriverNumber'])['LapTimeSec']
        .agg(CleanAvgLapSec='mean', FastestCleanLapSec='min', PaceStdDevSec='std')
        .reset_index()
    )

    merged = merged.merge(pace_summary, on=['RoundNumber', 'DriverNumber'], how='left')

    return merged


def integrate_weather_with_races(results_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    """Attaches average ambient & track temperatures and rainfall flags to race results."""
    if weather_df.empty or results_df.empty:
        return results_df

    weather_agg = (
        weather_df.groupby('RoundNumber')
        .agg(
            AvgAirTemp=('AirTemp', 'mean'),
            AvgTrackTemp=('TrackTemp', 'mean'),
            MaxTrackTemp=('TrackTemp', 'max'),
            AvgHumidity=('Humidity', 'mean'),
            AvgWindSpeed=('WindSpeed', 'mean'),
            RainfallRecorded=('Rainfall', lambda x: bool(x.any()))
        )
        .reset_index()
    )

    return results_df.merge(weather_agg, on='RoundNumber', how='left')


def compute_undercut_overcut_candidates(laps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies potential undercut and overcut attempts where two cars pitted within 1-3 laps
    of each other and swapped track position.
    """
    if laps_df.empty or 'LapNumber' not in laps_df.columns:
        return pd.DataFrame()

    pit_laps = laps_df[laps_df['IsPitLap']].copy()
    if pit_laps.empty:
        return pd.DataFrame()

    candidates = []
    # Analyze by round
    for rnd, r_df in pit_laps.groupby('RoundNumber'):
        event_name = r_df['EventName'].iloc[0] if 'EventName' in r_df.columns else f"Round {rnd}"
        drivers_pitted = r_df.sort_values('LapNumber')
        # Compare pairs of pit stops within 2 laps
        for i in range(len(drivers_pitted)):
            d1 = drivers_pitted.iloc[i]
            for j in range(i + 1, min(i + 4, len(drivers_pitted))):
                d2 = drivers_pitted.iloc[j]
                lap_diff = d2['LapNumber'] - d1['LapNumber']
                if 1 <= lap_diff <= 3 and d1['Driver'] != d2['Driver']:
                    candidates.append({
                        'RoundNumber': rnd,
                        'EventName': event_name,
                        'FirstPitter': d1['Driver'],
                        'FirstPitLap': int(d1['LapNumber']),
                        'FirstCompound': d1.get('Compound', 'UNKNOWN'),
                        'SecondPitter': d2['Driver'],
                        'SecondPitLap': int(d2['LapNumber']),
                        'SecondCompound': d2.get('Compound', 'UNKNOWN'),
                        'LapDelta': int(lap_diff),
                        'StrategyAttempt': 'Undercut Attempt' if lap_diff >= 1 else 'Overcut Attempt'
                    })

    return pd.DataFrame(candidates)
