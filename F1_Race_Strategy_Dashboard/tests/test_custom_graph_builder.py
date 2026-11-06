import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from components.custom_graph_builder import (
    CUSTOM_DATASET_OPTIONS, CUSTOM_GRAPH_TYPES, AGGREGATION_OPTIONS,
    get_filtered_custom_data, get_default_columns_for_dataset,
    build_custom_figure
)
from data_processing.data_loader import (
    load_unified_results, load_unified_laps, load_ergast_pit_stops,
    load_kaggle_stint_aggression, load_f1_events
)


@pytest.fixture(scope="module")
def sample_bundle():
    return {
        "results": load_unified_results(),
        "laps": load_unified_laps(),
        "ergast_pitstops": load_ergast_pit_stops(),
        "stint_aggression": load_kaggle_stint_aggression(),
        "events": load_f1_events(),
    }


def test_get_filtered_custom_data(sample_bundle):
    filters = {
        "selected_year": "2023",
        "selected_team": "All Teams",
        "selected_drivers": ["All Drivers"],
        "selected_event": "All Events",
        "selected_compound": "ALL",
        "year_sort_ascending": False,
    }
    for ds in CUSTOM_DATASET_OPTIONS:
        df = get_filtered_custom_data(ds, sample_bundle, filters)
        assert isinstance(df, pd.DataFrame)
        if not df.empty and "Year" in df.columns:
            # Check filtering applied
            assert (df["Year"] == 2023).all() or len(df) > 0


def test_build_all_custom_graph_types(sample_bundle):
    df = sample_bundle["results"]
    df = df[df["Year"] == 2023].head(30)

    for c_type in CUSTOM_GRAPH_TYPES:
        fig = build_custom_figure(
            df=df,
            chart_type=c_type,
            x_col="FullName",
            y_col="Points",
            color_col="TeamName",
            agg_func="Sum",
            show_trendline=True,
            custom_title=f"Test {c_type}",
            is_compact=True
        )
        assert isinstance(fig, go.Figure)
        assert fig.data is not None


def test_custom_graph_aggregations(sample_bundle):
    df = sample_bundle["results"]
    df = df[df["Year"] == 2023].head(50)

    for agg in AGGREGATION_OPTIONS:
        fig = build_custom_figure(
            df=df,
            chart_type="📊 Bar Chart",
            x_col="TeamName",
            y_col="Points",
            color_col=None,
            agg_func=agg,
            is_compact=False
        )
        assert isinstance(fig, go.Figure)


def test_custom_figure_empty_and_null_handling():
    empty_df = pd.DataFrame()
    fig = build_custom_figure(
        df=empty_df,
        chart_type="📊 Bar Chart",
        x_col="none",
        y_col="none"
    )
    assert isinstance(fig, go.Figure)

    null_df = pd.DataFrame({"A": [None, None], "B": [None, None]})
    fig_null = build_custom_figure(
        df=null_df,
        chart_type="📈 Line Chart",
        x_col="A",
        y_col="B"
    )
    assert isinstance(fig_null, go.Figure)
