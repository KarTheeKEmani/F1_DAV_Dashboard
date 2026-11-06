import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from data_processing.data_loader import load_unified_results
from components.custom_graph_builder import render_sidebar_custom_graph_maker


NAV_OPTIONS = [
    "🏁 Race Overview",
    "⏱️ Race Strategy Analysis",
    "🛞 Tyre & Stint Analysis",
    "🛑 Pit Stop Analytics",
    "⚡ Lap-Time & Telemetry Analysis",
    "🏆 Driver & Team Performance",
    "🗺️ Season & Race Explorer",
    "🔍 Dataset Explorer & Data Quality",
]


def render_sidebar(
    events_df: pd.DataFrame,
    drivers_list: List[str],
    teams_list: List[str],
    unified_results_df: Optional[pd.DataFrame] = None,
    results_df: Optional[pd.DataFrame] = None,
    laps_df: Optional[pd.DataFrame] = None,
    data_bundle: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Renders the Top Horizontal Dashboard Navigation Bar at the top of the main page,
    the cascading Year, Team Name, Driver, Grand Prix, and Compound filters at the top of the sidebar,
    and the interactive Custom Graph Studio for selected data directly in the left dashboard.
    """
    if unified_results_df is None or unified_results_df.empty:
        unified_results_df = results_df if (results_df is not None and not results_df.empty) else load_unified_results()

    # 1. Top Horizontal Navigation Bar at the VERY TOP of the Main Dashboard
    selected_page = st.radio(
        "📌 Dashboard Navigation",
        NAV_OPTIONS,
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    # 2. Left Sidebar: Brand Header + Cascading Year, Team, Driver & GP Filters at the Top
    with st.sidebar:
        st.markdown(
            '<div class="f1-sidebar-brand">'
            '<div class="f1-brand-title">🏎️ F1 ANALYTICS</div>'
            '<div class="f1-brand-tagline">STRATEGY & TELEMETRY CONTROL</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown("##### 🎯 YEAR, TEAM & DRIVER FILTERS")

        # Build sorted Year options from unified dataset (1950 - 2026)
        if not unified_results_df.empty and "Year" in unified_results_df.columns:
            avail_years = sorted(unified_results_df["Year"].dropna().astype(int).unique().tolist(), reverse=True)
        else:
            avail_years = list(range(2026, 1949, -1))

        year_options = ["All Years"] + [str(y) for y in avail_years]
        selected_year = st.selectbox("📅 Select Year (Season)", year_options, index=0)

        # Year-wise sort order option
        sort_order_choice = st.selectbox(
            "🔃 Year-Wise Sort Order",
            ["Newest First (2026 -> 1950)", "Chronological (1950 -> 2026)"],
            index=0,
        )
        year_sort_ascending = sort_order_choice.startswith("Chronological")

        # Filter the reference dataframe by selected Year for cascading Team, Driver, and Event lists
        ref_df = unified_results_df.copy() if not unified_results_df.empty else pd.DataFrame()
        if selected_year != "All Years" and not ref_df.empty:
            ref_df = ref_df[ref_df["Year"] == int(selected_year)]

        # Team / Constructor filter (Cascading from Year)
        if not ref_df.empty and "TeamName" in ref_df.columns:
            cascaded_teams = sorted(ref_df["TeamName"].dropna().astype(str).unique().tolist())
        else:
            cascaded_teams = sorted(teams_list) if teams_list else []

        team_choices = ["All Teams"] + cascaded_teams
        selected_team = st.selectbox("🏎️ Select Team / Constructor", team_choices, index=0)

        # Filter reference dataframe by selected Team for cascading Driver list
        if selected_team != "All Teams" and not ref_df.empty:
            ref_df_drv = ref_df[ref_df["TeamName"] == selected_team]
        else:
            ref_df_drv = ref_df

        # Driver selector (Cascading from Year & Team, showing Full Name + Code)
        if not ref_df_drv.empty and {"FullName", "Abbreviation"}.issubset(ref_df_drv.columns):
            drv_pairs = (
                ref_df_drv[["FullName", "Abbreviation"]]
                .dropna()
                .drop_duplicates()
                .sort_values("FullName")
            )
            formatted_drivers = [f"{r['FullName']} ({r['Abbreviation']})" for _, r in drv_pairs.iterrows()]
        else:
            formatted_drivers = sorted(drivers_list) if drivers_list else []

        driver_choices = ["All Drivers"] + formatted_drivers
        selected_drivers = st.multiselect(
            "👤 Select Driver(s)",
            driver_choices,
            default=["All Drivers"],
        )
        if not selected_drivers:
            selected_drivers = ["All Drivers"]

        # Grand Prix Event selector (Cascading from Year)
        if not ref_df.empty and "EventName" in ref_df.columns:
            event_names = ["All Events"] + sorted(ref_df["EventName"].dropna().astype(str).unique().tolist())
        elif not events_df.empty and "EventName" in events_df.columns:
            event_names = ["All Events"] + sorted(events_df["EventName"].dropna().astype(str).unique().tolist())
        else:
            event_names = ["All Events"]

        selected_event = st.selectbox("📍 Select Grand Prix", event_names, index=0)

        # Tyre Compound filter
        compound_choices = ["ALL", "SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
        selected_compound = st.selectbox("🛞 Tyre Compound", compound_choices, index=0)

        # Reset button
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.rerun()

        # Build current filter dictionary for dynamic graph maker
        active_filters_for_graph = {
            "selected_year": selected_year,
            "selected_team": selected_team,
            "selected_drivers": selected_drivers,
            "selected_event": selected_event,
            "selected_compound": selected_compound,
            "year_sort_ascending": year_sort_ascending,
        }

        # Build fallback bundle if data_bundle wasn't fully supplied
        effective_bundle = data_bundle or {
            "events": events_df,
            "results": unified_results_df if (results_df is None or results_df.empty) else results_df,
            "laps": laps_df if laps_df is not None else pd.DataFrame(),
        }

        # Interactive Custom Graph Studio for Selected Data (rendered right in the Left Dashboard)
        custom_main_fig, custom_graph_config = render_sidebar_custom_graph_maker(
            data_bundle=effective_bundle,
            filters=active_filters_for_graph,
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-size: 0.73rem; color: #626d7f; line-height: 1.4;">'
            '<b>Datasets:</b> 14 Kaggle F1 Repositories (1950–2026) + FastF1 Telemetry<br>'
            '<b>Sorting:</b> Year-Wise Active'
            '</div>',
            unsafe_allow_html=True,
        )

    return {
        "selected_page": selected_page,
        "selected_year": selected_year,
        "selected_season": f"{selected_year} Season" if selected_year != "All Years" else "1950-2026 All Seasons",
        "year_sort_ascending": year_sort_ascending,
        "year_sort_desc": not year_sort_ascending,
        "selected_event": selected_event,
        "selected_drivers": selected_drivers,
        "selected_team": selected_team,
        "selected_compound": selected_compound,
        "custom_graph_fig": custom_main_fig,
        "custom_graph_config": custom_graph_config,
    }
