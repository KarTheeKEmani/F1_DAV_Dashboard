import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_processing.data_loader import (
    load_f1_events, load_f1_results, load_f1_laps,
    load_f1_fastest_laps, load_f1_weather, load_strategy_dataset,
    load_ergast_pit_stops, load_fastest_laps_telemetry, load_round1_telemetry
)
from components.charts import (
    plot_race_finish_vs_grid, plot_driver_standings, plot_stint_timeline,
    plot_tyre_degradation, plot_lap_pace_progression, plot_telemetry_traces,
    plot_pitstop_distribution
)
from data_processing.data_integration import (
    build_driver_strategy_summary, compute_undercut_overcut_candidates,
    integrate_weather_with_races
)
from data_processing.analytics import (
    calculate_tyre_degradation, calculate_pitstop_strategy_impact,
    compute_pitstop_team_rankings, calculate_driver_consistency,
    calculate_teammate_comparison
)
from data_processing.schema_detection import discover_all_datasets, get_detected_relationships


def test_full_pipeline():
    print("1. Loading datasets...")
    events = load_f1_events()
    results = load_f1_results()
    laps = load_f1_laps()
    fl = load_f1_fastest_laps()
    weather = load_f1_weather()
    strat = load_strategy_dataset()
    ergast = load_ergast_pit_stops()
    fl_telem = load_fastest_laps_telemetry()
    r1_telem = load_round1_telemetry()

    print(f"   Events: {len(events)} rows")
    print(f"   Results: {len(results)} rows")
    print(f"   Laps: {len(laps)} rows")
    print(f"   Fastest Laps: {len(fl)} rows")
    print(f"   Weather: {len(weather)} rows")
    print(f"   Strategy: {len(strat)} rows")
    print(f"   Ergast Pit Stops: {len(ergast)} rows")
    print(f"   Fastest Lap Telemetry: {len(fl_telem)} rows")
    print(f"   Round 1 Telemetry: {len(r1_telem)} rows")

    print("2. Testing Data Integration...")
    strat_summary = build_driver_strategy_summary(laps, results)
    print(f"   Strategy Summary: {len(strat_summary)} rows")

    undercuts = compute_undercut_overcut_candidates(laps)
    print(f"   Undercut Candidates: {len(undercuts)} rows")

    weather_merged = integrate_weather_with_races(results, weather)
    print(f"   Weather Merged: {len(weather_merged)} rows")

    print("3. Testing Analytics Algorithms...")
    deg = calculate_tyre_degradation(laps)
    print(f"   Tyre Deg: {len(deg)} rows")

    impact = calculate_pitstop_strategy_impact(strat_summary)
    print(f"   Pit Impact Corr: {impact.get('correlation_pitstops_position')}")

    crew = compute_pitstop_team_rankings(ergast)
    print(f"   Pit Crew Rankings: {len(crew)} rows")

    cons = calculate_driver_consistency(laps)
    print(f"   Driver Consistency: {len(cons)} rows")

    teammates = calculate_teammate_comparison(results)
    print(f"   Teammate Battles: {len(teammates)} rows")

    print("4. Testing Chart Generation...")
    fig1 = plot_race_finish_vs_grid(results)
    assert fig1 is not None
    fig2 = plot_driver_standings(results)
    assert fig2 is not None
    fig3 = plot_stint_timeline(laps)
    assert fig3 is not None
    fig4 = plot_tyre_degradation(laps)
    assert fig4 is not None
    fig5 = plot_lap_pace_progression(laps, ['VER', 'HAM'])
    assert fig5 is not None
    fig6 = plot_telemetry_traces(fl_telem.head(500))
    assert fig6 is not None
    fig7 = plot_pitstop_distribution(ergast)
    assert fig7 is not None

    print("5. Testing Schema Discovery...")
    catalog = discover_all_datasets()
    print(f"   Discovered {len(catalog)} datasets in catalog.")
    rels = get_detected_relationships()
    print(f"   Detected {len(rels)} relationships.")

    print("\nALL PIPELINE & COMPONENT TESTS PASSED WITH 100% SUCCESS!")


if __name__ == '__main__':
    test_full_pipeline()
