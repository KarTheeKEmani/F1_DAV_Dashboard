import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, Tuple, List

from config import THEME_COLORS, TEAM_COLORS, TYRE_COMPOUND_COLORS
from components.styling import get_plotly_f1_layout
from data_processing.data_integration import apply_global_filters


CUSTOM_DATASET_OPTIONS = [
    "🏁 Race Results (Filtered)",
    "⏱️ Lap Times & Pace (Filtered)",
    "🛑 Pit Stops (Filtered)",
    "🛞 Tyre Stints & Strategy (Filtered)",
    "🏆 Driver Career & Standings",
]

CUSTOM_GRAPH_TYPES = [
    "📊 Bar Chart",
    "📈 Line Chart",
    "🟣 Scatter Plot / Sitograph",
    "🥧 Pie / Donut Chart",
    "📶 Histogram",
    "📦 Box Plot",
    "🎻 Violin Plot",
    "🌊 Area Chart",
]

AGGREGATION_OPTIONS = [
    "None (Raw Data)",
    "Sum",
    "Mean (Average)",
    "Count",
    "Max",
    "Min",
]


def get_filtered_custom_data(
    source_name: str,
    data_bundle: Dict[str, Any],
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """Retrieves and applies the active cascading filters to the selected dataset."""
    df = pd.DataFrame()

    if source_name == "🏁 Race Results (Filtered)":
        raw = data_bundle.get("results")
        if raw is not None and not raw.empty:
            df = apply_global_filters(raw, filters, apply_compound=False)
            for c in ["Position", "PositionOrder", "GridPosition", "Points", "Laps", "PositionsGained"]:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

    elif source_name == "⏱️ Lap Times & Pace (Filtered)":
        raw = data_bundle.get("laps")
        if raw is not None and not raw.empty:
            df = apply_global_filters(raw, filters, apply_compound=True)
            for c in ["LapNumber", "Stint", "TyreLife", "LapTimeSec", "Sector1TimeSec"]:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

    elif source_name == "🛑 Pit Stops (Filtered)":
        raw = data_bundle.get("ergast_pitstops")
        if raw is None or raw.empty:
            raw = data_bundle.get("pit_events")
        if raw is not None and not raw.empty:
            df = apply_global_filters(raw, filters, apply_compound=False)
            for c in ["stop", "lap", "DurationSec", "milliseconds", "stop_duration_s"]:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

    elif source_name == "🛞 Tyre Stints & Strategy (Filtered)":
        raw = data_bundle.get("stint_aggression")
        if raw is None or raw.empty:
            raw = data_bundle.get("strategy_dataset")
        if raw is not None and not raw.empty:
            df = apply_global_filters(raw, filters, apply_compound=False)
            for c in ["Laps", "Position", "TotalPitStops", "AvgPitStopTime", "Air_Temp_C"]:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

    elif source_name == "🏆 Driver Career & Standings":
        raw = data_bundle.get("gp_winners")
        if raw is None or raw.empty:
            raw = data_bundle.get("race_intelligence")
        if raw is not None and not raw.empty:
            df = apply_global_filters(raw, filters, apply_compound=False)

    return df if df is not None else pd.DataFrame()


def get_default_columns_for_dataset(df: pd.DataFrame, source_name: str) -> Tuple[str, str, Optional[str]]:
    """Chooses intelligent default X, Y, and Color columns based on dataset type."""
    cols = df.columns.tolist()

    if "Race Results" in source_name:
        x_default = "FullName" if "FullName" in cols else ("Driver" if "Driver" in cols else cols[0])
        y_default = "Points" if "Points" in cols else ("Position" if "Position" in cols else (cols[1] if len(cols) > 1 else cols[0]))
        color_default = "TeamName" if "TeamName" in cols else None
    elif "Lap Times" in source_name:
        x_default = "LapNumber" if "LapNumber" in cols else cols[0]
        y_default = "LapTimeSec" if "LapTimeSec" in cols else (cols[1] if len(cols) > 1 else cols[0])
        color_default = "Driver" if "Driver" in cols else ("Compound" if "Compound" in cols else None)
    elif "Pit Stops" in source_name:
        x_default = "TeamName" if "TeamName" in cols else ("Driver" if "Driver" in cols else cols[0])
        y_default = "DurationSec" if "DurationSec" in cols else (cols[1] if len(cols) > 1 else cols[0])
        color_default = "TeamName" if "TeamName" in cols else None
    else:
        x_default = cols[0] if cols else ""
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        y_default = num_cols[0] if num_cols else (cols[1] if len(cols) > 1 else (cols[0] if cols else ""))
        color_default = "TeamName" if "TeamName" in cols else None

    return x_default, y_default, color_default


def build_custom_figure(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    agg_func: str = "None (Raw Data)",
    show_trendline: bool = False,
    custom_title: Optional[str] = None,
    is_compact: bool = True
) -> go.Figure:
    """Builds a responsive, dark motorsport styled Plotly figure for selected data."""
    if df.empty or not x_col:
        fig = go.Figure()
        fig.add_annotation(
            text="No data matching current filters",
            showarrow=False,
            font=dict(color="#626d7f", size=13),
            xref="paper", yref="paper", x=0.5, y=0.5
        )
        layout_kwargs = get_plotly_f1_layout(
            title=custom_title or "No Data Available",
            height=320 if is_compact else 450
        )
        fig.update_layout(**layout_kwargs)
        return fig

    # Build workable copy
    plot_df = df.copy()

    # Drop NaNs in target columns
    check_cols = [x_col]
    if y_col and y_col in plot_df.columns and chart_type != "📶 Histogram":
        check_cols.append(y_col)
    if color_col and color_col in plot_df.columns:
        check_cols.append(color_col)
    plot_df = plot_df.dropna(subset=[c for c in check_cols if c in plot_df.columns])

    if plot_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="All values are null for chosen columns",
            showarrow=False,
            font=dict(color="#626d7f", size=13),
            xref="paper", yref="paper", x=0.5, y=0.5
        )
        fig.update_layout(**get_plotly_f1_layout(title="No Valid Data", height=320 if is_compact else 450))
        return fig

    # Aggregation if requested (for Bar, Line, Pie, Area)
    is_aggregated = False
    if agg_func != "None (Raw Data)" and y_col and y_col in plot_df.columns and pd.api.types.is_numeric_dtype(plot_df[y_col]):
        group_keys = [x_col]
        if color_col and color_col in plot_df.columns and color_col != x_col:
            group_keys.append(color_col)

        agg_dict = {
            "Sum": "sum",
            "Mean (Average)": "mean",
            "Count": "count",
            "Max": "max",
            "Min": "min"
        }
        py_func = agg_dict.get(agg_func, "mean")
        plot_df = plot_df.groupby(group_keys, as_index=False)[y_col].agg(py_func)
        is_aggregated = True

    # Color mapping for Teams & Compounds
    color_discrete_map = None
    if color_col in ["TeamName", "Team", "Constructor"]:
        color_discrete_map = TEAM_COLORS
    elif color_col in ["Compound", "CompoundCode"]:
        color_discrete_map = TYRE_COMPOUND_COLORS

    # Determine default title
    if not custom_title:
        clean_type = chart_type.split(" ", 1)[-1]
        agg_label = f" ({agg_func})" if is_aggregated else ""
        custom_title = f"{clean_type}: {y_col}{agg_label} by {x_col}"

    color_arg = color_col if (color_col and color_col != "None" and color_col in plot_df.columns) else None

    # Construct Chart by Type
    if "Bar" in chart_type:
        fig = px.bar(
            plot_df,
            x=x_col,
            y=y_col if y_col in plot_df.columns else None,
            color=color_arg,
            color_discrete_map=color_discrete_map,
            color_discrete_sequence=THEME_COLORS.get("chart_colors", px.colors.qualitative.Dark24),
            barmode="group",
            text_auto=".1f" if (is_aggregated and not is_compact) else False
        )

    elif "Line" in chart_type:
        sort_by = [color_arg, x_col] if color_arg else [x_col]
        plot_df = plot_df.sort_values(sort_by)
        fig = px.line(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_arg,
            color_discrete_map=color_discrete_map,
            color_discrete_sequence=THEME_COLORS.get("chart_colors", px.colors.qualitative.Dark24),
            markers=True
        )

    elif "Scatter" in chart_type or "Sitograph" in chart_type:
        # Check if trendline can be drawn
        trendline_mode = None
        trend_note = ""
        if show_trendline and pd.api.types.is_numeric_dtype(plot_df[x_col]) and pd.api.types.is_numeric_dtype(plot_df[y_col]):
            trendline_mode = "ols"
            r_val = plot_df[x_col].corr(plot_df[y_col])
            if not np.isnan(r_val):
                trend_note = f" (Pearson r = {r_val:+.2f})"

        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_arg,
            color_discrete_map=color_discrete_map,
            color_discrete_sequence=THEME_COLORS.get("chart_colors", px.colors.qualitative.Dark24),
            trendline=trendline_mode,
            trendline_color_override="#00d26a" if trendline_mode else None
        )
        custom_title += trend_note

    elif "Pie" in chart_type or "Donut" in chart_type:
        fig = px.pie(
            plot_df,
            names=x_col,
            values=y_col if (y_col in plot_df.columns and pd.api.types.is_numeric_dtype(plot_df[y_col])) else None,
            hole=0.45,
            color=color_arg,
            color_discrete_map=color_discrete_map,
            color_discrete_sequence=THEME_COLORS.get("chart_colors", px.colors.qualitative.Dark24)
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")

    elif "Histogram" in chart_type:
        fig = px.histogram(
            plot_df,
            x=x_col,
            y=y_col if (y_col in plot_df.columns and pd.api.types.is_numeric_dtype(plot_df[y_col])) else None,
            color=color_arg,
            color_discrete_map=color_discrete_map,
            color_discrete_sequence=THEME_COLORS.get("chart_colors", px.colors.qualitative.Dark24),
            marginal="box" if not is_compact else None
        )

    elif "Box" in chart_type:
        fig = px.box(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_arg,
            color_discrete_map=color_discrete_map,
            color_discrete_sequence=THEME_COLORS.get("chart_colors", px.colors.qualitative.Dark24),
            points="outliers"
        )

    elif "Violin" in chart_type:
        fig = px.violin(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_arg,
            color_discrete_map=color_discrete_map,
            color_discrete_sequence=THEME_COLORS.get("chart_colors", px.colors.qualitative.Dark24),
            box=True,
            points=False
        )

    elif "Area" in chart_type:
        sort_by = [color_arg, x_col] if color_arg else [x_col]
        plot_df = plot_df.sort_values(sort_by)
        fig = px.area(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_arg,
            color_discrete_map=color_discrete_map,
            color_discrete_sequence=THEME_COLORS.get("chart_colors", px.colors.qualitative.Dark24)
        )
    else:
        fig = px.bar(plot_df, x=x_col, y=y_col, color=color_arg)

    # Apply F1 dark theme styling
    chart_height = 340 if is_compact else 500
    base_layout = get_plotly_f1_layout(
        title=custom_title,
        height=chart_height
    )
    if "Pie" not in chart_type:
        if "xaxis" in base_layout:
            base_layout["xaxis"]["title"] = dict(text=x_col, font=dict(color="#ffffff", size=12))
        if "yaxis" in base_layout and y_col:
            base_layout["yaxis"]["title"] = dict(text=y_col, font=dict(color="#ffffff", size=12))

    if is_compact:
        base_layout["margin"] = dict(l=15, r=15, t=35, b=25)
        base_layout["showlegend"] = bool(color_arg)
        base_layout["legend"] = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9, color="#9aa4b2")
        )
        if "title" in base_layout and isinstance(base_layout["title"], dict):
            base_layout["title"]["font"] = dict(size=12, color="#ffffff")

    fig.update_layout(**base_layout)
    return fig


def render_sidebar_custom_graph_maker(
    data_bundle: Dict[str, Any],
    filters: Dict[str, Any]
) -> Tuple[Optional[go.Figure], Optional[Dict[str, Any]]]:
    """
    Renders the Custom Graph Maker section inside the Left Sidebar.
    Returns (plotly_fig, chart_config) if graph creation is enabled.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 GRAPH MAKER (SELECTED DATA)")

    with st.sidebar.expander("🛠️ Create Custom Graph", expanded=True):
        st.markdown(
            '<div style="font-size:0.75rem; color:#9aa4b2; margin-bottom:8px;">'
            'Generate real-time plots strictly filtered by your current <b>Year, Team, Driver & Grand Prix</b> selection.'
            '</div>',
            unsafe_allow_html=True
        )

        # 1. Select Dataset Source
        source_name = st.selectbox(
            "📁 Select Data Stream",
            CUSTOM_DATASET_OPTIONS,
            index=0,
            key="custom_graph_source"
        )

        filtered_df = get_filtered_custom_data(source_name, data_bundle, filters)
        row_count = len(filtered_df)

        # Show live count badge
        if row_count > 0:
            st.markdown(
                f'<div style="font-size:0.75rem; color:#00d26a; font-weight:600; margin-bottom:8px;">'
                f'⚡ {row_count:,} records in current filter'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 0 rows match current filters. Try selecting 'All Years' or 'All Teams'.")
            return None, None

        # 2. Select Chart Type
        chart_type = st.selectbox(
            "📈 Select Graph Type",
            CUSTOM_GRAPH_TYPES,
            index=0,
            key="custom_graph_type"
        )

        # 3. Dynamic Column Selectors based on dataset
        all_cols = filtered_df.columns.tolist()
        num_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = [c for c in all_cols if c not in num_cols]

        def_x, def_y, def_color = get_default_columns_for_dataset(filtered_df, source_name)

        x_index = all_cols.index(def_x) if def_x in all_cols else 0
        x_col = st.selectbox("📌 X-Axis Variable", all_cols, index=x_index, key="custom_graph_x")

        # Y-Axis (Histograms don't strictly require Y)
        y_options = num_cols if num_cols else all_cols
        y_index = y_options.index(def_y) if def_y in y_options else 0
        y_col = st.selectbox(
            "📊 Y-Axis Variable",
            y_options,
            index=y_index,
            key="custom_graph_y"
        )

        # 4. Color / Group By (Optional)
        color_choices = ["None"] + [c for c in ["TeamName", "Team", "Driver", "FullName", "Compound", "Year", "EventName"] if c in all_cols]
        # remove duplicate None or current x/y
        seen = set()
        clean_color_choices = []
        for c in color_choices:
            if c not in seen:
                seen.add(c)
                clean_color_choices.append(c)

        color_index = 0
        if def_color and def_color in clean_color_choices:
            color_index = clean_color_choices.index(def_color)

        color_col = st.selectbox(
            "🎨 Color / Group By",
            clean_color_choices,
            index=color_index,
            key="custom_graph_color"
        )
        color_val = None if color_col == "None" else color_col

        # 5. Aggregation Option (applicable for Bar, Line, Pie, Area)
        agg_func = "None (Raw Data)"
        if any(t in chart_type for t in ["Bar", "Line", "Pie", "Area"]):
            agg_func = st.selectbox(
                "🔢 Aggregation",
                AGGREGATION_OPTIONS,
                index=1 if "Bar" in chart_type else 0,
                key="custom_graph_agg"
            )

        # 6. Trendline toggle for Scatter
        show_trendline = False
        if "Scatter" in chart_type or "Sitograph" in chart_type:
            show_trendline = st.checkbox("📈 Show Linear Trendline (OLS)", value=True, key="custom_graph_trend")

        # 7. Custom Title (Optional)
        clean_type_name = chart_type.split(" ", 1)[-1]
        default_title = f"{clean_type_name}: {y_col} by {x_col}"
        custom_title = st.text_input("🏷️ Graph Title (Optional)", value=default_title, key="custom_graph_title")

        # 8. Main view mirror toggle
        show_in_main = st.checkbox("📌 Display at Top of Main Dashboard", value=True, key="custom_graph_show_main")

        # Build Sidebar Compact Figure
        sidebar_fig = build_custom_figure(
            df=filtered_df,
            chart_type=chart_type,
            x_col=x_col,
            y_col=y_col,
            color_col=color_val,
            agg_func=agg_func,
            show_trendline=show_trendline,
            custom_title=custom_title,
            is_compact=True
        )

        # Render immediately right inside the sidebar!
        st.markdown("##### 🔍 Preview in Left Dashboard:")
        st.plotly_chart(sidebar_fig, use_container_width=True, key="sidebar_custom_plot")

        chart_config = {
            "source_name": source_name,
            "chart_type": chart_type,
            "x_col": x_col,
            "y_col": y_col,
            "color_col": color_val,
            "agg_func": agg_func,
            "show_trendline": show_trendline,
            "custom_title": custom_title,
            "show_in_main": show_in_main,
            "row_count": row_count,
        }

        # Build Main View full-res figure if requested
        main_fig = None
        if show_in_main:
            main_fig = build_custom_figure(
                df=filtered_df,
                chart_type=chart_type,
                x_col=x_col,
                y_col=y_col,
                color_col=color_val,
                agg_func=agg_func,
                show_trendline=show_trendline,
                custom_title=custom_title,
                is_compact=False
            )

        return main_fig, chart_config


def render_main_custom_graph_card(fig: Optional[go.Figure], config: Optional[Dict[str, Any]]):
    """Renders a prominent, high-res interactive card for the custom graph at the top of the main dashboard."""
    if fig is None or not config or not config.get("show_in_main"):
        return

    st.markdown(
        '<div style="margin-top: 14px; margin-bottom: 10px;">'
        '<span style="background: linear-gradient(135deg, #e10600 0%, #b30000 100%); '
        'color: white; padding: 5px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.8px;">'
        '📊 CUSTOM GRAPH STUDIO — ACTIVE SELECTION'
        '</span>'
        '</div>',
        unsafe_allow_html=True
    )
    with st.expander(
        f"🎯 Full-Width View: {config.get('custom_title', 'Custom Graph')} ({config.get('row_count', 0):,} records)",
        expanded=True
    ):
        st.plotly_chart(fig, use_container_width=True, key=f"main_custom_graph_{config.get('chart_type')}")

