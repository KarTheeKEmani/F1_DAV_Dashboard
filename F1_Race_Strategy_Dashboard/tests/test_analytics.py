import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_processing.analytics import (
    calculate_tyre_degradation,
    calculate_pitstop_strategy_impact,
    calculate_driver_consistency,
    calculate_teammate_comparison
)


def test_calculate_tyre_degradation():
    # Synthetic lap data with known degradation slope
    tyre_life = np.arange(1, 25)
    lap_times = 90.0 + 0.1 * tyre_life + np.random.normal(0, 0.05, len(tyre_life))
    df = pd.DataFrame({
        "Compound": ["MEDIUM"] * len(tyre_life),
        "TyreLife": tyre_life,
        "LapTimeSec": lap_times,
        "IsOutlierLap": [False] * len(tyre_life)
    })

    deg_res = calculate_tyre_degradation(df)
    assert not deg_res.empty
    assert "DegradationSecPerLap" in deg_res.columns
    # Check that estimated slope is close to 0.1 s/lap
    assert deg_res['DegradationSecPerLap'].iloc[0] == pytest.approx(0.1, abs=0.05)


def test_calculate_pitstop_strategy_impact():
    df = pd.DataFrame({
        "DriverNumber": [1, 11, 44, 63],
        "Position": [1, 2, 3, 4],
        "PitStopsCount": [2, 2, 1, 2],
        "StrategyType": ["2-Stop", "2-Stop", "1-Stop", "2-Stop"],
        "StartingCompound": ["MEDIUM", "MEDIUM", "SOFT", "MEDIUM"]
    })
    impact = calculate_pitstop_strategy_impact(df)
    assert "correlation_pitstops_position" in impact
    assert "strategy_performance" in impact
    assert len(impact["strategy_performance"]) > 0


def test_calculate_driver_consistency():
    df = pd.DataFrame({
        "Driver": ["VER"] * 20 + ["PER"] * 20,
        "Team": ["Red Bull"] * 40,
        "LapTimeSec": [90.0 + i * 0.05 for i in range(20)] + [91.0 + (i % 3) * 0.5 for i in range(20)],
        "IsOutlierLap": [False] * 40
    })
    cons = calculate_driver_consistency(df)
    assert not cons.empty
    assert "ConsistencyCV" in cons.columns
    assert "Driver" in cons.columns


def test_simulate_race_strategy():
    from data_processing.analytics import simulate_race_strategy
    laps_df, summary_df = simulate_race_strategy(total_laps=50, base_lap_sec=90.0, pit_loss_sec=20.0)
    assert not laps_df.empty
    assert not summary_df.empty
    assert "TotalRaceTimeSec" in summary_df.columns
    assert "DeltaToFastestSec" in summary_df.columns
    assert len(summary_df) == 3
