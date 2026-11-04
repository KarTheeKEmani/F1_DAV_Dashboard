import os
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

try:
    import streamlit as st
    cache_data = st.cache_data
except ImportError:
    # Fallback decorator if run outside streamlit
    def cache_data(f):
        return f

from config import (
    DAV_DATA_DIR, F1_ZIP, F1_2_ZIP, F1_3_ZIP,
    STRATEGY_DATASET_CSV, FORMULA1_DIR, TELEMETRY_CACHE_DIR,
    DRIVER_MAP
)
from data_processing.data_cleaning import (
    clean_laps_data, clean_results_data, clean_pitstops_data
)


@cache_data
def load_f1_events() -> pd.DataFrame:
    """Loads 2023 Grand Prix calendar and event information."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Events.csv') as f:
            df = pd.read_csv(f)
            df['RoundNumber'] = pd.to_numeric(df['RoundNumber'], errors='coerce')
            return df.sort_values('RoundNumber').reset_index(drop=True)


@cache_data
def load_f1_results() -> pd.DataFrame:
    """Loads 2023 race results with team and driver classifications."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Results.csv') as f:
            df = pd.read_csv(f)
            return clean_results_data(df)


@cache_data
def load_f1_laps() -> pd.DataFrame:
    """Loads 2023 full season lap-by-lap records with timing, sectors, compounds, and stints."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Laps.csv') as f:
            df = pd.read_csv(f)
            return clean_laps_data(df)


@cache_data
def load_f1_fastest_laps() -> pd.DataFrame:
    """Loads 2023 official fastest lap records."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Fastest_Laps.csv') as f:
            df = pd.read_csv(f)
            return clean_laps_data(df)


@cache_data
def load_f1_weather() -> pd.DataFrame:
    """Loads 2023 weather conditions (AirTemp, TrackTemp, Humidity, Rainfall)."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Weather.csv') as f:
            df = pd.read_csv(f)
            for col in ['AirTemp', 'TrackTemp', 'Humidity', 'Pressure', 'WindSpeed', 'RoundNumber']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df


@cache_data
def load_strategy_dataset() -> pd.DataFrame:
    """Loads the comprehensive 2021-2024 strategy dataset (80,767 records)."""
    if not STRATEGY_DATASET_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(STRATEGY_DATASET_CSV)
    df = clean_laps_data(df)
    for col in ['Year', 'RoundNumber', 'Position', 'GridPosition', 'LapTimeSec']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


@cache_data
def load_ergast_pit_stops() -> pd.DataFrame:
    """Loads historical pit stop records merged with race details and driver names."""
    if not FORMULA1_DIR.exists():
        return pd.DataFrame()
    
    ps_file = FORMULA1_DIR / "pit_stops.csv"
    races_file = FORMULA1_DIR / "races.csv"
    drivers_file = FORMULA1_DIR / "drivers.csv"

    if not ps_file.exists():
        return pd.DataFrame()

    df_ps = pd.read_csv(ps_file)
    df_ps = clean_pitstops_data(df_ps)

    if races_file.exists():
        df_races = pd.read_csv(races_file, usecols=['raceId', 'year', 'round', 'name', 'date'])
        df_ps = df_ps.merge(df_races, on='raceId', how='left')

    if drivers_file.exists():
        df_drivers = pd.read_csv(drivers_file, usecols=['driverId', 'code', 'forename', 'surname'])
        df_drivers['driverName'] = df_drivers['forename'] + " " + df_drivers['surname']
        df_ps = df_ps.merge(df_drivers[['driverId', 'code', 'driverName']], on='driverId', how='left')

    return df_ps


@cache_data
def load_fastest_laps_telemetry() -> pd.DataFrame:
    """Loads extracted fastest laps telemetry traces across all rounds."""
    pq_path = TELEMETRY_CACHE_DIR / "fastest_laps_telemetry.parquet"
    if pq_path.exists():
        return pd.read_parquet(pq_path)
    return pd.DataFrame()


@cache_data
def load_round1_telemetry() -> pd.DataFrame:
    """Loads Round 1 Bahrain telemetry for all 20 drivers."""
    pq_path = TELEMETRY_CACHE_DIR / "telemetry_round1.parquet"
    if pq_path.exists():
        return pd.read_parquet(pq_path)
    return pd.DataFrame()


@cache_data
def load_tweets_sample(n_rows: int = 5000) -> pd.DataFrame:
    """Loads a sample of fan tweets from F1 3.zip for sentiment analysis."""
    if not F1_3_ZIP.exists():
        return pd.DataFrame()
    try:
        with zipfile.ZipFile(F1_3_ZIP, 'r') as zf:
            with zf.open('F1_tweets.csv') as f:
                df = pd.read_csv(f, nrows=n_rows)
                return df
    except Exception:
        return pd.DataFrame()


@cache_data
def load_game_weather_sample(n_rows: int = 5000) -> pd.DataFrame:
    """Loads sample game weather/telemetry packets from F1 2.zip."""
    if not F1_2_ZIP.exists():
        return pd.DataFrame()
    try:
        with zipfile.ZipFile(F1_2_ZIP, 'r') as zf:
            with zf.open('weather.csv') as f:
                df = pd.read_csv(f, nrows=n_rows)
                return df
    except Exception:
        return pd.DataFrame()
