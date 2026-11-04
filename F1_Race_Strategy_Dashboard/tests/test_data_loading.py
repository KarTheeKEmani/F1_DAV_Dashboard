import pytest
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_processing.data_loader import (
    load_f1_events,
    load_f1_results,
    load_f1_laps,
    load_f1_fastest_laps,
    load_f1_weather,
    load_strategy_dataset,
    load_ergast_pit_stops
)


def test_load_f1_events():
    df = load_f1_events()
    assert not df.empty, "Events dataframe should not be empty"
    assert "RoundNumber" in df.columns
    assert "EventName" in df.columns
    assert len(df) >= 20, f"Expected ~22 races, found {len(df)}"


def test_load_f1_results():
    df = load_f1_results()
    assert not df.empty, "Results dataframe should not be empty"
    assert "Position" in df.columns
    assert "Points" in df.columns
    assert "DriverNumber" in df.columns


def test_load_f1_laps():
    df = load_f1_laps()
    assert not df.empty, "Laps dataframe should not be empty"
    assert "LapTimeSec" in df.columns
    assert "Compound" in df.columns
    assert "Stint" in df.columns
    assert len(df) > 10000, "Expected over 10,000 laps in 2023 season"


def test_load_strategy_dataset():
    df = load_strategy_dataset()
    assert not df.empty, "Strategy dataset should not be empty"
    assert "TyreLife" in df.columns
    assert len(df) > 50000, "Expected over 50,000 laps in multi-year strategy dataset"


def test_load_ergast_pit_stops():
    df = load_ergast_pit_stops()
    assert not df.empty, "Pit stops dataset should not be empty"
    assert "DurationSec" in df.columns
    assert "raceId" in df.columns
