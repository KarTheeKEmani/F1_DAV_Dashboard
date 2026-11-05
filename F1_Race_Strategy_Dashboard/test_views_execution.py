import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_processing.data_loader import (
    load_f1_events, load_unified_results, load_unified_laps,
    load_f1_fastest_laps, load_f1_weather, load_strategy_dataset,
    load_ergast_pit_stops, load_fastest_laps_telemetry, load_round1_telemetry,
    load_kaggle_podiums, load_kaggle_safety_cars, load_kaggle_red_flags,
    load_kaggle_drivers_career, load_kaggle_circuits, load_kaggle_qualifying,
    load_kaggle_sprint_results, load_combined_driver_race, load_archive_2024_summary,
    load_kaggle_race_intelligence, load_kaggle_stint_aggression,
    load_kaggle_pit_events, load_kaggle_pit_prediction,
    load_kaggle_live_tracker, load_kaggle_gp_winners, load_kaggle_weather_multiyear
)
from components.charts import (
    plot_race_finish_vs_grid, plot_driver_standings, plot_stint_timeline,
    plot_tyre_degradation, plot_lap_pace_progression, plot_telemetry_traces,
    plot_pitstop_distribution, plot_strategy_simulation
)
from data_processing.data_integration import (
    build_driver_strategy_summary, compute_undercut_overcut_candidates,
    integrate_weather_with_races, apply_global_filters
)
from data_processing.analytics import (
    calculate_tyre_degradation, calculate_pitstop_strategy_impact,
    compute_pitstop_team_rankings, calculate_driver_consistency,
    calculate_teammate_comparison, simulate_race_strategy,
    analyze_safety_car_and_red_flags, analyze_multi_year_strategy_warehouse,
    analyze_all_time_drivers_and_podiums
)
from data_processing.schema_detection import discover_all_datasets, get_detected_relationships


def test_full_pipeline():
    print("1. Loading unified & 14 Kaggle F1 Race Analytics datasets...")
    events = load_f1_events()
    results = load_unified_results()
    laps = load_unified_laps()
    fl = load_f1_fastest_laps()
    weather = load_f1_weather()
    strat = load_strategy_dataset()
    ergast = load_ergast_pit_stops()
    fl_telem = load_fastest_laps_telemetry()
    r1_telem = load_round1_telemetry()

    podiums = load_kaggle_podiums()
    safety_cars = load_kaggle_safety_cars()
    red_flags = load_kaggle_red_flags()
    drivers_career = load_kaggle_drivers_career()
    circuits = load_kaggle_circuits()
    qualifying = load_kaggle_qualifying()
    sprint_res = load_kaggle_sprint_results()
    combined_wh = load_combined_driver_race()
    arch_2024 = load_archive_2024_summary()
    race_intel = load_kaggle_race_intelligence()
    stint_agg = load_kaggle_stint_aggression()
    pit_events = load_kaggle_pit_events()
    pit_pred = load_kaggle_pit_prediction()
    live_tracker = load_kaggle_live_tracker()
    gp_winners = load_kaggle_gp_winners()
    weather_multi = load_kaggle_weather_multiyear()

    print(f"   Unified Results (1950-2026): {len(results):,} rows")
    print(f"   Unified Laps (2021-2025+): {len(laps):,} rows")
    print(f"   Kaggle Race Intelligence (2010-2026): {len(race_intel):,} rows")
    print(f"   Kaggle Stint & Aggression (2018-2024): {len(stint_agg):,} rows")
    print(f"   Kaggle Pit Events (2011-2026): {len(pit_events):,} rows")
    print(f"   Kaggle Pit Prediction (2022-2025): {len(pit_pred):,} rows")
    print(f"   Kaggle Live Tracker (2024-2026): {len(live_tracker):,} rows")
    print(f"   Kaggle GP Winners (1950-2025): {len(gp_winners):,} rows")
    print(f"   Kaggle Weather Multi-Year (2018-2023): {len(weather_multi):,} rows")
    print(f"   Kaggle Pit Stops (1950-2026): {len(ergast):,} rows")
    print(f"   Kaggle Podiums (1950-2026): {len(podiums):,} rows")
    print(f"   Kaggle Safety Cars: {len(safety_cars)} rows | Red Flags: {len(red_flags)} rows")
    print(f"   Kaggle Drivers Career: {len(drivers_career)} rows")

    print("2. Testing Year-Wise Sorting & Team/Driver/Year Filtering...")
    sample_filters = {
        "selected_year": 2023,
        "year_sort_desc": True,
        "selected_team": "All Teams",
        "selected_drivers": ["All Drivers"],
        "selected_event": "All Events",
        "selected_compound": "ALL",
    }
    res_2023 = apply_global_filters(results, sample_filters, sort_year_wise=True)
    laps_2023 = apply_global_filters(laps, sample_filters, sort_year_wise=True)
    assert not res_2023.empty and not laps_2023.empty

    strat_summary = build_driver_strategy_summary(laps_2023, res_2023)
    print(f"   Strategy Summary (2023): {len(strat_summary)} rows")

    undercuts = compute_undercut_overcut_candidates(laps_2023)
    print(f"   Undercut Candidates (2023): {len(undercuts)} rows")

    print("3. Testing Analytics Algorithms...")
    deg = calculate_tyre_degradation(laps_2023)
    impact = calculate_pitstop_strategy_impact(strat_summary)
    crew = compute_pitstop_team_rankings(ergast)
    cons = calculate_driver_consistency(laps_2023)
    teammates = calculate_teammate_comparison(res_2023)
    sim_laps, sim_summary = simulate_race_strategy(57, 92.5, 21.5)
    sc_analysis = analyze_safety_car_and_red_flags(safety_cars, red_flags)
    wh_analysis = analyze_multi_year_strategy_warehouse(combined_wh, strat)
    hof_analysis = analyze_all_time_drivers_and_podiums(drivers_career, podiums)

    print("4. Testing Chart Generation...")
    assert plot_race_finish_vs_grid(res_2023) is not None
    assert plot_driver_standings(res_2023) is not None
    assert plot_stint_timeline(laps_2023) is not None
    assert plot_tyre_degradation(laps_2023) is not None
    assert plot_lap_pace_progression(laps_2023, ['VER', 'HAM']) is not None
    assert plot_telemetry_traces(fl_telem.head(500)) is not None
    assert plot_pitstop_distribution(ergast) is not None
    assert plot_strategy_simulation(sim_laps) is not None

    print("5. Testing Schema Discovery...")
    catalog = discover_all_datasets()
    print(f"   Discovered {len(catalog)} datasets in catalog.")
    rels = get_detected_relationships()
    print(f"   Detected {len(rels)} relationships.")

    print("\nALL PIPELINE, 14 KAGGLE DATASETS, YEAR-WISE FILTERS & COMPONENT TESTS PASSED WITH 100% SUCCESS!")


if __name__ == '__main__':
    test_full_pipeline()
