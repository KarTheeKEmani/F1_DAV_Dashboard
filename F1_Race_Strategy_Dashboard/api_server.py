import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_processing.data_loader import (
    load_f1_events, load_f1_results, load_f1_laps, load_unified_results,
    load_f1_weather, load_ergast_pit_stops,
    load_fastest_laps_telemetry, load_round1_telemetry,
    load_kaggle_podiums, load_kaggle_safety_cars,
    load_kaggle_red_flags, load_kaggle_drivers_career,
    load_kaggle_circuits, load_kaggle_sprint_results,
    load_kaggle_race_intelligence, load_kaggle_stint_aggression,
    load_kaggle_pit_events, load_kaggle_gp_winners
)
from data_processing.data_integration import build_driver_strategy_summary
from data_processing.analytics import calculate_tyre_degradation, simulate_race_strategy

app = FastAPI(
    title="Formula 1 Race Telemetry & Strategy REST API",
    description="Backend microservice providing high-performance race telemetry, tyre stint metrics, pit strategy modeling, and 6 integrated Kaggle datasets.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _clean_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Converts DataFrame to JSON-safe records replacing NaN/Inf with None."""
    if df.empty:
        return []
    clean_df = df.replace([np.inf, -np.inf], np.nan)
    return clean_df.astype(object).where(pd.notna(clean_df), None).to_dict(orient="records")


@app.get("/api/health")
def health_check():
    """Health check endpoint for service monitoring."""
    return {
        "status": "online",
        "service": "F1 Strategy & Telemetry Backend API",
        "version": "2.1.0",
        "kaggle_datasets_integrated": 14
    }


@app.get("/api/events")
def get_events():
    """Returns official 2023 FIA Formula 1 Grand Prix calendar."""
    df = load_f1_events()
    return _clean_records(df)


@app.get("/api/results")
def get_results(
    round_num: Optional[int] = Query(None, alias="round"),
    year: Optional[int] = Query(None),
    team: Optional[str] = Query(None),
    driver: Optional[str] = Query(None),
    limit: int = 500
):
    """Returns unified Year-wise race results (1950–2026), optionally filtered by year, round, team, and driver."""
    df = load_unified_results() if (year is not None or team is not None or driver is not None) else load_f1_results()
    if year is not None and "Year" in df.columns:
        df = df[df["Year"] == year]
    if round_num is not None and "RoundNumber" in df.columns:
        df = df[df["RoundNumber"] == round_num]
    if team is not None and "TeamName" in df.columns:
        df = df[df["TeamName"].str.contains(team, case=False, na=False)]
    if driver is not None:
        mask = pd.Series(False, index=df.index)
        if "FullName" in df.columns:
            mask = mask | df["FullName"].str.contains(driver, case=False, na=False)
        if "Abbreviation" in df.columns:
            mask = mask | df["Abbreviation"].str.contains(driver, case=False, na=False)
        df = df[mask]
    return _clean_records(df.head(limit))


@app.get("/api/strategy")
def get_strategy(round_num: Optional[int] = Query(None, alias="round")):
    """Returns driver tyre stint sequences, pit stop counts, and strategy classification."""
    laps_df = load_f1_laps()
    results_df = load_f1_results()
    if round_num is not None:
        laps_df = laps_df[laps_df["RoundNumber"] == round_num]
        results_df = results_df[results_df["RoundNumber"] == round_num]
    summary = build_driver_strategy_summary(laps_df, results_df)
    return _clean_records(summary)


@app.get("/api/tyre-degradation")
def get_tyre_degradation():
    """Returns empirical tyre wear degradation slopes (s/lap) per compound."""
    laps_df = load_f1_laps()
    deg_df = calculate_tyre_degradation(laps_df)
    return _clean_records(deg_df)


@app.get("/api/telemetry/fastest")
def get_fastest_telemetry(round_num: Optional[int] = Query(None, alias="round")):
    """Returns high-frequency telemetry samples for fastest laps."""
    df = load_fastest_laps_telemetry()
    if round_num is not None:
        df = df[df["RoundNumber"] == round_num]
    return _clean_records(df.head(1000))


@app.get("/api/pitstops")
def get_pitstops(limit: int = 100):
    """Returns millisecond-accurate stationary pit stop records from Kaggle historical database."""
    df = load_ergast_pit_stops()
    clean = df[(df["DurationSec"] >= 1.5) & (df["DurationSec"] <= 20.0)] if "DurationSec" in df.columns else df
    return _clean_records(clean.head(limit))


@app.get("/api/simulate")
def run_simulation(
    laps: int = 57,
    base_pace: float = 92.5,
    pit_loss: float = 21.5
):
    """Executes race strategy mathematical simulation model."""
    laps_df, summary_df = simulate_race_strategy(
        total_laps=laps,
        strategies=None,
        base_lap_sec=base_pace,
        pit_loss_sec=pit_loss
    )
    return {
        "summary": _clean_records(summary_df),
        "sample_laps": _clean_records(laps_df.head(100))
    }


@app.get("/api/kaggle/podiums")
def get_kaggle_podiums(season: Optional[int] = None, limit: int = 200):
    """Returns Grand Prix podium trios (1950-2026) from Kaggle dataset."""
    df = load_kaggle_podiums()
    if season is not None and "Season" in df.columns:
        df = df[df["Season"] == season]
    return _clean_records(df.head(limit))


@app.get("/api/kaggle/safety-cars")
def get_kaggle_safety_cars(limit: int = 200):
    """Returns historical Safety Car deployments from Kaggle Race Events dataset."""
    df = load_kaggle_safety_cars()
    return _clean_records(df.head(limit))


@app.get("/api/kaggle/red-flags")
def get_kaggle_red_flags(limit: int = 200):
    """Returns historical Red Flag race stoppages from Kaggle Race Events dataset."""
    df = load_kaggle_red_flags()
    return _clean_records(df.head(limit))


@app.get("/api/kaggle/drivers-career")
def get_kaggle_drivers_career(champions_only: bool = False, limit: int = 100):
    """Returns all-time Formula 1 Drivers Career Statistics (868 drivers)."""
    df = load_kaggle_drivers_career()
    if champions_only and "Championships" in df.columns:
        df = df[df["Championships"] > 0]
    df = df.sort_values("Race_Wins", ascending=False) if "Race_Wins" in df.columns else df
    return _clean_records(df.head(limit))


@app.get("/api/kaggle/circuits")
def get_kaggle_circuits():
    """Returns all 77 historical Formula 1 circuits with GPS coordinates and races hosted."""
    df = load_kaggle_circuits()
    return _clean_records(df)


@app.get("/api/kaggle/sprint-results")
def get_kaggle_sprint_results(limit: int = 150):
    """Returns Formula 1 Sprint Race results from Kaggle World Championship DB."""
    df = load_kaggle_sprint_results()
    return _clean_records(df.head(limit))


@app.get("/api/kaggle/race-intelligence")
def get_kaggle_race_intelligence(year: Optional[int] = None, team: Optional[str] = None, driver: Optional[str] = None, limit: int = 200):
    """Returns 2010-2026 Race Intelligence strategy, undercut/overcut, and DRS overtake records sorted Year-wise."""
    df = load_kaggle_race_intelligence()
    if year is not None and "Year" in df.columns:
        df = df[df["Year"] == year]
    if team is not None and "TeamName" in df.columns:
        df = df[df["TeamName"].str.contains(team, case=False, na=False)]
    if driver is not None and "FullName" in df.columns:
        df = df[df["FullName"].str.contains(driver, case=False, na=False)]
    return _clean_records(df.head(limit))


@app.get("/api/kaggle/stint-aggression")
def get_kaggle_stint_aggression(year: Optional[int] = None, driver: Optional[str] = None, limit: int = 200):
    """Returns 2018-2024 Stint & Driver Aggression Scores sorted Year-wise."""
    df = load_kaggle_stint_aggression()
    if year is not None and "Year" in df.columns:
        df = df[df["Year"] == year]
    if driver is not None and "FullName" in df.columns:
        df = df[df["FullName"].str.contains(driver, case=False, na=False)]
    return _clean_records(df.head(limit))


@app.get("/api/kaggle/pit-events")
def get_kaggle_pit_events(year: Optional[int] = None, team: Optional[str] = None, limit: int = 200):
    """Returns 2011-2026 Pit Events with both stationary and pit-lane durations sorted Year-wise."""
    df = load_kaggle_pit_events()
    if year is not None and "Year" in df.columns:
        df = df[df["Year"] == year]
    if team is not None and "TeamName" in df.columns:
        df = df[df["TeamName"].str.contains(team, case=False, na=False)]
    return _clean_records(df.head(limit))


@app.get("/api/kaggle/gp-winners")
def get_kaggle_gp_winners(year: Optional[int] = None, team: Optional[str] = None, limit: int = 200):
    """Returns 1950-2025 Grand Prix Winners sorted Year-wise."""
    df = load_kaggle_gp_winners()
    if year is not None and "Year" in df.columns:
        df = df[df["Year"] == year]
    if team is not None and "TeamName" in df.columns:
        df = df[df["TeamName"].str.contains(team, case=False, na=False)]
    return _clean_records(df.head(limit))


if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
