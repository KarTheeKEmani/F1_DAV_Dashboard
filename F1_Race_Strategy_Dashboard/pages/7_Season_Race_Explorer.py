import streamlit as st
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from components.styling import apply_custom_css
from components.sidebar import render_sidebar
from data_processing.data_loader import (
    load_f1_events, load_f1_results, load_f1_laps
)
from views import render_season_race_explorer

st.set_page_config(page_title="Season & Race Explorer - F1 Analytics", page_icon="🗺️", layout="wide")
apply_custom_css()

events_df = load_f1_events()
results_df = load_f1_results()
laps_df = load_f1_laps()

drivers_list = sorted(results_df['Abbreviation'].dropna().unique().tolist()) if not results_df.empty else []
teams_list = sorted(results_df['TeamName'].dropna().unique().tolist()) if not results_df.empty else []

filters = render_sidebar(events_df, drivers_list, teams_list)
data_bundle = {
    'events': events_df,
    'results': results_df,
    'laps': laps_df
}
render_season_race_explorer(data_bundle, filters)
