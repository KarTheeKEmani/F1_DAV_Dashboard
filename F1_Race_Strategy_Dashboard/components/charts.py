import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import THEME_COLORS, TYRE_COMPOUND_COLORS, TEAM_COLORS
from components.styling import get_plotly_f1_layout


def plot_race_finish_vs_grid(results_df: pd.DataFrame, title: str = "Grid Position vs Race Finish (Position Delta)") -> go.Figure:
    """Scatter plot comparing starting grid position with final finishing position."""
    if results_df.empty or 'GridPosition' not in results_df.columns or 'Position' not in results_df.columns:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Data Available"))
        return fig

    df = results_df.dropna(subset=['GridPosition', 'Position']).copy()
    df['PositionsGained'] = df['GridPosition'] - df['Position']

    fig = go.Figure()

    # Diagonal reference line (parity: finish = start)
    max_val = max(df['GridPosition'].max(), df['Position'].max(), 20)
    fig.add_trace(go.Scatter(
        x=[1, max_val],
        y=[1, max_val],
        mode='lines',
        name='Maintained Position',
        line=dict(color='#4b5563', dash='dash', width=1.5),
        hoverinfo='skip'
    ))

    # Drivers scatter
    for team, grp in df.groupby('TeamName' if 'TeamName' in df.columns else 'Team'):
        color = TEAM_COLORS.get(team, '#9aa4b2')
        driver_text = grp['FullName'] if 'FullName' in grp.columns else grp['Driver']
        hover_txt = [
            f"<b>{d}</b> ({team})<br>Grid: P{int(g)} ➔ Finish: P{int(p)}<br>Delta: {'+' if dg > 0 else ''}{int(dg)}"
            for d, g, p, dg in zip(driver_text, grp['GridPosition'], grp['Position'], grp['PositionsGained'])
        ]
        fig.add_trace(go.Scatter(
            x=grp['GridPosition'],
            y=grp['Position'],
            mode='markers+text',
            name=team,
            text=grp['Abbreviation'] if 'Abbreviation' in grp.columns else grp['Driver'],
            textposition='top center',
            textfont=dict(size=10, color='#ffffff'),
            marker=dict(
                size=12,
                color=color,
                line=dict(width=1.5, color='#ffffff')
            ),
            hovertext=hover_txt,
            hoverinfo='text'
        ))

    layout = get_plotly_f1_layout(title, height=450)
    layout['xaxis']['title'] = "Starting Grid Position"
    layout['yaxis']['title'] = "Finishing Position"
    layout['xaxis']['autorange'] = 'reversed'
    layout['yaxis']['autorange'] = 'reversed'
    fig.update_layout(layout)
    return fig


def plot_driver_standings(results_df: pd.DataFrame, title: str = "Driver Championship Standings") -> go.Figure:
    """Horizontal bar chart of driver points colored by team."""
    if results_df.empty:
        return go.Figure()

    standings = (
        results_df.groupby(['Abbreviation', 'FullName', 'TeamName'])['Points']
        .sum()
        .reset_index()
        .sort_values('Points', ascending=True)
    )

    colors = [TEAM_COLORS.get(t, '#e10600') for t in standings['TeamName']]

    fig = go.Figure(go.Bar(
        x=standings['Points'],
        y=standings['FullName'],
        orientation='h',
        marker=dict(color=colors, line=dict(color='#ffffff', width=0.5)),
        text=standings['Points'].apply(lambda x: f"{x:.0f} pts"),
        textposition='outside',
        textfont=dict(color='#ffffff', size=11),
        hovertemplate="<b>%{y}</b><br>Team: %{customdata}<br>Points: %{x}<extra></extra>",
        customdata=standings['TeamName']
    ))

    layout = get_plotly_f1_layout(title, height=max(400, len(standings) * 24))
    layout['xaxis']['title'] = "Total Championship Points"
    layout['yaxis']['title'] = ""
    fig.update_layout(layout)
    return fig


def plot_stint_timeline(laps_df: pd.DataFrame, title: str = "Race Tyre Stint & Pit Stop Strategy Timeline") -> go.Figure:
    """Timeline / Gantt chart representing tyre stints and pit stops across laps for each driver."""
    if laps_df.empty or 'Stint' not in laps_df.columns:
        return go.Figure()

    stints = (
        laps_df.dropna(subset=['Stint', 'LapNumber'])
        .groupby(['Driver', 'Stint', 'Compound'])
        .agg(
            StartLap=('LapNumber', 'min'),
            EndLap=('LapNumber', 'max'),
            LapsCount=('LapNumber', 'count')
        )
        .reset_index()
    )

    if stints.empty:
        return go.Figure()

    # Sort drivers by their finish or starting position
    drivers_ordered = stints.groupby('Driver')['EndLap'].max().sort_values(ascending=False).index.tolist()

    fig = go.Figure()

    for comp in ['SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET', 'UNKNOWN']:
        c_stints = stints[stints['Compound'] == comp]
        if c_stints.empty:
            continue
        c_color = TYRE_COMPOUND_COLORS.get(comp, '#6b7280')

        for _, row in c_stints.iterrows():
            fig.add_trace(go.Bar(
                y=[row['Driver']],
                x=[row['LapsCount']],
                base=[row['StartLap'] - 1],
                orientation='h',
                name=comp,
                marker=dict(
                    color=c_color,
                    line=dict(color='#131822', width=2)
                ),
                text=f"{comp[:1]} ({int(row['LapsCount'])}L)",
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(color='#000000' if comp in ['MEDIUM', 'HARD'] else '#ffffff', size=10, family="JetBrains Mono"),
                hovertemplate=f"<b>{row['Driver']}</b><br>Stint {int(row['Stint'])}: {comp}<br>Laps: {int(row['StartLap'])} - {int(row['EndLap'])} ({int(row['LapsCount'])} laps)<extra></extra>",
                showlegend=(row['Driver'] == drivers_ordered[0] and row['Stint'] == 1)
            ))

    layout = get_plotly_f1_layout(title, height=max(450, len(drivers_ordered) * 26))
    layout['barmode'] = 'stack'
    layout['xaxis']['title'] = "Race Lap Number"
    layout['yaxis']['title'] = "Driver"
    layout['yaxis']['categoryorder'] = 'array'
    layout['yaxis']['categoryarray'] = drivers_ordered[::-1]
    fig.update_layout(layout)
    return fig


def plot_tyre_degradation(laps_df: pd.DataFrame, title: str = "Tyre Pace Degradation (Lap Time vs Tyre Age)") -> go.Figure:
    """Scatter with linear trendlines showing lap time degradation per compound."""
    if laps_df.empty or 'TyreLife' not in laps_df.columns or 'LapTimeSec' not in laps_df.columns:
        return go.Figure()

    clean = laps_df[
        (~laps_df.get('IsOutlierLap', False)) &
        (laps_df['TyreLife'] > 1) &
        (laps_df['TyreLife'] < 42) &
        (laps_df['LapTimeSec'] > 50) &
        (laps_df['LapTimeSec'] < 140)
    ].copy()

    if clean.empty:
        return go.Figure()

    fig = go.Figure()

    for comp in ['SOFT', 'MEDIUM', 'HARD']:
        c_df = clean[clean['Compound'] == comp]
        if len(c_df) < 10:
            continue
        c_color = TYRE_COMPOUND_COLORS.get(comp, '#ffffff')

        # Scatter samples
        fig.add_trace(go.Scatter(
            x=c_df['TyreLife'],
            y=c_df['LapTimeSec'],
            mode='markers',
            name=f"{comp} Laps",
            marker=dict(color=c_color, size=6, opacity=0.35),
            hovertemplate=f"<b>{comp}</b><br>Tyre Life: %{{x}} laps<br>Lap Time: %{{y:.3f}}s<extra></extra>"
        ))

        # Linear trendline
        x_vals = c_df['TyreLife'].values
        y_vals = c_df['LapTimeSec'].values
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
        x_trend = np.linspace(x_vals.min(), x_vals.max(), 30)
        y_trend = slope * x_trend + intercept

        fig.add_trace(go.Scatter(
            x=x_trend,
            y=y_trend,
            mode='lines',
            name=f"{comp} Trend (+{slope:.3f} s/lap)",
            line=dict(color=c_color, width=3),
            hoverinfo='skip'
        ))

    layout = get_plotly_f1_layout(title, height=440)
    layout['xaxis']['title'] = "Tyre Life (Laps Completed on Set)"
    layout['yaxis']['title'] = "Lap Time (Seconds)"
    fig.update_layout(layout)
    return fig


def plot_lap_pace_progression(laps_df: pd.DataFrame, drivers: list = None, title: str = "Lap-by-Lap Pace Progression") -> go.Figure:
    """Lap time progression across the Grand Prix for selected drivers."""
    if laps_df.empty or 'LapNumber' not in laps_df.columns:
        return go.Figure()

    df = laps_df.copy()
    if drivers:
        df = df[df['Driver'].isin(drivers)]

    # Filter out pit laps from lines but show pit markers
    clean_laps = df[df['LapTimeSec'] > 0].copy()

    fig = go.Figure()

    for driver, d_grp in clean_laps.groupby('Driver'):
        d_grp = d_grp.sort_values('LapNumber')
        # pick color
        team = d_grp['Team'].iloc[0] if 'Team' in d_grp.columns else ''
        color = TEAM_COLORS.get(team, '#00b2fe')

        fig.add_trace(go.Scatter(
            x=d_grp['LapNumber'],
            y=d_grp['LapTimeSec'],
            mode='lines+markers',
            name=driver,
            line=dict(width=2, color=color),
            marker=dict(size=4, color=color),
            hovertemplate=f"<b>{driver}</b><br>Lap: %{{x}}<br>Time: %{{y:.3f}}s<br>Compound: %{{customdata}}<extra></extra>",
            customdata=d_grp['Compound']
        ))

    layout = get_plotly_f1_layout(title, height=450)
    layout['xaxis']['title'] = "Lap Number"
    layout['yaxis']['title'] = "Lap Time (Seconds)"
    fig.update_layout(layout)
    return fig


def plot_telemetry_traces(telem_df: pd.DataFrame, title: str = "High-Frequency Telemetry Comparison") -> go.Figure:
    """
    Subplots displaying synchronized Speed, Throttle %, Brake, and Gear
    against Track Distance (meters).
    """
    if telem_df.empty:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Telemetry Available"))
        return fig

    # Create 3 synchronized subplots: Speed, Throttle/Brake, Gear
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.5, 0.3, 0.2],
        subplot_titles=("Speed (km/h)", "Throttle (%) & Brake", "Gear")
    )

    x_col = 'Distance' if 'Distance' in telem_df.columns else 'TimeSec'
    x_label = "Distance (meters)" if x_col == 'Distance' else "Time (seconds)"

    drivers = telem_df['DriverCode'].unique() if 'DriverCode' in telem_df.columns else telem_df['DriverNumber'].unique()

    palette = ['#e10600', '#00b2fe', '#ffd600', '#00d26a']

    for i, d in enumerate(drivers):
        d_sub = telem_df[(telem_df['DriverCode' if 'DriverCode' in telem_df.columns else 'DriverNumber'] == d)].sort_values(x_col)
        c = palette[i % len(palette)]
        name_label = str(d)

        # 1. Speed trace
        fig.add_trace(go.Scatter(
            x=d_sub[x_col],
            y=d_sub['Speed'],
            mode='lines',
            name=f"{name_label} Speed",
            line=dict(color=c, width=2),
            hovertemplate=f"<b>{name_label}</b>: %{{y}} km/h<extra></extra>"
        ), row=1, col=1)

        # 2. Throttle trace
        fig.add_trace(go.Scatter(
            x=d_sub[x_col],
            y=d_sub['Throttle'],
            mode='lines',
            name=f"{name_label} Throttle",
            line=dict(color=c, width=1.5, dash='solid'),
            hovertemplate=f"<b>{name_label} Throttle</b>: %{{y}}%<extra></extra>"
        ), row=2, col=1)

        # 2. Brake trace (binary step or shaded)
        if 'Brake' in d_sub.columns:
            brake_y = d_sub['Brake'].astype(int) * 100
            fig.add_trace(go.Scatter(
                x=d_sub[x_col],
                y=brake_y,
                mode='lines',
                name=f"{name_label} Brake",
                line=dict(color='#ff1801' if i == 0 else '#ff8000', width=1, dash='dot'),
                hovertemplate=f"<b>{name_label} Brake</b>: %{{y}}%<extra></extra>"
            ), row=2, col=1)

        # 3. Gear trace
        if 'nGear' in d_sub.columns:
            fig.add_trace(go.Scatter(
                x=d_sub[x_col],
                y=d_sub['nGear'],
                mode='lines',
                name=f"{name_label} Gear",
                line=dict(color=c, width=1.5, shape='hv'),
                hovertemplate=f"<b>{name_label} Gear</b>: %{{y}}<extra></extra>"
            ), row=3, col=1)

    base_layout = get_plotly_f1_layout(title, height=600)
    base_layout.pop('xaxis', None)
    base_layout.pop('yaxis', None)
    fig.update_layout(base_layout)
    fig.update_xaxes(title_text=x_label, row=3, col=1, gridcolor="#222b3a")
    fig.update_xaxes(gridcolor="#222b3a", row=1, col=1)
    fig.update_xaxes(gridcolor="#222b3a", row=2, col=1)
    fig.update_yaxes(title_text="km/h", row=1, col=1, gridcolor="#222b3a")
    fig.update_yaxes(title_text="%", row=2, col=1, gridcolor="#222b3a")
    fig.update_yaxes(title_text="Gear", row=3, col=1, gridcolor="#222b3a")
    return fig


def plot_pitstop_distribution(pitstops_df: pd.DataFrame, title: str = "Pit Stop Stationary Duration Distribution") -> go.Figure:
    """Histogram & box plot showing distribution of stationary pit stop times."""
    if pitstops_df.empty or 'DurationSec' not in pitstops_df.columns:
        return go.Figure()

    clean = pitstops_df[
        (pitstops_df['DurationSec'] >= 1.5) &
        (pitstops_df['DurationSec'] <= 15.0)
    ].copy()

    if clean.empty:
        return go.Figure()

    fig = go.Figure()

    # Histogram
    fig.add_trace(go.Histogram(
        x=clean['DurationSec'],
        nbinsx=40,
        marker=dict(color='#e10600', line=dict(color='#131822', width=1)),
        name='Stops Count',
        hovertemplate="Duration: %{x:.2f}s<br>Count: %{y}<extra></extra>"
    ))

    # Median line
    med_val = clean['DurationSec'].median()
    fig.add_vline(
        x=med_val,
        line_width=2,
        line_dash="dash",
        line_color="#ffd600",
        annotation_text=f"Median: {med_val:.2f}s",
        annotation_position="top right",
        annotation_font=dict(color="#ffd600", size=12)
    )

    layout = get_plotly_f1_layout(title, height=400)
    layout['xaxis']['title'] = "Pit Stop Stationary Duration (Seconds)"
    layout['yaxis']['title'] = "Number of Pit Stops"
    fig.update_layout(layout)
    return fig


def plot_strategy_simulation(lap_df: pd.DataFrame, title: str = "Simulated Strategy Pace & Pit Window Crossover") -> go.Figure:
    """
    Subplots comparing simulated lap-by-lap pace and cumulative race gap
    across competing pit strategies.
    """
    if lap_df.empty:
        return go.Figure()

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        row_heights=[0.55, 0.45],
        subplot_titles=("Simulated Lap Time (s) per Lap", "Cumulative Time Gap to Leader (s)")
    )

    palette = ['#e10600', '#00b2fe', '#ffd600', '#00d26a']
    strategies = lap_df['Strategy'].unique()

    # Determine reference leading strategy cumulative time per lap
    min_cum = lap_df.groupby('LapNumber')['CumulativeTimeSec'].min()

    for idx, strat in enumerate(strategies):
        s_data = lap_df[lap_df['Strategy'] == strat].sort_values('LapNumber')
        c = palette[idx % len(palette)]

        # 1. Lap Pace trace
        fig.add_trace(go.Scatter(
            x=s_data['LapNumber'],
            y=s_data['LapTimeSec'],
            mode='lines',
            name=strat,
            line=dict(color=c, width=2.5),
            hovertemplate=f"<b>{strat}</b><br>Lap %{{x}}: %{{y:.3f}}s<extra></extra>"
        ), row=1, col=1)

        # 2. Cumulative Gap trace
        gaps = s_data['CumulativeTimeSec'].values - min_cum.loc[s_data['LapNumber']].values
        fig.add_trace(go.Scatter(
            x=s_data['LapNumber'],
            y=gaps,
            mode='lines',
            name=f"{strat} Gap",
            line=dict(color=c, width=2, dash='dot'),
            showlegend=False,
            hovertemplate=f"<b>{strat}</b><br>Gap: +%{{y:.2f}}s<extra></extra>"
        ), row=2, col=1)

    base_layout = get_plotly_f1_layout(title, height=520)
    base_layout.pop('xaxis', None)
    base_layout.pop('yaxis', None)
    fig.update_layout(base_layout)
    fig.update_xaxes(title_text="Race Lap Number", row=2, col=1, gridcolor="#222b3a")
    fig.update_xaxes(gridcolor="#222b3a", row=1, col=1)
    fig.update_yaxes(title_text="Lap Time (s)", row=1, col=1, gridcolor="#222b3a")
    fig.update_yaxes(title_text="Gap (s)", row=2, col=1, gridcolor="#222b3a")
    return fig
