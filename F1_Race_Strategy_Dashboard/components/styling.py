import streamlit as st
import plotly.graph_objects as go
from config import THEME_COLORS, TYRE_COMPOUND_COLORS


def apply_custom_css():
    """Applies a clean, modern motorsport pit-wall dark theme CSS and hides Streamlit Deploy/Menu clutter."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:ital,wght@0,300;0,400;0,600;0,700;0,900;1,400&family=JetBrains+Mono:wght@400;600&display=swap');

    /* Global Root Variables */
    :root {{
        --bg-dark: {THEME_COLORS['bg_dark']};
        --bg-card: {THEME_COLORS['bg_card']};
        --bg-card-secondary: {THEME_COLORS['bg_card_secondary']};
        --border-color: {THEME_COLORS['border']};
        --accent-red: {THEME_COLORS['accent_red']};
        --accent-glow: {THEME_COLORS['accent_red_glow']};
        --text-primary: {THEME_COLORS['text_primary']};
        --text-secondary: {THEME_COLORS['text_secondary']};
        --text-muted: {THEME_COLORS['text_muted']};
        --f1-font: 'Titillium Web', -apple-system, BlinkMacSystemFont, sans-serif;
        --mono-font: 'JetBrains Mono', monospace;
    }}

    /* HIDE STREAMLIT DEPLOY BUTTON, MAIN MENU, FOOTER & DEFAULT SIDEBAR NAV */
    .stDeployButton,
    .stAppDeployButton,
    div[data-testid="stAppDeployButton"],
    div[data-testid="stToolbarActions"],
    div[data-testid="stStatusWidget"],
    #MainMenu,
    footer,
    div[data-testid="stSidebarNav"],
    section[data-testid="stSidebarNav"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* Main Container & Background */
    .stApp {{
        background-color: var(--bg-dark);
        color: var(--text-primary);
        font-family: var(--f1-font);
    }}

    .block-container {{
        padding-top: 1.8rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 97% !important;
    }}

    /* Top Header Bar */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 2.2rem !important;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--f1-font);
        font-weight: 700;
        letter-spacing: 0.4px;
        color: #ffffff !important;
    }}

    h2 {{
        border-left: 4px solid var(--accent-red);
        padding-left: 12px;
        margin-top: 0.2rem !important;
        margin-bottom: 0.8rem !important;
        font-size: 1.55rem !important;
    }}

    h3 {{
        font-size: 1.12rem !important;
        margin-top: 0.6rem !important;
        margin-bottom: 0.5rem !important;
        color: #f3f4f6 !important;
    }}

    /* Active Filter Status Bar */
    .f1-filter-banner {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        background: linear-gradient(90deg, rgba(19, 24, 34, 0.95) 0%, rgba(24, 31, 44, 0.95) 100%);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-red);
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 18px;
    }}

    .f1-filter-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.82rem;
        color: #e5e7eb;
    }}

    .f1-filter-pill b {{
        color: #ffffff;
        font-weight: 700;
    }}

    /* KPI Cards Container */
    .f1-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }}

    .f1-kpi-card {{
        background: linear-gradient(145deg, #121722 0%, #171e2c 100%);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 14px 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}

    .f1-kpi-card:hover {{
        border-color: var(--accent-red);
        transform: translateY(-2px);
    }}

    .f1-kpi-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: var(--accent-red);
    }}

    .f1-kpi-title {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-secondary);
        font-weight: 600;
        margin-bottom: 4px;
    }}

    .f1-kpi-value {{
        font-size: 1.55rem;
        font-weight: 900;
        color: #ffffff;
        font-family: var(--f1-font);
        line-height: 1.2;
    }}

    .f1-kpi-subtitle {{
        font-size: 0.74rem;
        color: var(--text-muted);
        margin-top: 4px;
    }}

    /* Tyre Compound Badges */
    .tyre-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        font-weight: 900;
        font-size: 0.7rem;
        margin: 0 3px;
        border: 2px solid;
    }}
    .tyre-badge-soft {{
        border-color: #e10600;
        color: #e10600;
        background: rgba(225, 6, 0, 0.15);
    }}
    .tyre-badge-medium {{
        border-color: #ffd600;
        color: #ffd600;
        background: rgba(255, 214, 0, 0.15);
    }}
    .tyre-badge-hard {{
        border-color: #f0f2f5;
        color: #f0f2f5;
        background: rgba(240, 242, 245, 0.15);
    }}
    .tyre-badge-intermediate {{
        border-color: #39b54a;
        color: #39b54a;
        background: rgba(57, 181, 74, 0.15);
    }}
    .tyre-badge-wet {{
        border-color: #00a0dd;
        color: #00a0dd;
        background: rgba(0, 160, 221, 0.15);
    }}

    /* Streamlit Tab Customization */
    div[data-testid="stTabs"] button {{
        font-family: var(--f1-font);
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.4px;
        color: var(--text-secondary);
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
        background: transparent;
        border: none;
        transition: all 0.15s ease;
    }}

    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: #ffffff !important;
        border-bottom: 3px solid var(--accent-red) !important;
        background: rgba(225, 6, 0, 0.08);
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: #0d1118;
        border-right: 1px solid var(--border-color);
    }}

    .f1-sidebar-brand {{
        text-align: left;
        padding: 8px 4px 14px 4px;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 14px;
    }}

    .f1-brand-title {{
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 900;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin: 0;
    }}

    .f1-brand-tagline {{
        color: var(--accent-red);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-top: 2px;
    }}

    /* Custom Callouts / Executive Insight Boxes */
    .f1-insight-box {{
        background: rgba(19, 24, 34, 0.85);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-red);
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0 16px 0;
        color: #d1d5db;
        font-size: 0.88rem;
        line-height: 1.45;
    }}

    .f1-insight-title {{
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 3px;
        font-size: 0.94rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_active_filter_banner(filters: dict):
    """Renders a sleek horizontal status strip displaying active Year, Team, Driver, and Sort Order."""
    yr = filters.get("selected_year", "All Years")
    team = filters.get("selected_team", "All Teams")
    drvs = filters.get("selected_drivers", ["All Drivers"])
    drv_str = ", ".join(drvs[:3]) + (f" (+{len(drvs)-3})" if len(drvs) > 3 else "") if isinstance(drvs, list) else str(drvs)
    ev = filters.get("selected_event", "All Events")
    sort_lbl = "Chronological (1950 -> 2026)" if filters.get("year_sort_ascending", False) else "Newest First (2026 -> 1950)"

    st.markdown(
        f"""
        <div class="f1-filter-banner">
            <span class="f1-filter-pill">📅 Year: <b>{yr}</b></span>
            <span class="f1-filter-pill">🏎️ Team: <b>{team}</b></span>
            <span class="f1-filter-pill">👤 Driver: <b>{drv_str}</b></span>
            <span class="f1-filter-pill">📍 Grand Prix: <b>{ev}</b></span>
            <span class="f1-filter-pill">🔃 Year Sort: <b>{sort_lbl}</b></span>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_plotly_f1_layout(title: str = "", height: int = 400) -> dict:
    """Returns Plotly layout dictionary styled with clean Formula 1 dark pit-wall aesthetics."""
    return dict(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Titillium Web, sans-serif", size=14, color="#ffffff"),
            x=0.01,
            y=0.97,
        ),
        paper_bgcolor=THEME_COLORS["bg_card"],
        plot_bgcolor=THEME_COLORS["bg_card"],
        height=height,
        margin=dict(l=42, r=24, t=48 if title else 22, b=40),
        font=dict(family="Titillium Web, sans-serif", color="#9aa4b2"),
        xaxis=dict(
            gridcolor="#1e2636",
            zerolinecolor="#283144",
            tickfont=dict(color="#9aa4b2", size=11),
            title_font=dict(color="#ffffff", size=12),
        ),
        yaxis=dict(
            gridcolor="#1e2636",
            zerolinecolor="#283144",
            tickfont=dict(color="#9aa4b2", size=11),
            title_font=dict(color="#ffffff", size=12),
        ),
        legend=dict(
            bgcolor="rgba(19, 24, 34, 0.85)",
            bordercolor=THEME_COLORS["border"],
            borderwidth=1,
            font=dict(color="#ffffff", size=11),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(
            bgcolor="#171e2c",
            font_size=12,
            font_family="JetBrains Mono, monospace",
            font_color="#ffffff",
            bordercolor=THEME_COLORS["accent_red"],
        ),
    )


def compound_badge_html(compound: str) -> str:
    """Returns an inline HTML badge for an F1 tyre compound."""
    c_upper = str(compound).upper()
    letter = c_upper[0] if c_upper and c_upper != "UNKNOWN" else "?"
    css_class = "tyre-badge-soft"
    if "MED" in c_upper:
        css_class = "tyre-badge-medium"
    elif "HARD" in c_upper:
        css_class = "tyre-badge-hard"
    elif "INTER" in c_upper:
        css_class = "tyre-badge-intermediate"
    elif "WET" in c_upper:
        css_class = "tyre-badge-wet"

    return f'<span class="tyre-badge {css_class}" title="{c_upper}">{letter}</span>'
