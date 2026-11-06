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
    df = df[(df['GridPosition'] > 0) & (df['Position'] > 0)]
    if df.empty:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Valid Grid/Finish Records for Filter Selection"))
        return fig
    if len(df) > 250:
        df = df.head(250).copy()
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
        results_df.groupby(['FullName', 'TeamName'], as_index=False)['Points']
        .sum()
        .query("Points > 0")
        .sort_values('Points', ascending=True)
        .tail(25)
    )
    if standings.empty:
        standings = (
            results_df.groupby(['FullName', 'TeamName'], as_index=False)['Points']
            .sum()
            .sort_values('Points', ascending=True)
            .tail(20)
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

    work_laps = laps_df.dropna(subset=['Stint', 'LapNumber']).copy()
    if 'Year' in work_laps.columns and work_laps['Year'].nunique() > 1:
        latest_yr = work_laps['Year'].max()
        work_laps = work_laps[work_laps['Year'] == latest_yr]
    if 'EventName' in work_laps.columns and work_laps['EventName'].nunique() > 1:
        first_ev = work_laps['EventName'].iloc[0]
        work_laps = work_laps[work_laps['EventName'] == first_ev]

    stints = (
        work_laps
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

        # Scatter samples (cap visual scatter markers for smooth UI rendering)
        c_sample = c_df.sample(min(len(c_df), 1200), random_state=42) if len(c_df) > 1200 else c_df
        fig.add_trace(go.Scatter(
            x=c_sample['TyreLife'],
            y=c_sample['LapTimeSec'],
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
    if 'Year' in df.columns and df['Year'].nunique() > 1:
        df = df[df['Year'] == df['Year'].max()]
    if 'EventName' in df.columns and df['EventName'].nunique() > 1:
        df = df[df['EventName'] == df['EventName'].iloc[0]]
    if drivers:
        df = df[df['Driver'].isin(drivers) | (df['FullName'].isin(drivers) if 'FullName' in df.columns else False)]

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


# =====================================================================
# DIVERSE VISUALIZATION EXTENSIONS (PIE, DONUT, VIOLIN, HEATMAP,
# SUNBURST, TREEMAP, RADAR/SPIDER, WATERFALL, SITOGRAPH/SCATTER)
# =====================================================================

def plot_constructor_points_donut(results_df: pd.DataFrame, title: str = "Constructor Points Share (Donut Chart)") -> go.Figure:
    """Donut chart showing constructor championship points percentage distribution."""
    if results_df.empty or 'TeamName' not in results_df.columns or 'Points' not in results_df.columns:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Constructor Data Available"))
        return fig

    team_pts = results_df.groupby('TeamName', as_index=False)['Points'].sum()
    team_pts = team_pts[team_pts['Points'] > 0].sort_values('Points', ascending=False)
    if team_pts.empty:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Points Scored"))
        return fig

    colors = [TEAM_COLORS.get(t, '#9aa4b2') for t in team_pts['TeamName']]

    fig = go.Figure(go.Pie(
        labels=team_pts['TeamName'],
        values=team_pts['Points'],
        hole=0.48,
        marker=dict(colors=colors, line=dict(color='#0a0d12', width=2)),
        textinfo='label+percent',
        textfont=dict(color='#ffffff', size=11),
        hovertemplate="<b>%{label}</b><br>Points: %{value:.0f} (%{percent})<extra></extra>"
    ))

    layout = get_plotly_f1_layout(title, height=390)
    layout['showlegend'] = True
    fig.update_layout(layout)
    return fig


def plot_championship_sunburst(results_df: pd.DataFrame, title: str = "Championship Hierarchy: Constructor ➔ Driver (Sunburst)") -> go.Figure:
    """Sunburst chart visualizing the two-tier hierarchy of Constructor -> Driver -> Points."""
    if results_df.empty or not {'TeamName', 'FullName', 'Points'}.issubset(results_df.columns):
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Hierarchy Data Available"))
        return fig

    agg = results_df.groupby(['TeamName', 'FullName'], as_index=False)['Points'].sum()
    agg = agg[agg['Points'] > 0]
    if agg.empty:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Points Records"))
        return fig

    fig = px.sunburst(
        agg,
        path=['TeamName', 'FullName'],
        values='Points',
        color='TeamName',
        color_discrete_map=TEAM_COLORS,
        title=title
    )
    layout = get_plotly_f1_layout(title, height=430)
    fig.update_layout(layout)
    fig.update_traces(textinfo='label+value', hovertemplate="<b>%{label}</b><br>Points: %{value}<extra></extra>")
    return fig


def plot_cumulative_points_area(results_df: pd.DataFrame, top_n: int = 6, title: str = "Cumulative Points Progression (Area Chart)") -> go.Figure:
    """Filled area/line chart showing driver points accumulation round-by-round."""
    if results_df.empty or not {'RoundNumber', 'FullName', 'Points'}.issubset(results_df.columns):
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Cumulative Data Available"))
        return fig

    # Pick top N drivers by total points
    top_drivers = (
        results_df.groupby('FullName')['Points'].sum()
        .sort_values(ascending=False).head(top_n).index.tolist()
    )
    if not top_drivers:
        return go.Figure()

    df_sub = results_df[results_df['FullName'].isin(top_drivers)].copy()
    df_sub['RoundNumber'] = pd.to_numeric(df_sub['RoundNumber'], errors='coerce')
    df_sub = df_sub.dropna(subset=['RoundNumber']).sort_values('RoundNumber')

    fig = go.Figure()
    palette = ['#e10600', '#00b2fe', '#ffd600', '#00d26a', '#ff8000', '#c0c0c0', '#9aa4b2']

    for i, drv in enumerate(top_drivers):
        drv_df = df_sub[df_sub['FullName'] == drv].groupby('RoundNumber', as_index=False)['Points'].sum().sort_values('RoundNumber')
        drv_df['CumPoints'] = drv_df['Points'].cumsum()
        c = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=drv_df['RoundNumber'],
            y=drv_df['CumPoints'],
            mode='lines+markers',
            name=drv,
            line=dict(color=c, width=2.5),
            marker=dict(size=5),
            hovertemplate=f"<b>{drv}</b><br>Round %{{x}}: %{{y:.0f}} pts<extra></extra>"
        ))

    layout = get_plotly_f1_layout(title, height=380)
    layout['xaxis']['title'] = "Grand Prix Round Number"
    layout['yaxis']['title'] = "Cumulative Championship Points"
    fig.update_layout(layout)
    return fig


def plot_driver_finish_heatmap(results_df: pd.DataFrame, top_n: int = 14, title: str = "Driver Finishing Position Matrix (Heatmap)") -> go.Figure:
    """Heatmap showing driver finishing positions across championship rounds/races."""
    if results_df.empty or not {'FullName', 'Position'}.issubset(results_df.columns):
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Heatmap Data Available"))
        return fig

    round_col = 'RoundNumber' if 'RoundNumber' in results_df.columns else ('round' if 'round' in results_df.columns else None)
    if not round_col:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("Round numbers unavailable"))
        return fig

    # Filter to top N drivers by points or frequency
    top_drvs = (
        results_df.groupby('FullName')['Points'].sum()
        .sort_values(ascending=False).head(top_n).index.tolist()
        if 'Points' in results_df.columns
        else results_df['FullName'].value_counts().head(top_n).index.tolist()
    )

    sub = results_df[results_df['FullName'].isin(top_drvs)].copy()
    sub = sub.dropna(subset=['Position', round_col])
    sub['Position'] = pd.to_numeric(sub['Position'], errors='coerce')
    sub[round_col] = pd.to_numeric(sub[round_col], errors='coerce')
    sub = sub.dropna(subset=['Position', round_col])

    if sub.empty:
        return go.Figure()

    pivot = sub.pivot_table(index='FullName', columns=round_col, values='Position', aggfunc='min')
    pivot = pivot.reindex(top_drvs)

    text_vals = np.where(
        np.isnan(pivot.values),
        "-",
        np.nan_to_num(pivot.values, nan=0).astype(int).astype(str)
    )
    text_vals = np.where(text_vals == "0", "-", text_vals)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"R{int(c)}" for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale='Viridis',
        reversescale=True,
        text=text_vals,
        texttemplate="%{text}",
        textfont=dict(color="#ffffff", size=10, family="JetBrains Mono"),
        colorbar=dict(title="Finish Pos", tickvals=[1, 5, 10, 15, 20]),
        hovertemplate="Driver: <b>%{y}</b><br>Round: %{x}<br>Finish: P%{z}<extra></extra>"
    ))

    layout = get_plotly_f1_layout(title, height=max(360, len(top_drvs) * 26))
    layout['xaxis']['title'] = "Championship Round"
    layout['yaxis']['title'] = ""
    fig.update_layout(layout)
    return fig


def plot_strategy_type_donut(strat_summary_df: pd.DataFrame, title: str = "Pit Stop Strategy Distribution (Donut Chart)") -> go.Figure:
    """Donut chart illustrating percentage breakdown of 1-stop, 2-stop, and 3+ stop strategies."""
    if strat_summary_df.empty or 'StrategyType' not in strat_summary_df.columns:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Strategy Split Available"))
        return fig

    counts = strat_summary_df['StrategyType'].value_counts().reset_index()
    counts.columns = ['StrategyType', 'DriversCount']

    palette = ['#00b2fe', '#ffd600', '#e10600', '#9aa4b2', '#00d26a']

    fig = go.Figure(go.Pie(
        labels=counts['StrategyType'],
        values=counts['DriversCount'],
        hole=0.48,
        marker=dict(colors=palette, line=dict(color='#0a0d12', width=2)),
        textinfo='label+percent',
        textfont=dict(color='#ffffff', size=11),
        hovertemplate="<b>%{label}</b><br>Count: %{value} (%{percent})<extra></extra>"
    ))

    layout = get_plotly_f1_layout(title, height=360)
    layout['showlegend'] = True
    fig.update_layout(layout)
    return fig


def plot_pit_stops_vs_finish_scatter(strat_summary_df: pd.DataFrame, title: str = "Pit Stop Count vs Finishing Position (Sitograph / Correlation)") -> go.Figure:
    """Scatter plot (sitograph) correlating pit stop count to final finishing position with trendline."""
    if strat_summary_df.empty or not {'PitStopsCount', 'Position'}.issubset(strat_summary_df.columns):
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Pit Correlation Data Available"))
        return fig

    df = strat_summary_df.dropna(subset=['PitStopsCount', 'Position']).copy()
    df = df[(df['PitStopsCount'] >= 0) & (df['Position'] > 0)]
    if df.empty:
        return go.Figure()

    fig = go.Figure()

    # Jittered scatter markers so overlapping integer values are visible
    np.random.seed(42)
    jitter_x = df['PitStopsCount'] + np.random.uniform(-0.12, 0.12, size=len(df))
    jitter_y = df['Position'] + np.random.uniform(-0.12, 0.12, size=len(df))

    fig.add_trace(go.Scatter(
        x=jitter_x,
        y=jitter_y,
        mode='markers',
        name='Driver Finishes',
        marker=dict(size=9, color='#00b2fe', opacity=0.75, line=dict(width=1, color='#ffffff')),
        text=df.get('Driver', df.get('FullName', '')),
        hovertemplate="<b>%{text}</b><br>Pit Stops: %{customdata[0]}<br>Finishing Position: P%{customdata[1]}<extra></extra>",
        customdata=df[['PitStopsCount', 'Position']].values
    ))

    # Linear trendline if sufficient variation
    if df['PitStopsCount'].nunique() > 1 and len(df) >= 4:
        slope, intercept = np.polyfit(df['PitStopsCount'], df['Position'], 1)
        x_trend = np.linspace(df['PitStopsCount'].min(), df['PitStopsCount'].max(), 30)
        y_trend = slope * x_trend + intercept
        corr = df['PitStopsCount'].corr(df['Position'])
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=y_trend,
            mode='lines',
            name=f"Trendline (r = {corr:+.2f})",
            line=dict(color='#e10600', width=2.5, dash='dash')
        ))

    layout = get_plotly_f1_layout(title, height=390)
    layout['xaxis']['title'] = "Number of Pit Stops"
    layout['yaxis']['title'] = "Finishing Position (Lower is Better)"
    layout['yaxis']['autorange'] = 'reversed'
    fig.update_layout(layout)
    return fig


def plot_safety_car_causes_pie(sc_df: pd.DataFrame, title: str = "Safety Car Deployment Triggers (Pie Chart)") -> go.Figure:
    """Pie chart showing breakdown of Safety Car triggers (Accidents, Debris, Weather)."""
    if sc_df.empty or 'Cause' not in sc_df.columns:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Safety Car Data Available"))
        return fig

    counts = sc_df['Cause'].value_counts().head(8).reset_index()
    counts.columns = ['Cause', 'Deployments']

    palette = ['#e10600', '#00b2fe', '#ffd600', '#ff8000', '#00d26a', '#9aa4b2', '#cd7f32', '#c0c0c0']

    fig = go.Figure(go.Pie(
        labels=counts['Cause'],
        values=counts['Deployments'],
        hole=0.40,
        marker=dict(colors=palette, line=dict(color='#0a0d12', width=2)),
        textinfo='label+percent',
        textfont=dict(color='#ffffff', size=11),
        hovertemplate="<b>%{label}</b><br>Deployments: %{value} (%{percent})<extra></extra>"
    ))

    layout = get_plotly_f1_layout(title, height=360)
    layout['showlegend'] = True
    fig.update_layout(layout)
    return fig


def plot_compound_donut_chart(laps_df: pd.DataFrame, title: str = "Tyre Compound Usage Share (Donut Chart)") -> go.Figure:
    """Donut chart illustrating total laps completed per tyre compound."""
    if laps_df.empty or 'Compound' not in laps_df.columns:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Compound Data Available"))
        return fig

    comp_counts = laps_df['Compound'].value_counts().reset_index()
    comp_counts.columns = ['Compound', 'LapsCount']
    comp_counts = comp_counts[comp_counts['Compound'] != 'UNKNOWN']

    colors = [TYRE_COMPOUND_COLORS.get(c, '#6b7280') for c in comp_counts['Compound']]

    fig = go.Figure(go.Pie(
        labels=comp_counts['Compound'],
        values=comp_counts['LapsCount'],
        hole=0.48,
        marker=dict(colors=colors, line=dict(color='#0a0d12', width=2)),
        textinfo='label+percent',
        textfont=dict(color='#ffffff', size=11),
        hovertemplate="<b>%{label}</b><br>Laps: %{value:,} (%{percent})<extra></extra>"
    ))

    layout = get_plotly_f1_layout(title, height=370)
    layout['showlegend'] = True
    fig.update_layout(layout)
    return fig


def plot_stint_length_violin(laps_df: pd.DataFrame, title: str = "Tyre Stint Duration Density (Violin Plot)") -> go.Figure:
    """Violin plot showing both the probability density distribution and quartiles for stint lengths."""
    if laps_df.empty or not {'Stint', 'Compound', 'LapNumber'}.issubset(laps_df.columns):
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Stint Data Available"))
        return fig

    stints = (
        laps_df.dropna(subset=['Stint', 'Compound', 'LapNumber'])
        .groupby(['Driver', 'Stint', 'Compound'])['LapNumber'].count()
        .reset_index()
        .rename(columns={'LapNumber': 'StintLength'})
    )
    stints = stints[stints['Compound'] != 'UNKNOWN']
    if stints.empty:
        return go.Figure()

    fig = px.violin(
        stints,
        x='Compound',
        y='StintLength',
        color='Compound',
        color_discrete_map=TYRE_COMPOUND_COLORS,
        box=True,
        points='all',
        title=title
    )
    layout = get_plotly_f1_layout(title, height=380)
    layout['yaxis']['title'] = "Stint Length (Laps Completed)"
    layout['xaxis']['title'] = "Tyre Compound"
    fig.update_layout(layout)
    return fig


def plot_stint_compound_treemap(laps_df: pd.DataFrame, title: str = "Tyre Usage Hierarchy: Constructor ➔ Compound (Treemap)") -> go.Figure:
    """Treemap visualizing tyre compound usage proportion across teams."""
    team_col = 'TeamName' if 'TeamName' in laps_df.columns else ('Team' if 'Team' in laps_df.columns else None)
    if laps_df.empty or not team_col or 'Compound' not in laps_df.columns:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Treemap Data Available"))
        return fig

    df_clean = laps_df[(laps_df['Compound'] != 'UNKNOWN') & laps_df[team_col].notna()].copy()
    agg = df_clean.groupby([team_col, 'Compound'], as_index=False)['LapNumber'].count()
    agg.rename(columns={'LapNumber': 'LapsCount', team_col: 'Constructor'}, inplace=True)
    if agg.empty:
        return go.Figure()

    fig = px.treemap(
        agg,
        path=['Constructor', 'Compound'],
        values='LapsCount',
        color='Compound',
        color_discrete_map=TYRE_COMPOUND_COLORS,
        title=title
    )
    layout = get_plotly_f1_layout(title, height=410)
    fig.update_layout(layout)
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Laps: %{value:,}<extra></extra>")
    return fig


def plot_pitstop_by_team_violin(clean_ps: pd.DataFrame, title: str = "Pit Stop Duration Distribution by Constructor (Violin Plot)") -> go.Figure:
    """Violin plot illustrating pit crew consistency and time variance across constructors."""
    team_col = 'TeamName' if 'TeamName' in clean_ps.columns else ('constructorName' if 'constructorName' in clean_ps.columns else None)
    dur_col = 'DurationSec' if 'DurationSec' in clean_ps.columns else ('stop_duration_s' if 'stop_duration_s' in clean_ps.columns else None)

    if clean_ps.empty or not team_col or not dur_col:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Pit Crew Variance Data"))
        return fig

    # Handle both stationary pit stop times (1.5s - 15s) and pit lane transit times (15s - 45s)
    med_dur = clean_ps[dur_col].median()
    if med_dur > 15.0:
        df = clean_ps[(clean_ps[dur_col] >= 14.0) & (clean_ps[dur_col] <= 45.0)].copy()
    else:
        df = clean_ps[(clean_ps[dur_col] >= 1.5) & (clean_ps[dur_col] <= 15.0)].copy()

    if df.empty:
        df = clean_ps.dropna(subset=[team_col, dur_col]).copy()

    top_teams = df[team_col].value_counts().head(10).index.tolist()
    df = df[df[team_col].isin(top_teams)]
    if df.empty:
        return go.Figure()

    fig = px.violin(
        df,
        x=team_col,
        y=dur_col,
        color=team_col,
        color_discrete_map=TEAM_COLORS,
        box=True,
        points='outliers',
        title=title
    )
    layout = get_plotly_f1_layout(title, height=390)
    layout['yaxis']['title'] = "Duration (Seconds)"
    layout['xaxis']['tickangle'] = -25
    layout['xaxis']['title'] = ""
    fig.update_layout(layout)
    return fig


def plot_driver_lap_time_violin(laps_df: pd.DataFrame, drivers: list = None, title: str = "Driver Lap Pace Consistency (Violin Plot)") -> go.Figure:
    """Violin plot comparing pace density curves and medians across selected drivers."""
    if laps_df.empty or 'LapTimeSec' not in laps_df.columns:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Lap Timing Available"))
        return fig

    clean = laps_df[
        (~laps_df.get('IsOutlierLap', False)) &
        (laps_df['LapTimeSec'] > 50) &
        (laps_df['LapTimeSec'] < 135)
    ].copy()

    drv_col = 'Driver' if 'Driver' in clean.columns else 'FullName'
    if drivers:
        clean = clean[clean[drv_col].isin(drivers)]
    else:
        top_d = clean[drv_col].value_counts().head(6).index.tolist()
        clean = clean[clean[drv_col].isin(top_d)]

    if clean.empty:
        return go.Figure()

    fig = px.violin(
        clean,
        x=drv_col,
        y='LapTimeSec',
        color=drv_col,
        box=True,
        points=False,
        title=title
    )
    layout = get_plotly_f1_layout(title, height=390)
    layout['yaxis']['title'] = "Lap Time (Seconds)"
    layout['xaxis']['title'] = "Driver"
    fig.update_layout(layout)
    return fig


def plot_driver_performance_radar(results_df: pd.DataFrame, laps_df: pd.DataFrame, drivers: list = None, title: str = "Driver Multi-Attribute Radar / Spider Analysis") -> go.Figure:
    """
    Radar/Spider chart comparing drivers across 5 motorsport dimensions:
    - Scoring Rate (Points / Race)
    - Grid Delta (Positions Gained)
    - Pace Consistency (100 - CV%)
    - Win / Podium Rate (%)
    - Qualifying Index (Average Grid Position inverted)
    """
    if results_df.empty:
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Driver Comparison Data Available"))
        return fig

    # Determine top drivers to compare
    drv_col = 'FullName' if 'FullName' in results_df.columns else 'Driver'
    if drivers and len(drivers) > 0:
        target_drvs = drivers[:4]
    else:
        target_drvs = (
            results_df.groupby(drv_col)['Points'].sum()
            .sort_values(ascending=False).head(3).index.tolist()
            if 'Points' in results_df.columns
            else results_df[drv_col].dropna().unique().tolist()[:3]
        )

    categories = ['Scoring Power', 'Overtaking Delta', 'Pace Consistency', 'Podium Conversion', 'Qualifying Rank']
    palette = ['#e10600', '#00b2fe', '#ffd600', '#00d26a']

    fig = go.Figure()

    for idx, d in enumerate(target_drvs):
        d_res = results_df[results_df[drv_col] == d]
        if d_res.empty:
            continue

        races_count = max(1, len(d_res))
        tot_pts = d_res['Points'].sum() if 'Points' in d_res.columns else 0
        scoring_pwr = min(100, (tot_pts / (races_count * 25)) * 100)

        pos_gained = d_res['PositionsGained'].sum() if 'PositionsGained' in d_res.columns else 0
        overtake_score = min(100, max(10, 50 + pos_gained * 2))

        # Pace consistency from laps if present
        d_laps = laps_df[laps_df.get('Driver', '') == d] if not laps_df.empty else pd.DataFrame()
        if not d_laps.empty and 'LapTimeSec' in d_laps.columns and len(d_laps) > 10:
            clean_l = d_laps[(d_laps['LapTimeSec'] > 50) & (d_laps['LapTimeSec'] < 135)]
            cv = (clean_l['LapTimeSec'].std() / clean_l['LapTimeSec'].mean()) * 100 if len(clean_l) > 5 else 3.0
            consistency = max(20, min(100, 100 - cv * 12))
        else:
            consistency = 78.0

        podiums = (d_res['Position'] <= 3).sum() if 'Position' in d_res.columns else 0
        podium_rate = min(100, (podiums / races_count) * 100)

        avg_grid = d_res['GridPosition'].mean() if 'GridPosition' in d_res.columns else 10.0
        qual_rank = max(10, min(100, (21 - avg_grid) * 5))

        values = [scoring_pwr, overtake_score, consistency, podium_rate, qual_rank]
        # close the polygon loop
        values += [values[0]]
        cats = categories + [categories[0]]

        c = palette[idx % len(palette)]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=cats,
            fill='toself',
            name=str(d),
            line=dict(color=c, width=2),
            marker=dict(size=6, color=c)
        ))

    layout = get_plotly_f1_layout(title, height=430)
    layout['polar'] = dict(
        bgcolor="#131822",
        radialaxis=dict(visible=True, range=[0, 100], gridcolor="#283144", tickfont=dict(color="#9aa4b2", size=9)),
        angularaxis=dict(gridcolor="#283144", tickfont=dict(color="#ffffff", size=11, family="Titillium Web"))
    )
    fig.update_layout(layout)
    return fig


def plot_grid_to_finish_waterfall(results_df: pd.DataFrame, title: str = "Grid to Finish Delta (Diverging Waterfall)") -> go.Figure:
    """Diverging waterfall bar chart displaying position changes from starting grid to final finish."""
    if results_df.empty or not {'GridPosition', 'Position'}.issubset(results_df.columns):
        fig = go.Figure()
        fig.update_layout(get_plotly_f1_layout("No Grid Delta Data Available"))
        return fig

    df = results_df.dropna(subset=['GridPosition', 'Position']).copy()
    df = df[(df['GridPosition'] > 0) & (df['Position'] > 0)].head(18)
    if df.empty:
        return go.Figure()

    df['Delta'] = df['GridPosition'] - df['Position']
    df = df.sort_values('Delta', ascending=True)

    colors = ['#00d26a' if d > 0 else ('#e10600' if d < 0 else '#9aa4b2') for d in df['Delta']]
    drv_col = 'FullName' if 'FullName' in df.columns else 'Driver'

    fig = go.Figure(go.Bar(
        x=df['Delta'],
        y=df[drv_col],
        orientation='h',
        marker=dict(color=colors, line=dict(color='#0a0d12', width=1)),
        text=[f"{'+' if d > 0 else ''}{int(d)}" for d in df['Delta']],
        textposition='outside',
        textfont=dict(color='#ffffff', size=11, family="JetBrains Mono"),
        hovertemplate="<b>%{y}</b><br>Delta: %{x:+d} positions<extra></extra>"
    ))

    layout = get_plotly_f1_layout(title, height=max(360, len(df) * 24))
    layout['xaxis']['title'] = "Positions Gained (+) / Lost (-)"
    layout['yaxis']['title'] = ""
    fig.update_layout(layout)
    return fig

