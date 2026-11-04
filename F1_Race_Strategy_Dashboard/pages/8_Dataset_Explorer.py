import streamlit as st
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from components.styling import apply_custom_css
from views import render_dataset_explorer

st.set_page_config(page_title="Dataset Explorer & Data Quality - F1 Analytics", page_icon="🔍", layout="wide")
apply_custom_css()

render_dataset_explorer()
