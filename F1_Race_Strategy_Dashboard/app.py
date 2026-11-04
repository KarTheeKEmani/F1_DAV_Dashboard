import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# Streamlit Page Config - Direct Dashboard Load (NO LOGIN)
st.set_page_config(
    page_title="F1 Race Strategy & Telemetry Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from data_processing.data_loader import (
    load_f1_events, load_f1_results, load_f1_laps,
    load_f1_fastest_laps, load_f1_weather, load_strategy_dataset,
    load_ergast_pit_stops, load_fastest_laps_telemetry, load_round1_telemetry
)
from views import (
    render_race_overview, render_race_strategy, render_tyre_analysis,
    render_pit_stop_analytics, render_telemetry_analysis,
    render_driver_team_performance, render_season_race_explorer,
    render_dataset_explorer
)


def main():
    # Apply Motorsport Dark Pit-Wall CSS Theme
    apply_custom_css()

    # Load core datasets with caching
    with st.spinner("Initializing Formula 1 telemetry streams & strategy datasets..."):
        events_df = load_f1_events()
        results_df = load_f1_results()
        laps_df = load_f1_laps()
        fastest_laps_df = load_f1_fastest_laps()
        weather_df = load_f1_weather()
        strategy_df = load_strategy_dataset()
        ergast_ps_df = load_ergast_pit_stops()
        telem_fastest_df = load_fastest_laps_telemetry()
        telem_r1_df = load_round1_telemetry()

    # Prepare drivers and teams lists for cascading filters
    drivers_list = sorted(results_df['Abbreviation'].dropna().unique().tolist()) if not results_df.empty else []
    teams_list = sorted(results_df['TeamName'].dropna().unique().tolist()) if not results_df.empty else []

    # Render Sidebar with Navigation and Cascading Filters
    filters = render_sidebar(events_df, drivers_list, teams_list)

    # Pack data dictionary
    data_bundle = {
        'events': events_df,
        'results': results_df,
        'laps': laps_df,
        'fastest_laps': fastest_laps_df,
        'weather': weather_df,
        'strategy_dataset': strategy_df,
        'ergast_pitstops': ergast_ps_df,
        'fastest_laps_telemetry': telem_fastest_df,
        'round1_telemetry': telem_r1_df
    }

    # Dispatch to Selected View
    page = filters['selected_page']

    if page == "🏁 Race Overview":
        render_race_overview(data_bundle, filters)
    elif page == "⏱️ Race Strategy Analysis":
        render_race_strategy(data_bundle, filters)
    elif page == "🛞 Tyre & Stint Analysis":
        render_tyre_analysis(data_bundle, filters)
    elif page == "🛑 Pit Stop Analytics":
        render_pit_stop_analytics(data_bundle, filters)
    elif page == "⚡ Lap-Time & Telemetry Analysis":
        render_telemetry_analysis(data_bundle, filters)
    elif page == "🏆 Driver & Team Performance":
        render_driver_team_performance(data_bundle, filters)
    elif page == "🗺️ Season & Race Explorer":
        render_season_race_explorer(data_bundle, filters)
    elif page == "🔍 Dataset Explorer & Data Quality":
        render_dataset_explorer()


if __name__ == "__main__":
    main()
