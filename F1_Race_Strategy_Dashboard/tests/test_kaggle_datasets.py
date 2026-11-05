import pytest
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from data_processing.data_loader import (
    load_unified_results,
    load_unified_laps,
    load_kaggle_podiums,
    load_kaggle_safety_cars,
    load_kaggle_red_flags,
    load_kaggle_drivers_career,
    load_kaggle_circuits,
    load_kaggle_qualifying,
    load_kaggle_sprint_results,
    load_combined_driver_race,
    load_archive_2024_summary,
    load_ergast_pit_stops,
    load_strategy_dataset,
    load_kaggle_stint_aggression,
    load_kaggle_pit_events,
    load_kaggle_pit_prediction,
    load_kaggle_race_intelligence,
    load_kaggle_championship_standings,
    load_kaggle_live_tracker,
    load_kaggle_gp_winners,
    load_kaggle_weather_multiyear,
)
from data_processing.data_integration import apply_global_filters
from data_processing.analytics import (
    analyze_safety_car_and_red_flags,
    analyze_multi_year_strategy_warehouse,
    analyze_all_time_drivers_and_podiums,
    simulate_race_strategy,
)
import api_server


def test_load_unified_results_and_year_team_driver_filters():
    res = load_unified_results()
    assert not res.empty
    assert len(res) >= 26000
    assert {"Year", "FullName", "TeamName", "EventName", "Position"}.issubset(res.columns)
    # Check default year-wise sorting (newest year at top)
    assert res["Year"].iloc[0] >= 2024

    # Test filtering by Year, Team, Driver, and Year-wise sort order
    filters = {
        "selected_year": 2023,
        "year_sort_desc": True,
        "selected_team": "Red Bull Racing",
        "selected_drivers": ["Max Verstappen"],
        "selected_event": "All Events",
        "selected_compound": "ALL",
    }
    filtered = apply_global_filters(res, filters, sort_year_wise=True)
    assert not filtered.empty
    assert (filtered["Year"] == 2023).all()
    assert (filtered["TeamName"] == "Red Bull Racing").all()
    assert (filtered["FullName"] == "Max Verstappen").all()

    # Test chronological (oldest -> newest) sorting across All Years
    filters_chrono = {
        "selected_year": "All Years",
        "year_sort_desc": False,
        "selected_team": "Ferrari",
        "selected_drivers": ["All Drivers"],
        "selected_event": "All Events",
        "selected_compound": "ALL",
    }
    ferrari_chrono = apply_global_filters(res, filters_chrono, sort_year_wise=True)
    assert not ferrari_chrono.empty
    assert ferrari_chrono["Year"].iloc[0] <= ferrari_chrono["Year"].iloc[-1]


def test_load_unified_laps():
    laps = load_unified_laps()
    assert not laps.empty
    assert len(laps) >= 80000
    assert {"Year", "Driver", "FullName", "TeamName", "Compound", "LapTimeSec"}.issubset(laps.columns)


def test_load_new_kaggle_race_analytics_datasets():
    ri = load_kaggle_race_intelligence()
    sa = load_kaggle_stint_aggression()
    pe = load_kaggle_pit_events()
    pp = load_kaggle_pit_prediction()
    cs = load_kaggle_championship_standings()
    lt = load_kaggle_live_tracker()
    gw = load_kaggle_gp_winners()
    wm = load_kaggle_weather_multiyear()

    assert len(ri) >= 6000
    assert {"Year", "FullName", "TeamName", "tyre_strategy", "undercut_attempt", "overcut_attempt"}.issubset(ri.columns)

    assert len(sa) >= 7000
    assert {"Year", "FullName", "Compound", "Driver Aggression Score", "Tire Usage Aggression"}.issubset(sa.columns)

    assert len(pe) >= 12000
    assert {"Year", "FullName", "TeamName", "pit_duration_s", "stop_duration_s"}.issubset(pe.columns)

    assert len(pp) >= 100000
    assert {"Year", "Driver", "FullName", "TeamName", "PitNextLap", "Cumulative_Degradation"}.issubset(pp.columns)

    assert len(cs) >= 300
    assert len(lt) >= 900
    assert len(gw) >= 1100
    assert len(wm) >= 18000


def test_load_kaggle_podiums():
    df = load_kaggle_podiums()
    assert not df.empty, "Kaggle podiums dataset should not be empty"
    assert len(df) >= 1100
    assert {"Year", "Season", "Grand Prix", "Winner", "Second Place Driver", "Third Place Driver"}.issubset(df.columns)


def test_load_kaggle_safety_cars_and_red_flags():
    sc = load_kaggle_safety_cars()
    rf = load_kaggle_red_flags()
    assert not sc.empty, "Safety cars dataset should not be empty"
    assert len(sc) >= 350
    assert {"Race", "Cause", "FullLaps", "Year"}.issubset(sc.columns)

    assert not rf.empty, "Red flags dataset should not be empty"
    assert len(rf) >= 100
    assert {"Race", "Lap", "Incident", "Year"}.issubset(rf.columns)


def test_load_kaggle_drivers_career():
    df = load_kaggle_drivers_career()
    assert not df.empty, "Drivers career dataset should not be empty"
    assert len(df) >= 850
    assert {"Driver", "Championships", "Race_Wins", "Pole_Positions", "Win_Rate"}.issubset(df.columns)


def test_load_kaggle_circuits_qualifying_sprints():
    circ = load_kaggle_circuits()
    qual = load_kaggle_qualifying()
    spr = load_kaggle_sprint_results()

    assert len(circ) >= 75
    assert {"name", "lat", "lng", "RacesHosted"}.issubset(circ.columns)

    assert len(qual) >= 10000
    assert {"raceId", "FullName", "TeamName", "q1_sec"}.issubset(qual.columns)

    assert len(spr) >= 300
    assert {"raceId", "FullName", "TeamName", "points"}.issubset(spr.columns)


def test_load_combined_and_2024_archive():
    comb = load_combined_driver_race()
    arch = load_archive_2024_summary()
    ps = load_ergast_pit_stops()

    assert len(comb) >= 26000
    assert len(arch) >= 350
    assert len(ps) >= 11000
    assert "TeamName" in ps.columns


def test_kaggle_analytics_functions():
    sc = load_kaggle_safety_cars()
    rf = load_kaggle_red_flags()
    sc_res = analyze_safety_car_and_red_flags(sc, rf)
    assert sc_res["total_safety_cars"] >= 350
    assert sc_res["total_red_flags"] >= 100
    assert not sc_res["causes_breakdown"].empty

    comb = load_combined_driver_race()
    strat = load_strategy_dataset()
    wh_res = analyze_multi_year_strategy_warehouse(comb, strat)
    assert not wh_res["grid_to_finish"].empty
    assert not wh_res["pitstops_vs_finish_multiyear"].empty
    assert not wh_res["season_compound_pace"].empty

    drv = load_kaggle_drivers_career()
    pod = load_kaggle_podiums()
    hof_res = analyze_all_time_drivers_and_podiums(drv, pod)
    assert not hof_res["top_winners_career"].empty
    assert not hof_res["podium_leaders_1950_2026"].empty

    # Verify positional call compatibility on simulate_race_strategy
    l_df, s_df = simulate_race_strategy(57, 92.5, 21.5)
    assert len(l_df) == 171
    assert len(s_df) == 3


def test_api_server_kaggle_endpoints():
    health = api_server.health_check()
    assert health["status"] == "online"
    assert health["kaggle_datasets_integrated"] == 14

    assert len(api_server.get_kaggle_podiums(limit=10)) == 10
    assert len(api_server.get_kaggle_safety_cars(limit=10)) == 10
    assert len(api_server.get_kaggle_red_flags(limit=10)) == 10
    assert len(api_server.get_kaggle_drivers_career(champions_only=True, limit=10)) == 10
    assert len(api_server.get_kaggle_circuits()) >= 75
    assert len(api_server.get_kaggle_sprint_results(limit=10)) == 10
    assert len(api_server.get_kaggle_race_intelligence(year=2024, limit=10)) == 10
    assert len(api_server.get_kaggle_stint_aggression(year=2023, limit=10)) == 10
    assert len(api_server.get_kaggle_pit_events(year=2024, limit=10)) == 10
    assert len(api_server.get_kaggle_gp_winners(year=2024, limit=10)) == 10
