import sys
from pathlib import Path
import kagglehub

RAW_DATA_DIR = Path(r"G:\DAV\f1-project\notebooks\data\raw")

KAGGLE_DATASETS = {
    "f1_world_1950_2026": {
        "slug": "samuelpombourcq/formula-1-world-championship-1950-2026",
        "description": "Formula 1 World Championship (1950-2026, 15 CSV tables including practice, sprints, pit stops)",
        "expected_file": "races.csv",
    },
    "strategy": {
        "slug": "yajatpawar/formula-1-strategy-dataset",
        "description": "Multi-Season F1 Strategy & Stints Dataset (2021-2024, 80,767 laps)",
        "expected_file": "f1_strategy_final_dataset.csv",
    },
    "stint_aggression": {
        "slug": "akashrane2609/f1-stint-data-with-aggression-scores",
        "description": "F1 Stint Data with Driver & Tyre Aggression Scores (2018-2024, 7,374 stints)",
        "expected_file": "f1_pitstops_2018_2024.csv",
    },
    "pit_stop_analytics": {
        "slug": "akashrane2609/formula-1-pit-stop-dataset",
        "description": "Granular F1 Pit Stop & Stint Dataset (2011-2026, 9 CSV tables with stationary vs pit-lane duration)",
        "expected_file": "pit_events.csv",
    },
    "pit_stop_prediction": {
        "slug": "vanshjasuja16/f1-strategy-dataset-pit-stop-prediction",
        "description": "F1 Strategy & Pit Stop Prediction Dataset (2022-2025, 101,371 laps)",
        "expected_file": "f1_strategy_dataset_v4.csv",
    },
    "race_intelligence": {
        "slug": "meruvakodandasuraj/formula-1-race-intelligence-20102026",
        "description": "Formula 1 Race Intelligence (2010-2026, 5 CSV tables with undercuts, overcuts, DRS overtakes)",
        "expected_file": "race_results.csv",
    },
    "live_tracker_2024_2026": {
        "slug": "devtayyabsajjad/formula-1-live-tracker-2024-2026-dataset",
        "description": "Formula 1 Live Tracker (2024-2026, 12 CSV tables including Sprint Qualifying & Results)",
        "expected_file": "race_results.csv",
    },
    "gp_winners_1950_2025": {
        "slug": "julianbloise/winners-formula-1-1950-to-2025",
        "description": "Formula 1 Grand Prix Winners Dataset (1950-2025, 1,142 races)",
        "expected_file": "winners_f1_1950_2025_v2.csv",
    },
    "weather_2018_2023": {
        "slug": "quantumkaze/f1-weather-dataset-2018-2023",
        "description": "Formula 1 Multi-Year Track Weather Dataset (2018-2023, 18,214 observations)",
        "expected_file": "F1 Weather(2023-2018).csv",
    },
    "rohanrao_f1": {
        "slug": "rohanrao/formula-1-world-championship-1950-2020",
        "description": "Formula 1 World Championship 1950-2024 Extended Database (14 CSV tables)",
        "expected_file": "pit_stops.csv",
    },
    "formula1": {
        "slug": "melissamonfared/formula-1",
        "description": "Formula 1 Relational Database (14 CSV tables)",
        "expected_file": "races.csv",
    },
    "podiums": {
        "slug": "maulikgajera/formula-one-race-podiums-19502026",
        "description": "Formula One Race Podiums (1950-2026, 1,158 Grands Prix)",
        "expected_file": "f1_podiums_1950_2026.csv",
    },
    "race_events": {
        "slug": "jtrotman/formula-1-race-events",
        "description": "Formula 1 Safety Cars (380 deployments) & Red Flags (103 stoppages)",
        "expected_file": "safety_cars.csv",
    },
    "drivers_career": {
        "slug": "petalme/f1-drivers-dataset",
        "description": "All-Time Formula 1 Drivers Career Statistics (868 drivers, 22 metrics)",
        "expected_file": "F1Drivers_Dataset.csv",
    },
}


def ensure_kaggle_datasets(force: bool = False):
    """Downloads and verifies all 14 Kaggle Formula 1 datasets into G:\\DAV."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    for folder_name, meta in KAGGLE_DATASETS.items():
        target_dir = RAW_DATA_DIR / folder_name
        expected_path = target_dir / meta["expected_file"]

        if expected_path.exists() and not force:
            print(f"[SKIP] {folder_name} ({meta['slug']}) already exists at {target_dir}")
            results[folder_name] = {"status": "cached", "path": str(target_dir)}
            continue

        print(f"[DOWNLOADING] {folder_name} -> {meta['slug']} ...")
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            dl_path = kagglehub.dataset_download(meta["slug"], output_dir=str(target_dir))
            print(f"[SUCCESS] Downloaded {meta['slug']} to {dl_path}")
            results[folder_name] = {"status": "downloaded", "path": str(dl_path)}
        except Exception as e:
            print(f"[ERROR] Failed to download {meta['slug']}: {e}")
            results[folder_name] = {"status": "error", "error": str(e)}

    return results


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    summary = ensure_kaggle_datasets(force=force_flag)
    print("\n=== Kaggle Dataset Sync Summary (14 Repositories) ===")
    for k, v in summary.items():
        print(f"  {k}: {v['status']} ({v.get('path', v.get('error', ''))})")
