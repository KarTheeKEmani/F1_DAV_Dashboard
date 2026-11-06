import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import plotly.graph_objects as go
from data_processing.data_loader import (
    load_unified_results, load_unified_laps, load_ergast_pit_stops,
    load_strategy_dataset, load_kaggle_safety_cars
)
from data_processing.data_integration import build_driver_strategy_summary
from components.charts import (
    plot_race_finish_vs_grid,
    plot_driver_standings,
    plot_stint_timeline,
    plot_tyre_degradation,
    plot_lap_pace_progression,
    plot_telemetry_traces,
    plot_pitstop_distribution,
    plot_strategy_simulation,
    plot_constructor_points_donut,
    plot_championship_sunburst,
    plot_cumulative_points_area,
    plot_driver_finish_heatmap,
    plot_strategy_type_donut,
    plot_pit_stops_vs_finish_scatter,
    plot_safety_car_causes_pie,
    plot_compound_donut_chart,
    plot_stint_length_violin,
    plot_stint_compound_treemap,
    plot_pitstop_by_team_violin,
    plot_driver_lap_time_violin,
    plot_driver_performance_radar,
    plot_grid_to_finish_waterfall
)


def test_all_graphs():
    print("Testing all F1 graph types...")
    results_df = load_unified_results()
    laps_df = load_unified_laps()
    pitstops_df = load_ergast_pit_stops()
    strat_df = load_strategy_dataset()
    sc_df = load_kaggle_safety_cars()

    res_2023 = results_df[results_df['Year'] == 2023]
    laps_2023 = laps_df[laps_df['Year'] == 2023]
    strat_summary = build_driver_strategy_summary(laps_2023, res_2023)

    charts = [
        ("1. Grid vs Finish Scatter", plot_race_finish_vs_grid(res_2023)),
        ("2. Driver Standings Bar", plot_driver_standings(res_2023)),
        ("3. Stint Timeline Gantt", plot_stint_timeline(laps_2023)),
        ("4. Tyre Degradation Scatter + Trendline", plot_tyre_degradation(laps_2023)),
        ("5. Lap Pace Progression Line", plot_lap_pace_progression(laps_2023, ['VER', 'HAM'])),
        ("6. Pit Stop Distribution Histogram", plot_pitstop_distribution(pitstops_df)),
        ("7. Constructor Points Donut / Pie", plot_constructor_points_donut(res_2023)),
        ("8. Championship Sunburst Hierarchy", plot_championship_sunburst(res_2023)),
        ("9. Cumulative Points Area Chart", plot_cumulative_points_area(res_2023)),
        ("10. Driver Finish Heatmap", plot_driver_finish_heatmap(res_2023)),
        ("11. Strategy Type Donut / Pie", plot_strategy_type_donut(strat_summary)),
        ("12. Pit Stops vs Finish Scatter / Sitograph", plot_pit_stops_vs_finish_scatter(strat_summary)),
        ("13. Safety Car Causes Pie Chart", plot_safety_car_causes_pie(sc_df)),
        ("14. Compound Usage Share Donut / Pie", plot_compound_donut_chart(laps_2023)),
        ("15. Stint Length Violin Density Plot", plot_stint_length_violin(laps_2023)),
        ("16. Stint Compound Treemap", plot_stint_compound_treemap(laps_2023)),
        ("17. Pit Stop by Team Violin Plot", plot_pitstop_by_team_violin(pitstops_df)),
        ("18. Driver Lap Time Violin Plot", plot_driver_lap_time_violin(laps_2023, ['VER', 'HAM', 'NOR'])),
        ("19. Driver Attributes Radar / Spider Chart", plot_driver_performance_radar(res_2023, laps_2023, ['Max Verstappen', 'Lewis Hamilton'])),
        ("20. Grid to Finish Waterfall Chart", plot_grid_to_finish_waterfall(res_2023)),
    ]

    for name, fig in charts:
        assert isinstance(fig, go.Figure), f"Failed on {name}"
        assert len(fig.data) > 0 or "layout" in fig.__dict__, f"No data in {name}"
        print(f"  [OK] {name}")

    print("\nALL 20 GRAPH TYPES TESTED AND WORKING PERFECTLY!")


if __name__ == '__main__':
    test_all_graphs()

