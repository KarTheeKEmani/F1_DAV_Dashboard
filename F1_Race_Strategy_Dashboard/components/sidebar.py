import streamlit as st
import pandas as pd
from typing import Dict, Any, List


def render_sidebar(events_df: pd.DataFrame, drivers_list: List[str], teams_list: List[str]) -> Dict[str, Any]:
    """
    Renders the Formula 1 pit-wall sidebar navigation and cascading filters.
    Returns dictionary with all user selections.
    """
    with st.sidebar:
        st.markdown(
            """
            <div class="f1-sidebar-brand">
                <div class="f1-brand-title">🏁 F1 TELEMETRY</div>
                <div class="f1-brand-tagline">RACE STRATEGY PLATFORM</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 1. Navigation Menu
        st.markdown("### 📌 CONTROL CENTER")
        nav_options = [
            "🏁 Race Overview",
            "⏱️ Race Strategy Analysis",
            "🛞 Tyre & Stint Analysis",
            "🛑 Pit Stop Analytics",
            "⚡ Lap-Time & Telemetry Analysis",
            "🏆 Driver & Team Performance",
            "🗺️ Season & Race Explorer",
            "🔍 Dataset Explorer & Data Quality",
        ]
        selected_page = st.radio("Navigate Section", nav_options, index=0, label_visibility="collapsed")

        st.markdown("---")
        st.markdown("### ⚙️ RACE FILTERS")

        # Season selector
        season_options = ["2023 (FastF1 Official)", "2021-2024 (Multi-Year Strategy)", "Historical (1950-2024 Ergast)"]
        selected_season = st.selectbox("Season Dataset", season_options, index=0)

        # Grand Prix Event selector (Cascading)
        if not events_df.empty and 'EventName' in events_df.columns:
            event_names = ["All Events"] + sorted(events_df['EventName'].dropna().unique().tolist())
            selected_event = st.selectbox("Grand Prix", event_names, index=0)
        else:
            selected_event = "All Events"

        # Driver Multi-select
        driver_choices = ["All Drivers"] + sorted(drivers_list) if drivers_list else ["All Drivers"]
        selected_drivers = st.multiselect("Drivers", driver_choices, default=["All Drivers"])

        # Team / Constructor filter
        team_choices = ["All Teams"] + sorted(teams_list) if teams_list else ["All Teams"]
        selected_team = st.selectbox("Team / Constructor", team_choices, index=0)

        # Tyre Compound filter
        compound_choices = ["ALL", "SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
        selected_compound = st.selectbox("Tyre Compound", compound_choices, index=0)

        # Reset button
        st.markdown("")
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()

        # Footer Badge
        st.markdown("---")
        st.markdown(
            """
            <div style="font-size: 0.75rem; color: #626d7f; line-height: 1.4;">
                <b>Project:</b> Formula 1 Telemetry Platform<br>
                <b>Data:</b> FastF1 2023, Ergast DB, Strategy Stints<br>
                <b>Status:</b> Live Race Analytics Ready
            </div>
            """,
            unsafe_allow_html=True
        )

    return {
        "selected_page": selected_page,
        "selected_season": selected_season,
        "selected_event": selected_event,
        "selected_drivers": selected_drivers,
        "selected_team": selected_team,
        "selected_compound": selected_compound
    }
