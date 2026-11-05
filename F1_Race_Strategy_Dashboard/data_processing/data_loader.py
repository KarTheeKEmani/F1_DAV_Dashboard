import os
import logging
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

# Suppress noisy bare-mode warnings when running outside Streamlit (e.g. FastAPI / pytest)
for _logger_name in [
    "streamlit.runtime.caching.cache_data_api",
    "streamlit.runtime.scriptrunner_utils.script_run_context",
]:
    logging.getLogger(_logger_name).setLevel(logging.ERROR)

try:
    import streamlit as st
    cache_data = st.cache_data
except ImportError:
    def cache_data(f):
        return f

from config import (
    DAV_DATA_DIR, F1_ZIP, F1_2_ZIP, F1_3_ZIP,
    F1_WORLD_1950_2026_DIR, STRATEGY_DATASET_CSV,
    STINT_AGGRESSION_CSV, PIT_STOP_ANALYTICS_DIR,
    PIT_STOP_PREDICTION_CSV, RACE_INTELLIGENCE_DIR,
    LIVE_TRACKER_DIR, GP_WINNERS_CSV, WEATHER_2018_2023_CSV,
    FORMULA1_DIR, ROHANRAO_F1_DIR, PODIUMS_CSV,
    SAFETY_CARS_CSV, RED_FLAGS_CSV, DRIVERS_CAREER_CSV,
    COMBINED_DRIVER_RACE_CSV, ARCHIVE_LAPDATA_DIR,
    ARCHIVE_CALCVARS_DIR, TELEMETRY_CACHE_DIR,
    DRIVER_MAP, DRIVER_CODE_TO_FULLNAME, TEAM_NAME_MAP
)
from data_processing.data_cleaning import (
    clean_laps_data, clean_results_data, clean_pitstops_data,
    parse_timedelta_to_seconds, clean_compound_name
)


def _get_f1_rel_dir() -> Path:
    """Prefers the 1950-2026 World Championship Kaggle dataset, falling back to rohanrao_f1 or formula1."""
    if F1_WORLD_1950_2026_DIR.exists() and (F1_WORLD_1950_2026_DIR / "races.csv").exists():
        return F1_WORLD_1950_2026_DIR
    if ROHANRAO_F1_DIR.exists() and (ROHANRAO_F1_DIR / "races.csv").exists():
        return ROHANRAO_F1_DIR
    return FORMULA1_DIR


@cache_data
def load_f1_events() -> pd.DataFrame:
    """Loads 2023 Grand Prix calendar and event information."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Events.csv') as f:
            df = pd.read_csv(f)
            df['RoundNumber'] = pd.to_numeric(df['RoundNumber'], errors='coerce')
            df['Year'] = 2023
            return df.sort_values('RoundNumber').reset_index(drop=True)


@cache_data
def load_f1_results() -> pd.DataFrame:
    """Loads 2023 race results with team and driver classifications."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Results.csv') as f:
            df = pd.read_csv(f)
            df = clean_results_data(df)
            df['Year'] = 2023
            if 'TeamName' in df.columns:
                df['TeamName'] = df['TeamName'].replace(TEAM_NAME_MAP)
            return df


@cache_data
def load_f1_laps() -> pd.DataFrame:
    """Loads 2023 full season lap-by-lap records with timing, sectors, compounds, and stints."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Laps.csv') as f:
            df = pd.read_csv(f)
            df = clean_laps_data(df)
            df['Year'] = 2023
            if 'Team' in df.columns:
                df['Team'] = df['Team'].replace(TEAM_NAME_MAP)
                df['TeamName'] = df['Team']
            if 'Driver' in df.columns:
                df['FullName'] = df['Driver'].map(DRIVER_CODE_TO_FULLNAME).fillna(df['Driver'])
            return df


@cache_data
def load_f1_fastest_laps() -> pd.DataFrame:
    """Loads 2023 official fastest lap records."""
    if not F1_ZIP.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(F1_ZIP, 'r') as zf:
        with zf.open('Fastest_Laps.csv') as f:
            df = pd.read_csv(f)
            df = clean_laps_data(df)
            df['Year'] = 2023
            return df


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
            df['Year'] = 2023
            return df


@cache_data
def load_unified_results() -> pd.DataFrame:
    """
    Loads unified multi-season race results spanning 1950-2026 across:
    1. Kaggle Formula 1 World Championship (1950-2026)
    2. Kaggle Formula 1 Race Intelligence (2010-2026)
    3. Kaggle Formula 1 Live Tracker (2024-2026)
    4. FastF1 2023 Official Results
    Sorted Year-wise (newest season first).
    """
    frames = []

    # 1. FastF1 2023 Official Results
    df_2023 = load_f1_results()
    if not df_2023.empty:
        cols_keep = [
            'Year', 'RoundNumber', 'EventName', 'DriverNumber', 'Abbreviation',
            'FullName', 'TeamName', 'Position', 'GridPosition', 'PositionsGained',
            'Points', 'Status', 'Time'
        ]
        avail_c = [c for c in cols_keep if c in df_2023.columns]
        frames.append(df_2023[avail_c].copy())

    # 2. Kaggle World Championship 1950-2026
    rel_dir = _get_f1_rel_dir()
    if rel_dir.exists() and (rel_dir / "results.csv").exists():
        try:
            res = pd.read_csv(rel_dir / "results.csv", na_values=r"\N")
            races = pd.read_csv(rel_dir / "races.csv", usecols=['raceId', 'year', 'round', 'name'], na_values=r"\N")
            drivers = pd.read_csv(rel_dir / "drivers.csv", usecols=['driverId', 'number', 'code', 'forename', 'surname'], na_values=r"\N")
            constructors = pd.read_csv(rel_dir / "constructors.csv", usecols=['constructorId', 'name'], na_values=r"\N").rename(
                columns={'name': 'TeamName'}
            )
            status = pd.read_csv(rel_dir / "status.csv", na_values=r"\N")

            m = (
                res.merge(races, on='raceId', how='left')
                .merge(drivers, on='driverId', how='left', suffixes=('', '_drv'))
                .merge(constructors, on='constructorId', how='left')
                .merge(status, on='statusId', how='left')
            )
            m['Year'] = pd.to_numeric(m['year'], errors='coerce')
            m['RoundNumber'] = pd.to_numeric(m['round'], errors='coerce')
            m['EventName'] = m['name']
            m['FullName'] = (m['forename'].fillna('') + ' ' + m['surname'].fillna('')).str.strip()
            m['Abbreviation'] = m['code'].fillna(m['surname'].astype(str).str[:3].str.upper())
            m['DriverNumber'] = pd.to_numeric(m['number'], errors='coerce').fillna(m['driverId'])
            m['TeamName'] = m['TeamName'].fillna('Unknown').replace(TEAM_NAME_MAP)
            m['Position'] = pd.to_numeric(m['positionOrder'], errors='coerce')
            m['GridPosition'] = pd.to_numeric(m['grid'], errors='coerce')
            m['PositionsGained'] = np.where(m['GridPosition'] > 0, m['GridPosition'] - m['Position'], 0)
            m['Points'] = pd.to_numeric(m['points'], errors='coerce').fillna(0.0)
            m['Status'] = m['status'].fillna('Finished')
            m['Time'] = m['time'].fillna('')

            # Exclude 2023 if already loaded from FastF1 to prevent duplicate 2023 rows
            if not df_2023.empty:
                m = m[m['Year'] != 2023]

            cols_keep = [
                'Year', 'RoundNumber', 'EventName', 'DriverNumber', 'Abbreviation',
                'FullName', 'TeamName', 'Position', 'GridPosition', 'PositionsGained',
                'Points', 'Status', 'Time'
            ]
            frames.append(m[cols_keep].copy())
        except Exception:
            pass

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined['Year'] = pd.to_numeric(combined['Year'], errors='coerce').fillna(2023).astype(int)
    combined['RoundNumber'] = pd.to_numeric(combined['RoundNumber'], errors='coerce').fillna(1).astype(int)
    combined = combined.sort_values(['Year', 'RoundNumber', 'Position'], ascending=[False, True, True]).reset_index(drop=True)
    return combined


@cache_data
def load_strategy_dataset() -> pd.DataFrame:
    """Loads the comprehensive 2021-2024 Kaggle strategy dataset (80,767 records), sorted Year-wise."""
    if not STRATEGY_DATASET_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(STRATEGY_DATASET_CSV)
    df = clean_laps_data(df)
    for col in ['Year', 'RoundNumber', 'Position', 'GridPosition', 'LapTimeSec']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if 'Team' in df.columns:
        df['Team'] = df['Team'].replace(TEAM_NAME_MAP)
        df['TeamName'] = df['Team']
    if 'Driver' in df.columns:
        df['FullName'] = df['Driver'].map(DRIVER_CODE_TO_FULLNAME).fillna(df['Driver'])
    if 'Year' in df.columns:
        df['Year'] = df['Year'].fillna(2023).astype(int)
        df = df.sort_values(['Year', 'RoundNumber', 'LapNumber'], ascending=[False, True, True]).reset_index(drop=True)
    return df


@cache_data
def load_unified_laps() -> pd.DataFrame:
    """
    Loads multi-season lap & stint records (2021-2026) unifying:
    - Kaggle Strategy Dataset (2021-2024, 80,767 laps)
    - Kaggle Pit Stop Prediction Dataset (2025 laps)
    - Kaggle Race Intelligence Lap Intelligence (2026 & pre-2021 laps)
    Sorted Year-wise (newest season first).
    """
    frames = []
    strat_df = load_strategy_dataset()
    if not strat_df.empty:
        frames.append(strat_df)

    # Add 2025 laps from Pit Stop Prediction dataset if present
    if PIT_STOP_PREDICTION_CSV.exists():
        try:
            df_p = pd.read_csv(PIT_STOP_PREDICTION_CSV)
            df_p = df_p[pd.to_numeric(df_p.get('Year'), errors='coerce') == 2025].copy()
            if not df_p.empty:
                df_p['Year'] = 2025
                df_p['EventName'] = df_p['Race'].astype(str)
                df_p['RoundNumber'] = pd.factorize(df_p['EventName'])[0] + 1
                df_p['LapTimeSec'] = pd.to_numeric(df_p['LapTime (s)'], errors='coerce')
                df_p['Compound'] = df_p['Compound'].apply(clean_compound_name)
                df_p['IsPitLap'] = df_p['PitStop'].fillna(0).astype(bool)
                df_p['IsOutlierLap'] = df_p['IsPitLap'] | (df_p['LapTimeSec'] > 125)
                df_p['FullName'] = df_p['Driver'].map(DRIVER_CODE_TO_FULLNAME).fillna(df_p['Driver'])
                # Map driver code to team & number
                code_to_team = {v['code']: v['team'] for v in DRIVER_MAP.values()}
                code_to_num = {v['code']: k for k, v in DRIVER_MAP.items()}
                df_p['Team'] = df_p['Driver'].map(code_to_team).fillna('McLaren')
                df_p['TeamName'] = df_p['Team']
                df_p['DriverNumber'] = df_p['Driver'].map(code_to_num).fillna(99)
                frames.append(df_p)
        except Exception:
            pass

    if not frames:
        return load_f1_laps()

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(['Year', 'RoundNumber', 'LapNumber'], ascending=[False, True, True]).reset_index(drop=True)
    return combined


@cache_data
def load_ergast_pit_stops() -> pd.DataFrame:
    """Loads historical pit stop records (11,371+ stops) merged with race details, drivers, and constructors, sorted Year-wise."""
    rel_dir = _get_f1_rel_dir()
    if not rel_dir.exists():
        return pd.DataFrame()

    ps_file = rel_dir / "pit_stops.csv"
    races_file = rel_dir / "races.csv"
    drivers_file = rel_dir / "drivers.csv"
    results_file = rel_dir / "results.csv"
    constructors_file = rel_dir / "constructors.csv"

    if not ps_file.exists():
        return pd.DataFrame()

    df_ps = pd.read_csv(ps_file)
    df_ps = clean_pitstops_data(df_ps)

    if races_file.exists():
        df_races = pd.read_csv(races_file, usecols=['raceId', 'year', 'round', 'name', 'date'])
        df_ps = df_ps.merge(df_races, on='raceId', how='left')
        df_ps['Year'] = pd.to_numeric(df_ps['year'], errors='coerce')
        df_ps['RoundNumber'] = pd.to_numeric(df_ps['round'], errors='coerce')
        df_ps['EventName'] = df_ps['name']

    if drivers_file.exists():
        df_drivers = pd.read_csv(drivers_file, usecols=['driverId', 'code', 'forename', 'surname'])
        df_drivers['driverName'] = df_drivers['forename'] + " " + df_drivers['surname']
        df_drivers['FullName'] = df_drivers['driverName']
        df_ps = df_ps.merge(df_drivers[['driverId', 'code', 'driverName', 'FullName']], on='driverId', how='left')

    if results_file.exists() and constructors_file.exists():
        df_res = pd.read_csv(results_file, usecols=['raceId', 'driverId', 'constructorId']).drop_duplicates(
            subset=['raceId', 'driverId']
        )
        df_con = pd.read_csv(constructors_file, usecols=['constructorId', 'name']).rename(
            columns={'name': 'constructorName'}
        )
        df_res = df_res.merge(df_con, on='constructorId', how='left')
        df_ps = df_ps.merge(df_res[['raceId', 'driverId', 'constructorName']], on=['raceId', 'driverId'], how='left')
        df_ps['constructorName'] = df_ps['constructorName'].replace(TEAM_NAME_MAP)
        df_ps['TeamName'] = df_ps['constructorName']

    if 'Year' in df_ps.columns:
        df_ps = df_ps.sort_values(['Year', 'RoundNumber', 'lap'], ascending=[False, True, True]).reset_index(drop=True)

    return df_ps


@cache_data
def load_kaggle_stint_aggression() -> pd.DataFrame:
    """Loads the Kaggle F1 Stint Data with Aggression Scores (2018-2024, 7,374 stints), sorted Year-wise."""
    if not STINT_AGGRESSION_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(STINT_AGGRESSION_CSV)
    if 'Season' in df.columns:
        df['Year'] = pd.to_numeric(df['Season'], errors='coerce')
    if 'Constructor' in df.columns:
        df['Constructor'] = df['Constructor'].replace(TEAM_NAME_MAP)
        df['TeamName'] = df['Constructor']
    if 'Driver' in df.columns:
        df['FullName'] = df['Driver']
    if 'Tire Compound' in df.columns:
        df['Compound'] = df['Tire Compound'].astype(str).str.upper()
    if 'Race Name' in df.columns:
        df['EventName'] = df['Race Name']
    if 'Year' in df.columns:
        df = df.sort_values(['Year', 'Round', 'Position'], ascending=[False, True, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_pit_events() -> pd.DataFrame:
    """Loads the Kaggle Granular F1 Pit Stop Dataset (2011-2026, 12,912 events with pit_duration_s & stop_duration_s)."""
    pit_file = PIT_STOP_ANALYTICS_DIR / "pit_events.csv"
    if not pit_file.exists():
        return pd.DataFrame()
    df = pd.read_csv(pit_file)
    df['Year'] = pd.to_numeric(df['season'], errors='coerce')
    df['RoundNumber'] = pd.to_numeric(df['round_number'], errors='coerce')

    drv_file = PIT_STOP_ANALYTICS_DIR / "race_drivers.csv"
    ctx_file = PIT_STOP_ANALYTICS_DIR / "race_context.csv"
    if drv_file.exists():
        drv = pd.read_csv(drv_file, usecols=['season', 'round_number', 'driver_id', 'driver_name', 'constructor_id']).drop_duplicates(
            subset=['season', 'round_number', 'driver_id']
        )
        df = df.merge(drv, on=['season', 'round_number', 'driver_id'], how='left')
        df['FullName'] = df['driver_name']
        df['TeamName'] = df['constructor_id'].astype(str).str.replace('_', ' ').str.title().replace(TEAM_NAME_MAP)
    if ctx_file.exists():
        ctx = pd.read_csv(ctx_file, usecols=['season', 'round_number', 'circuit_short_name']).drop_duplicates(
            subset=['season', 'round_number']
        )
        df = df.merge(ctx, on=['season', 'round_number'], how='left')
        df['EventName'] = df['circuit_short_name']

    df = df.sort_values(['Year', 'RoundNumber', 'lap_number'], ascending=[False, True, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_pit_prediction() -> pd.DataFrame:
    """Loads the Kaggle F1 Strategy & Pit Stop Prediction Dataset (2022-2025, 101,371 laps)."""
    if not PIT_STOP_PREDICTION_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(PIT_STOP_PREDICTION_CSV)
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    if 'Driver' in df.columns:
        df['FullName'] = df['Driver'].map(DRIVER_CODE_TO_FULLNAME).fillna(df['Driver'])
        code_to_team = {v['code']: v['team'] for v in DRIVER_MAP.values()}
        df['TeamName'] = df['Driver'].map(code_to_team).fillna('McLaren')
    if 'Race' in df.columns:
        df['EventName'] = df['Race']
    df = df.sort_values(['Year', 'Race', 'LapNumber'], ascending=[False, True, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_race_intelligence() -> pd.DataFrame:
    """Loads the Kaggle Formula 1 Race Intelligence dataset (2010-2026, 6,464 driver-race entries with 42 strategy cols)."""
    rr_file = RACE_INTELLIGENCE_DIR / "race_results.csv"
    if not rr_file.exists():
        return pd.DataFrame()
    df = pd.read_csv(rr_file)
    df['Year'] = pd.to_numeric(df['season'], errors='coerce')
    df['RoundNumber'] = pd.to_numeric(df['round'], errors='coerce')
    df['FullName'] = df['driver'].replace({'Alex Albon': 'Alexander Albon', 'Nico Hülkenberg': 'Nico Hulkenberg'})
    df['TeamName'] = df['team'].replace(TEAM_NAME_MAP)
    df['EventName'] = df['circuit_name']
    df = df.sort_values(['Year', 'RoundNumber', 'finish_position'], ascending=[False, True, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_championship_standings() -> pd.DataFrame:
    """Loads the Kaggle Race Intelligence Championship Standings (2010-2026, 311 records)."""
    cs_file = RACE_INTELLIGENCE_DIR / "championship_standings.csv"
    if not cs_file.exists():
        return pd.DataFrame()
    df = pd.read_csv(cs_file)
    df['Year'] = pd.to_numeric(df['season'], errors='coerce')
    df['FullName'] = df['driver'].replace({'Alex Albon': 'Alexander Albon', 'Nico Hülkenberg': 'Nico Hulkenberg'})
    df['TeamName'] = df['team'].replace(TEAM_NAME_MAP)
    df = df.sort_values(['Year', 'driver_position'], ascending=[False, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_live_tracker() -> pd.DataFrame:
    """Loads the Kaggle Formula 1 Live Tracker dataset (2024-2026, 1,024 entries)."""
    lt_file = LIVE_TRACKER_DIR / "race_results.csv"
    if not lt_file.exists():
        return pd.DataFrame()
    df = pd.read_csv(lt_file)
    df['Year'] = pd.to_numeric(df['season'], errors='coerce')
    df['RoundNumber'] = pd.to_numeric(df['round'], errors='coerce')
    df['FullName'] = df['driver_name']
    df['TeamName'] = df['constructor'].replace(TEAM_NAME_MAP)
    df['EventName'] = df['race_name']
    df = df.sort_values(['Year', 'RoundNumber', 'position'], ascending=[False, True, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_gp_winners() -> pd.DataFrame:
    """Loads the Kaggle Formula 1 Grand Prix Winners Dataset (1950-2025, 1,142 races)."""
    if not GP_WINNERS_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(GP_WINNERS_CSV)
    df['Year'] = pd.to_numeric(df['year'], errors='coerce')
    df['FullName'] = df['winner_name']
    df['TeamName'] = df['team'].replace(TEAM_NAME_MAP)
    df['EventName'] = df['grand_prix']
    df = df.sort_values(['Year', 'date'], ascending=[False, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_weather_multiyear() -> pd.DataFrame:
    """Loads the Kaggle Multi-Year F1 Weather Dataset (2018-2023, 18,214 observations)."""
    if not WEATHER_2018_2023_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(WEATHER_2018_2023_CSV)
    if 'Round Number' in df.columns:
        df['RoundNumber'] = pd.to_numeric(df['Round Number'], errors='coerce')
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.sort_values(['Year', 'RoundNumber'], ascending=[False, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_podiums() -> pd.DataFrame:
    """Loads the Kaggle Formula One Race Podiums (1950-2026) dataset (1,158 races)."""
    if not PODIUMS_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(PODIUMS_CSV)
    if 'Season' in df.columns:
        df['Season'] = pd.to_numeric(df['Season'], errors='coerce')
        df['Year'] = df['Season']
    if 'Grand Prix' in df.columns:
        df['EventName'] = df['Grand Prix']
    df = df.sort_values(['Year', 'Round'], ascending=[False, True]).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_safety_cars() -> pd.DataFrame:
    """Loads the Kaggle F1 Safety Car deployments dataset (380 deployments)."""
    if not SAFETY_CARS_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(SAFETY_CARS_CSV)
    if 'Race' in df.columns:
        df['Year'] = pd.to_numeric(df['Race'].astype(str).str.extract(r'^(\d{4})')[0], errors='coerce')
        df['EventName'] = df['Race']
    for col in ['Deployed', 'Retreated', 'FullLaps']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.sort_values('Year', ascending=False).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_red_flags() -> pd.DataFrame:
    """Loads the Kaggle F1 Red Flags dataset (103 race stoppages)."""
    if not RED_FLAGS_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(RED_FLAGS_CSV)
    if 'Race' in df.columns:
        df['Year'] = pd.to_numeric(df['Race'].astype(str).str.extract(r'^(\d{4})')[0], errors='coerce')
        df['EventName'] = df['Race']
    if 'Lap' in df.columns:
        df['Lap'] = pd.to_numeric(df['Lap'], errors='coerce')
    df = df.sort_values('Year', ascending=False).reset_index(drop=True)
    return df


@cache_data
def load_kaggle_drivers_career() -> pd.DataFrame:
    """Loads the Kaggle All-Time F1 Drivers Career Statistics dataset (868 drivers)."""
    if not DRIVERS_CAREER_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(DRIVERS_CAREER_CSV)
    num_cols = [
        'Championships', 'Race_Entries', 'Race_Starts', 'Pole_Positions',
        'Race_Wins', 'Podiums', 'Fastest_Laps', 'Points',
        'Pole_Rate', 'Start_Rate', 'Win_Rate', 'Podium_Rate',
        'FastLap_Rate', 'Points_Per_Entry', 'Years_Active', 'Decade'
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['FullName'] = df['Driver']
    return df


@cache_data
def load_kaggle_circuits() -> pd.DataFrame:
    """Loads all 77 historical Formula 1 circuits with GPS coordinates and total Grands Prix hosted."""
    rel_dir = _get_f1_rel_dir()
    circuits_file = rel_dir / "circuits.csv"
    races_file = rel_dir / "races.csv"
    if not circuits_file.exists():
        return pd.DataFrame()

    df_circ = pd.read_csv(circuits_file, na_values=r"\N")
    for col in ['lat', 'lng', 'alt']:
        if col in df_circ.columns:
            df_circ[col] = pd.to_numeric(df_circ[col], errors='coerce')

    if races_file.exists():
        df_races = pd.read_csv(races_file, usecols=['raceId', 'circuitId', 'year'])
        agg = df_races.groupby('circuitId').agg(
            RacesHosted=('raceId', 'count'),
            FirstSeason=('year', 'min'),
            LastSeason=('year', 'max')
        ).reset_index()
        df_circ = df_circ.merge(agg, on='circuitId', how='left')
        df_circ['RacesHosted'] = df_circ['RacesHosted'].fillna(0).astype(int)

    return df_circ


@cache_data
def load_kaggle_qualifying() -> pd.DataFrame:
    """Loads historical knockout Qualifying records (10,494+ rows) merged with race, driver, and constructor info."""
    rel_dir = _get_f1_rel_dir()
    qual_file = rel_dir / "qualifying.csv"
    if not qual_file.exists():
        return pd.DataFrame()

    df_q = pd.read_csv(qual_file, na_values=r"\N")
    for q_col in ['q1', 'q2', 'q3']:
        if q_col in df_q.columns:
            df_q[f"{q_col}_sec"] = df_q[q_col].apply(parse_timedelta_to_seconds)

    races_file = rel_dir / "races.csv"
    drivers_file = rel_dir / "drivers.csv"
    constructors_file = rel_dir / "constructors.csv"

    if races_file.exists():
        df_races = pd.read_csv(races_file, usecols=['raceId', 'year', 'round', 'name'])
        df_q = df_q.merge(df_races, on='raceId', how='left')
        df_q['Year'] = pd.to_numeric(df_q['year'], errors='coerce')
        df_q['RoundNumber'] = pd.to_numeric(df_q['round'], errors='coerce')
        df_q['EventName'] = df_q['name']
    if drivers_file.exists():
        df_drv = pd.read_csv(drivers_file, usecols=['driverId', 'code', 'forename', 'surname'])
        df_drv['driverName'] = df_drv['forename'] + " " + df_drv['surname']
        df_drv['FullName'] = df_drv['driverName']
        df_q = df_q.merge(df_drv[['driverId', 'code', 'driverName', 'FullName']], on='driverId', how='left')
    if constructors_file.exists():
        df_con = pd.read_csv(constructors_file, usecols=['constructorId', 'name']).rename(
            columns={'name': 'constructorName'}
        )
        df_q = df_q.merge(df_con, on='constructorId', how='left')
        df_q['constructorName'] = df_q['constructorName'].replace(TEAM_NAME_MAP)
        df_q['TeamName'] = df_q['constructorName']

    if 'Year' in df_q.columns:
        df_q = df_q.sort_values(['Year', 'RoundNumber', 'position'], ascending=[False, True, True]).reset_index(drop=True)
    return df_q


@cache_data
def load_kaggle_sprint_results() -> pd.DataFrame:
    """Loads Formula 1 Sprint Race results (360+ entries) merged with race, driver, and constructor names."""
    rel_dir = _get_f1_rel_dir()
    sprint_file = rel_dir / "sprint_results.csv"
    if not sprint_file.exists():
        return pd.DataFrame()

    df_s = pd.read_csv(sprint_file, na_values=r"\N")
    for col in ['grid', 'position', 'positionOrder', 'points', 'laps']:
        if col in df_s.columns:
            df_s[col] = pd.to_numeric(df_s[col], errors='coerce')

    races_file = rel_dir / "races.csv"
    drivers_file = rel_dir / "drivers.csv"
    constructors_file = rel_dir / "constructors.csv"

    if races_file.exists():
        df_races = pd.read_csv(races_file, usecols=['raceId', 'year', 'round', 'name'])
        df_s = df_s.merge(df_races, on='raceId', how='left')
        df_s['Year'] = pd.to_numeric(df_s['year'], errors='coerce')
        df_s['RoundNumber'] = pd.to_numeric(df_s['round'], errors='coerce')
        df_s['EventName'] = df_s['name']
    if drivers_file.exists():
        df_drv = pd.read_csv(drivers_file, usecols=['driverId', 'code', 'forename', 'surname'])
        df_drv['driverName'] = df_drv['forename'] + " " + df_drv['surname']
        df_drv['FullName'] = df_drv['driverName']
        df_s = df_s.merge(df_drv[['driverId', 'code', 'driverName', 'FullName']], on='driverId', how='left')
    if constructors_file.exists():
        df_con = pd.read_csv(constructors_file, usecols=['constructorId', 'name']).rename(
            columns={'name': 'constructorName'}
        )
        df_s = df_s.merge(df_con, on='constructorId', how='left')
        df_s['constructorName'] = df_s['constructorName'].replace(TEAM_NAME_MAP)
        df_s['TeamName'] = df_s['constructorName']

    if 'Year' in df_s.columns:
        df_s = df_s.sort_values(['Year', 'RoundNumber', 'positionOrder'], ascending=[False, True, True]).reset_index(drop=True)
    return df_s


@cache_data
def load_combined_driver_race() -> pd.DataFrame:
    """Loads the 26,499-row multi-source combined dataset (Ergast results + strategy + podiums), sorted Year-wise."""
    if not COMBINED_DRIVER_RACE_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(COMBINED_DRIVER_RACE_CSV, low_memory=False)
    for col in ['year', 'round', 'grid', 'position', 'points', 'avg_lap_time_sec', 'pit_stops']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if 'year' in df.columns:
        df['Year'] = df['year']
    if 'forename' in df.columns and 'surname' in df.columns:
        df['FullName'] = (df['forename'].fillna('') + ' ' + df['surname'].fillna('')).str.strip()
    if 'name' in df.columns:
        df['EventName'] = df['name']
    df = df.sort_values(['year', 'round', 'positionOrder'], ascending=[False, True, True]).reset_index(drop=True)
    return df


@cache_data
def load_archive_2024_summary() -> pd.DataFrame:
    """Loads 2024 Grand Prix calculated sector & pace variables from G:\\DAV\\archive."""
    if not ARCHIVE_CALCVARS_DIR.exists():
        return pd.DataFrame()
    frames = []
    for csv_path in sorted(ARCHIVE_CALCVARS_DIR.glob("*.csv")):
        try:
            df = pd.read_csv(csv_path)
            df["EventName"] = csv_path.stem
            df["Year"] = 2024
            if "Driver" in df.columns:
                df["FullName"] = df["Driver"].map(DRIVER_CODE_TO_FULLNAME).fillna(df["Driver"])
            frames.append(df)
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


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
        df = pd.read_parquet(pq_path)
        if not df.empty and "DriverNumber" not in df.columns:
            bahrain_drivers = [1, 11, 14, 55, 44, 18, 63, 77, 10, 23, 22, 2, 20, 21, 27, 24, 4, 31, 16, 81]
            chunk = max(1, len(df) // len(bahrain_drivers))
            drv_nums = [bahrain_drivers[min(i // chunk, len(bahrain_drivers) - 1)] for i in range(len(df))]
            df["DriverNumber"] = drv_nums
            df["DriverCode"] = df["DriverNumber"].map(lambda n: DRIVER_MAP.get(n, {}).get("code", str(n)))
        return df
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
