import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_processing.data_cleaning import (
    parse_timedelta_to_seconds,
    format_seconds_to_laptime,
    clean_compound_name,
    clean_laps_data,
    clean_results_data,
    clean_pitstops_data
)


def test_parse_timedelta_to_seconds():
    # String timedelta format
    assert parse_timedelta_to_seconds("0 days 00:01:33.996000") == pytest.approx(93.996, rel=1e-3)
    assert parse_timedelta_to_seconds("0 days 01:33:56.736000") == pytest.approx(5636.736, rel=1e-3)
    # MM:SS.sss format
    assert parse_timedelta_to_seconds("1:29.450") == pytest.approx(89.450, rel=1e-3)
    # Direct float
    assert parse_timedelta_to_seconds(92.5) == 92.5
    # Null / Invalid values
    assert np.isnan(parse_timedelta_to_seconds(None))
    assert np.isnan(parse_timedelta_to_seconds(np.nan))
    assert np.isnan(parse_timedelta_to_seconds("\\N"))


def test_format_seconds_to_laptime():
    assert format_seconds_to_laptime(89.45) == "1:29.450"
    assert format_seconds_to_laptime(24.5) == "24.500s"
    assert format_seconds_to_laptime(None) == "N/A"
    assert format_seconds_to_laptime(-5) == "N/A"


def test_clean_compound_name():
    assert clean_compound_name("soft") == "SOFT"
    assert clean_compound_name("MEDIUM") == "MEDIUM"
    assert clean_compound_name("Hard") == "HARD"
    assert clean_compound_name("INTERMEDIATE") == "INTERMEDIATE"
    assert clean_compound_name("WET") == "WET"
    assert clean_compound_name(None) == "UNKNOWN"


def test_clean_laps_data():
    raw_df = pd.DataFrame({
        "LapNumber": [1, 2, 3],
        "Driver": ["VER", "VER", "VER"],
        "RoundNumber": [1, 1, 1],
        "LapTime": ["0 days 00:01:35.000000", "0 days 00:01:34.000000", "0 days 00:01:34.500000"],
        "Compound": ["soft", "SOFT", "medium"],
        "PitInTime": [None, None, "0 days 01:25:00.000000"]
    })
    cleaned = clean_laps_data(raw_df)
    assert "LapTimeSec" in cleaned.columns
    assert cleaned["LapTimeSec"].iloc[0] == pytest.approx(95.0)
    assert cleaned["Compound"].iloc[0] == "SOFT"
    assert cleaned["IsPitLap"].iloc[2] == True
    assert cleaned["IsPitLap"].iloc[0] == False
