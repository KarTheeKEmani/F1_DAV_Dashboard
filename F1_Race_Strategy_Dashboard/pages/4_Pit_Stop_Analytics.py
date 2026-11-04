import streamlit as st
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from data_processing.data_loader import (
    load_f1_events, load_f1_results, load_f1_laps, load_ergast_pit_stops
)
from views import render_pit_stop_analytics

st.set_page_config(page_title="Pit Stop Analytics - F1 Analytics", page_icon="🛑", layout="wide")
apply_custom_css()

events_df = load_f1_events()
results_df = load_f1_results()
laps_df = load_f1_laps()
ergast_ps_df = load_ergast_pit_stops()

drivers_list = sorted(results_df['Abbreviation'].dropna().unique().tolist()) if not results_df.empty else []
teams_list = sorted(results_df['TeamName'].dropna().unique().tolist()) if not results_df.empty else []

filters = render_sidebar(events_df, drivers_list, teams_list)
data_bundle = {
    'events': events_df,
    'results': results_df,
    'laps': laps_df,
    'ergast_pitstops': ergast_ps_df
}
render_pit_stop_analytics(data_bundle, filters)
