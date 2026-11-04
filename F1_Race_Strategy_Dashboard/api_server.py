import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_processing.data_loader import (
    load_f1_events, load_f1_results, load_f1_laps,
    load_f1_weather, load_ergast_pit_stops,
    load_fastest_laps_telemetry, load_round1_telemetry
)
from data_processing.data_integration import build_driver_strategy_summary
from data_processing.analytics import calculate_tyre_degradation, simulate_race_strategy

app = FastAPI(
    title="Formula 1 Race Telemetry & Strategy REST API",
    description="Backend microservice providing high-performance race telemetry, tyre stint metrics, and pit strategy modeling.",
    version="1.0.0"
)

# Enable CORS for external frontends (e.g., Streamlit, React, Vue, Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    """Health check endpoint for service monitoring."""
    return {"status": "online", "service": "F1 Strategy & Telemetry Backend API"}


@app.get("/api/events")
def get_events():
    """Returns official 2023 FIA Formula 1 Grand Prix calendar."""
    df = load_f1_events()
    return df.to_dict(orient="records")


@app.get("/api/results")
def get_results(round_num: Optional[int] = Query(None, alias="round")):
    """Returns race results and standings, optionally filtered by round number."""
    df = load_f1_results()
    if round_num is not None:
        df = df[df["RoundNumber"] == round_num]
    return df.to_dict(orient="records")


@app.get("/api/strategy")
def get_strategy(round_num: Optional[int] = Query(None, alias="round")):
    """Returns driver tyre stint sequences, pit stop counts, and strategy classification."""
    laps_df = load_f1_laps()
    results_df = load_f1_results()
    if round_num is not None:
        laps_df = laps_df[laps_df["RoundNumber"] == round_num]
        results_df = results_df[results_df["RoundNumber"] == round_num]
    summary = build_driver_strategy_summary(laps_df, results_df)
    return summary.to_dict(orient="records")


@app.get("/api/tyre-degradation")
def get_tyre_degradation():
    """Returns empirical tyre wear degradation slopes (s/lap) per compound."""
    laps_df = load_f1_laps()
    deg_df = calculate_tyre_degradation(laps_df)
    return deg_df.to_dict(orient="records")


@app.get("/api/telemetry/fastest")
def get_fastest_telemetry(round_num: Optional[int] = Query(None, alias="round")):
    """Returns high-frequency telemetry samples for fastest laps."""
    df = load_fastest_laps_telemetry()
    if round_num is not None:
        df = df[df["RoundNumber"] == round_num]
    return df.head(1000).to_dict(orient="records")


@app.get("/api/pitstops")
def get_pitstops(limit: int = 100):
    """Returns millisecond-accurate stationary pit stop records from historical database."""
    df = load_ergast_pit_stops()
    clean = df[(df["DurationSec"] >= 1.5) & (df["DurationSec"] <= 20.0)] if "DurationSec" in df.columns else df
    return clean.head(limit).to_dict(orient="records")


@app.get("/api/simulate")
def run_simulation(
    laps: int = 57,
    base_pace: float = 92.5,
    pit_loss: float = 21.5
):
    """Executes race strategy mathematical simulation model."""
    laps_df, summary_df = simulate_race_strategy(
        total_laps=laps,
        base_lap_sec=base_pace,
        pit_loss_sec=pit_loss
    )
    return {
        "summary": summary_df.to_dict(orient="records"),
        "sample_laps": laps_df.head(100).to_dict(orient="records")
    }


if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
