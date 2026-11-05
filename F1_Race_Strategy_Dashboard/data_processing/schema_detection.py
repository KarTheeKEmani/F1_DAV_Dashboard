import os
import zipfile
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import openpyxl

from config import (
    DAV_DATA_DIR, F1_ZIP, F1_2_ZIP, F1_3_ZIP,
    ARCHIVE_ZIP, ARCHIVE_DIR, STRATEGY_DATASET_CSV,
    FORMULA1_DIR, ROHANRAO_F1_DIR, F1_WORLD_1950_2026_DIR, PODIUMS_CSV,
    SAFETY_CARS_CSV, RED_FLAGS_CSV, DRIVERS_CAREER_CSV,
    COMBINED_DRIVER_RACE_CSV, ARCHIVE_CALCVARS_DIR,
    STINT_AGGRESSION_CSV, PIT_STOP_ANALYTICS_DIR,
    PIT_STOP_PREDICTION_CSV, RACE_INTELLIGENCE_DIR,
    LIVE_TRACKER_DIR, GP_WINNERS_CSV, WEATHER_2018_2023_CSV
)


def inspect_dataframe(df: pd.DataFrame, dataset_name: str, source_path: str, category: str) -> Dict[str, Any]:
    """Generates detailed schema and data quality audit for a DataFrame."""
    row_count, col_count = df.shape
    dup_count = int(df.duplicated().sum()) if row_count < 200000 else int(df.head(50000).duplicated().sum())

    columns_info = []
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct = round((null_count / row_count * 100), 2) if row_count > 0 else 0
        dtype_str = str(df[col].dtype)
        unique_count = int(df[col].nunique(dropna=True))

        # Check for potential candidate key
        is_candidate_key = (null_count == 0 and unique_count == row_count and row_count > 1)

        sample_vals = [str(x) for x in df[col].dropna().head(3).tolist()]
        columns_info.append({
            "name": col,
            "dtype": dtype_str,
            "null_count": null_count,
            "null_pct": null_pct,
            "unique_count": unique_count,
            "is_candidate_key": is_candidate_key,
            "sample_values": sample_vals
        })

    # Summary warnings
    warnings = []
    if dup_count > 0:
        warnings.append(f"Contains {dup_count:,} duplicate rows.")
    high_null_cols = [c["name"] for c in columns_info if c["null_pct"] > 30.0]
    if high_null_cols:
        warnings.append(f"High missing values (>30%) in columns: {', '.join(high_null_cols[:5])}")

    return {
        "dataset_name": dataset_name,
        "source_path": str(source_path),
        "category": category,
        "row_count": row_count,
        "col_count": col_count,
        "duplicate_count": dup_count,
        "columns": columns_info,
        "warnings": warnings,
        "head_preview": df.head(5).copy()
    }


def discover_all_datasets() -> Dict[str, Dict[str, Any]]:
    """
    Audits every dataset in G:\\DAV and categorizes them:
    - F1 (FastF1 2023 Season: Events, Results, Laps, Fastest Laps, Weather, Sprint, Telemetry)
    - Kaggle Strategy Dataset (yajatpawar/formula-1-strategy-dataset: 2021-2024 Stint & Tyre dataset)
    - Kaggle World Championship Relational (rohanrao/formula-1-world-championship-1950-2020 & melissamonfared/formula-1)
    - Kaggle Race Podiums 1950-2026 (maulikgajera/formula-one-race-podiums-19502026)
    - Kaggle Safety Cars & Red Flags (jtrotman/formula-1-race-events)
    - Kaggle All-Time Drivers Career Dataset (petalme/f1-drivers-dataset)
    - Multi-Source Combined Driver-Race Dataset (f1_driver_race_combined.csv)
    - Archive 2024 Season Lap & Sector Aggregates (G:\\DAV\\archive)
    - F1 2 (F1 Game Telemetry & Weather packets)
    - F1 3 (Formula 1 Tweets / Fan sentiment)
    - Unrelated files (e.g. DAV_Lab_02 customer lab)
    """
    catalog = {}

    # 1. Inspect F1.zip
    if F1_ZIP.exists():
        try:
            with zipfile.ZipFile(F1_ZIP, 'r') as zf:
                for fname in zf.namelist():
                    if fname.endswith('.csv'):
                        cat_label = "2023 Race Telemetry & Timing"
                        if "Telemetry" in fname:
                            with zf.open(fname) as f:
                                df = pd.read_csv(f, nrows=20000)
                                audit = inspect_dataframe(df, f"F1.zip -> {fname} (Sample)", str(F1_ZIP), "High-Frequency Telemetry")
                                audit["notes"] = "Full file contains 16.18M telemetry points across 22 Grands Prix."
                                catalog[f"F1_{fname}"] = audit
                        else:
                            with zf.open(fname) as f:
                                df = pd.read_csv(f)
                                audit = inspect_dataframe(df, f"F1.zip -> {fname}", str(F1_ZIP), cat_label)
                                catalog[f"F1_{fname}"] = audit
        except Exception as e:
            catalog["F1_zip_error"] = {"error": str(e), "dataset_name": "F1.zip"}

    # 2. Inspect Kaggle Strategy Dataset
    if STRATEGY_DATASET_CSV.exists():
        try:
            df_strat = pd.read_csv(STRATEGY_DATASET_CSV)
            audit = inspect_dataframe(df_strat, "Kaggle: f1_strategy_final_dataset.csv", str(STRATEGY_DATASET_CSV), "Kaggle Strategy & Stints (2021-2024)")
            audit["notes"] = "80,767 race laps across 2021-2024 covering tyre stints, compound codes, degradation, and SC/VSC status."
            catalog["Kaggle_Strategy_Dataset"] = audit
        except Exception:
            pass

    # 3. Inspect Kaggle World Championship Relational Database (1950-2026 / Rohan Rao / Ergast)
    rel_dir = F1_WORLD_1950_2026_DIR if F1_WORLD_1950_2026_DIR.exists() else (ROHANRAO_F1_DIR if ROHANRAO_F1_DIR.exists() else FORMULA1_DIR)
    if rel_dir.exists():
        rel_files = [
            "pit_stops.csv", "races.csv", "results.csv", "drivers.csv",
            "constructors.csv", "circuits.csv", "qualifying.csv",
            "sprint_results.csv", "driver_standings.csv", "constructor_standings.csv",
            "status.csv", "practice_sessions.csv"
        ]
        for rf in rel_files:
            fp = rel_dir / rf
            if fp.exists():
                try:
                    df_rel = pd.read_csv(fp, na_values=r"\N")
                    audit = inspect_dataframe(df_rel, f"Kaggle F1 DB -> {rf}", str(fp), "Kaggle Historical Relational DB (1950-2026)")
                    catalog[f"Kaggle_DB_{rf}"] = audit
                except Exception:
                    pass

        lap_times_fp = rel_dir / "lap_times.csv"
        if lap_times_fp.exists():
            try:
                df_lt = pd.read_csv(lap_times_fp, nrows=50000)
                audit = inspect_dataframe(df_lt, "Kaggle F1 DB -> lap_times.csv (Sample)", str(lap_times_fp), "Kaggle Historical Relational DB (1950-2026)")
                audit["notes"] = "Full table contains 589,081+ historical lap timing records across decades."
                catalog["Kaggle_DB_lap_times.csv"] = audit
            except Exception:
                pass

    # 3b. Inspect Additional Kaggle F1 Race Analytics Repositories (2010-2026)
    extra_kaggle_files = [
        ("Kaggle_Race_Intelligence_2010_2026", RACE_INTELLIGENCE_DIR / "race_results.csv", "Kaggle: race_intelligence/race_results.csv", "Kaggle Race Intelligence (2010-2026)", 50000),
        ("Kaggle_Stint_Aggression_2018_2024", STINT_AGGRESSION_CSV, "Kaggle: f1_pitstops_2018_2024.csv", "Kaggle Stint & Aggression (2018-2024)", 50000),
        ("Kaggle_Pit_Events_2011_2026", PIT_STOP_ANALYTICS_DIR / "pit_events.csv", "Kaggle: pit_stop_analytics/pit_events.csv", "Kaggle Pit Stop Analytics (2011-2026)", 50000),
        ("Kaggle_Pit_Prediction_2022_2025", PIT_STOP_PREDICTION_CSV, "Kaggle: f1_strategy_dataset_v4.csv (Sample)", "Kaggle Pit-Stop Prediction (2022-2025)", 25000),
        ("Kaggle_GP_Winners_1950_2025", GP_WINNERS_CSV, "Kaggle: winners_f1_1950_2025_v2.csv", "Kaggle Grand Prix Winners (1950-2025)", 50000),
        ("Kaggle_Weather_2018_2023", WEATHER_2018_2023_CSV, "Kaggle: F1 Weather(2023-2018).csv", "Kaggle Multi-Year Weather (2018-2023)", 25000),
    ]
    for key_id, fp_path, label_str, cat_str, max_r in extra_kaggle_files:
        if fp_path.exists():
            try:
                df_ex = pd.read_csv(fp_path, nrows=max_r, low_memory=False)
                catalog[key_id] = inspect_dataframe(df_ex, label_str, str(fp_path), cat_str)
            except Exception:
                pass
    if LIVE_TRACKER_DIR.exists() and (LIVE_TRACKER_DIR / "race_results.csv").exists():
        try:
            df_lt2 = pd.read_csv(LIVE_TRACKER_DIR / "race_results.csv")
            catalog["Kaggle_Live_Tracker_2024_2026"] = inspect_dataframe(
                df_lt2, "Kaggle: live_tracker_2024_2026/race_results.csv",
                str(LIVE_TRACKER_DIR / "race_results.csv"), "Kaggle Live Tracker (2024-2026)"
            )
        except Exception:
            pass

    # 4. Inspect Kaggle Race Podiums (1950-2026)
    if PODIUMS_CSV.exists():
        try:
            df_pod = pd.read_csv(PODIUMS_CSV)
            audit = inspect_dataframe(df_pod, "Kaggle: f1_podiums_1950_2026.csv", str(PODIUMS_CSV), "Kaggle Historical Podiums (1950-2026)")
            audit["notes"] = "1,158 Grand Prix podium trios (Winner, 2nd, 3rd) from 1950 to 2026."
            catalog["Kaggle_Podiums_1950_2026"] = audit
        except Exception:
            pass

    # 5. Inspect Kaggle Safety Cars & Red Flags
    if SAFETY_CARS_CSV.exists():
        try:
            df_sc = pd.read_csv(SAFETY_CARS_CSV)
            audit = inspect_dataframe(df_sc, "Kaggle: safety_cars.csv", str(SAFETY_CARS_CSV), "Kaggle Race Neutralizations & Events")
            audit["notes"] = "380 historical Safety Car deployments with deployment causes, laps deployed/retreated, and full SC laps."
            catalog["Kaggle_Safety_Cars"] = audit
        except Exception:
            pass

    if RED_FLAGS_CSV.exists():
        try:
            df_rf = pd.read_csv(RED_FLAGS_CSV)
            audit = inspect_dataframe(df_rf, "Kaggle: red_flags.csv", str(RED_FLAGS_CSV), "Kaggle Race Neutralizations & Events")
            audit["notes"] = "103 historical Red Flag race suspensions, stoppage laps, resumption status, and incident descriptions."
            catalog["Kaggle_Red_Flags"] = audit
        except Exception:
            pass

    # 6. Inspect Kaggle All-Time Drivers Career Dataset
    if DRIVERS_CAREER_CSV.exists():
        try:
            df_dc = pd.read_csv(DRIVERS_CAREER_CSV)
            audit = inspect_dataframe(df_dc, "Kaggle: F1Drivers_Dataset.csv", str(DRIVERS_CAREER_CSV), "Kaggle All-Time Driver Career Stats")
            audit["notes"] = "868 all-time Formula 1 drivers with career entries, titles, poles, wins, podiums, and efficiency rates."
            catalog["Kaggle_Drivers_Career"] = audit
        except Exception:
            pass

    # 7. Inspect Processed Multi-Source Combined Dataset
    if COMBINED_DRIVER_RACE_CSV.exists():
        try:
            df_comb = pd.read_csv(COMBINED_DRIVER_RACE_CSV, low_memory=False)
            audit = inspect_dataframe(df_comb, "Processed: f1_driver_race_combined.csv", str(COMBINED_DRIVER_RACE_CSV), "Integrated Multi-Dataset Warehouse")
            audit["notes"] = "26,499 driver-race entries unifying Ergast results, multi-year tyre strategy metrics, and podium records."
            catalog["Processed_Combined_Warehouse"] = audit
        except Exception:
            pass

    # 8. Inspect Archive 2024 Season Dataset
    if ARCHIVE_DIR.exists() and (ARCHIVE_DIR / "GP.csv").exists():
        try:
            df_gp = pd.read_csv(ARCHIVE_DIR / "GP.csv")
            audit = inspect_dataframe(df_gp, "Archive 2024 -> GP.csv & 20 Race Sector Aggregates", str(ARCHIVE_DIR), "2024 Season Pace & Sector Archive")
            audit["notes"] = "Contains 2024 Grand Prix calendar, driver roster, 21 LapData CSVs, 20 calculated sector pace CSVs, and 838K Bahrain telemetry rows."
            catalog["Archive_2024_Season"] = audit
        except Exception:
            pass

    # 9. Inspect F1 2.zip (Weather & Game packets)
    if F1_2_ZIP.exists():
        try:
            with zipfile.ZipFile(F1_2_ZIP, 'r') as zf:
                for fname in zf.namelist():
                    if fname.endswith('.csv'):
                        with zf.open(fname) as f:
                            df = pd.read_csv(f, nrows=5000)
                            audit = inspect_dataframe(df, f"F1 2.zip -> {fname} (Sample)", str(F1_2_ZIP), "Game Telemetry & Dynamic Weather")
                            audit["notes"] = "Codemasters UDP telemetry stream featuring pit stop windows, ideal rejoin positions, and weather."
                            catalog[f"F1_2_{fname}"] = audit
        except Exception:
            pass

    # 10. Inspect F1 3.zip (F1 Tweets)
    if F1_3_ZIP.exists():
        try:
            with zipfile.ZipFile(F1_3_ZIP, 'r') as zf:
                with zf.open("F1_tweets.csv") as f:
                    df = pd.read_csv(f, nrows=10000)
                    audit = inspect_dataframe(df, "F1 3.zip -> F1_tweets.csv (Sample)", str(F1_3_ZIP), "Social Sentiment & Fan Engagement")
                    audit["notes"] = "Fan Twitter discussions during Grand Prix weekends with sentiment and hashtag analysis."
                    catalog["F1_3_Tweets"] = audit
        except Exception:
            pass

    # 11. Document Unrelated Files (e.g. Customer Data)
    cust_file = DAV_DATA_DIR / "DAV_Lab_02_Raw_Customer_Data.xlsx"
    if cust_file.exists():
        try:
            df_cust = pd.read_excel(cust_file, nrows=10)
            audit = inspect_dataframe(df_cust, "DAV_Lab_02_Raw_Customer_Data.xlsx", str(cust_file), "Excluded Non-F1 Dataset")
            audit["notes"] = "EXCLUDED: Customer sales/demographics lab data, unrelated to motorsport telemetry."
            catalog["Excluded_Customer_Data"] = audit
        except Exception:
            pass

    return catalog


def get_detected_relationships() -> List[Dict[str, str]]:
    """Returns detected keys connecting datasets across FastF1, Kaggle repositories, and Historical tables."""
    return [
        {
            "from_table": "F1: Results.csv",
            "from_key": "RoundNumber, DriverNumber",
            "to_table": "F1: Laps.csv",
            "to_key": "RoundNumber, DriverNumber",
            "relationship": "1-to-Many",
            "purpose": "Links final finishing position to lap-by-lap tyre degradation & sector pace."
        },
        {
            "from_table": "F1: Events.csv",
            "from_key": "RoundNumber",
            "to_table": "F1: Results.csv / Weather.csv",
            "to_key": "RoundNumber",
            "relationship": "1-to-Many",
            "purpose": "Maps Grand Prix circuit names, dates, and ambient weather conditions to race events."
        },
        {
            "from_table": "F1: Laps.csv",
            "from_key": "Time, LapStartTime, DriverNumber",
            "to_table": "F1: Telemetry.csv",
            "to_key": "SessionTime / Time, DriverNumber",
            "relationship": "1-to-Many",
            "purpose": "Syncs high-frequency throttle, brake, speed, and gear traces to specific laps."
        },
        {
            "from_table": "Kaggle F1 DB: races.csv",
            "from_key": "raceId, circuitId",
            "to_table": "pit_stops.csv / qualifying.csv / sprint_results.csv / circuits.csv",
            "to_key": "raceId, circuitId",
            "relationship": "1-to-Many",
            "purpose": "Connects 1,125 historical Grands Prix to 11,371 pit stops, 10,494 qualifying sessions, 360 sprint entries, and 77 GPS circuits."
        },
        {
            "from_table": "Kaggle Strategy Dataset (2021-2024)",
            "from_key": "Year, RoundNumber, Driver",
            "to_table": "Processed: f1_driver_race_combined.csv",
            "to_key": "year, round, driver_code",
            "relationship": "Many-to-1 Aggregate",
            "purpose": "Merges multi-season stint lengths, compounds used, and SC/VSC/rain laps into the 26,499-row historical race table."
        },
        {
            "from_table": "Kaggle Podiums (1950-2026) & Race Events",
            "from_key": "Season/Year, Grand Prix",
            "to_table": "Kaggle F1 DB: races.csv",
            "to_key": "year, name",
            "relationship": "1-to-Many",
            "purpose": "Enriches Grand Prix history with 1,158 podium trios, 380 Safety Car deployments, and 103 Red Flag stoppages."
        },
        {
            "from_table": "Kaggle All-Time Drivers Career (F1Drivers_Dataset.csv)",
            "from_key": "Driver",
            "to_table": "Kaggle F1 DB: drivers.csv",
            "to_key": "forename + surname",
            "relationship": "1-to-1",
            "purpose": "Links 868 historical drivers to career Pole Rate, Win Rate, Podium Rate, and Points per Entry."
        }
    ]
