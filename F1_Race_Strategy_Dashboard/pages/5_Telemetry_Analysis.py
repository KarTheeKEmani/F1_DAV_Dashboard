import streamlit as st
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from data_processing.data_loader import (
    load_f1_events, load_f1_results, load_f1_laps,
    load_fastest_laps_telemetry, load_round1_telemetry
)
from views import render_telemetry_analysis

st.set_page_config(page_title="Telemetry Analysis - F1 Analytics", page_icon="⚡", layout="wide")
apply_custom_css()

events_df = load_f1_events()
results_df = load_f1_results()
laps_df = load_f1_laps()
telem_fastest_df = load_fastest_laps_telemetry()
telem_r1_df = load_round1_telemetry()

drivers_list = sorted(results_df['Abbreviation'].dropna().unique().tolist()) if not results_df.empty else []
teams_list = sorted(results_df['TeamName'].dropna().unique().tolist()) if not results_df.empty else []

filters = render_sidebar(events_df, drivers_list, teams_list)
data_bundle = {
    'events': events_df,
    'results': results_df,
    'laps': laps_df,
    'fastest_laps_telemetry': telem_fastest_df,
    'round1_telemetry': telem_r1_df
}
render_telemetry_analysis(data_bundle, filters)
