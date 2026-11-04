import streamlit as st
import plotly.graph_objects as go
from config import THEME_COLORS, TYRE_COMPOUND_COLORS


def apply_custom_css():
    """Applies a professional, motorsport pit-wall dark theme CSS across the entire app."""
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

    /* Main Container & Background */
    .stApp {{
        background-color: var(--bg-dark);
        color: var(--text-primary);
        font-family: var(--f1-font);
    }}

    /* Top Header Bar */
    header[data-testid="stHeader"] {{
        background: rgba(10, 13, 18, 0.85);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--border-color);
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--f1-font);
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #ffffff !important;
    }}

    h1 {{
        border-left: 5px solid var(--accent-red);
        padding-left: 14px;
        margin-top: 5px;
        margin-bottom: 15px;
        text-transform: uppercase;
        font-size: 2.1rem;
    }}

    /* KPI Cards Container */
    .f1-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }}

    .f1-kpi-card {{
        background: linear-gradient(145deg, #131822 0%, #171e2c 100%);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px 18px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
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
        width: 4px;
        height: 100%;
        background: var(--accent-red);
    }}

    .f1-kpi-title {{
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: var(--text-secondary);
        font-weight: 600;
        margin-bottom: 6px;
    }}

    .f1-kpi-value {{
        font-size: 1.85rem;
        font-weight: 900;
        color: #ffffff;
        font-family: var(--f1-font);
        line-height: 1.2;
    }}

    .f1-kpi-subtitle {{
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }}

    /* Content Cards */
    .f1-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }}

    .f1-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 12px;
        margin-bottom: 16px;
    }}

    .f1-card-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* Tyre Compound Badges */
    .tyre-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        font-weight: 900;
        font-size: 0.72rem;
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
        font-size: 0.95rem;
        letter-spacing: 0.5px;
        color: var(--text-secondary);
        padding: 10px 18px;
        border-radius: 4px 4px 0 0;
        background: transparent;
        border: none;
        transition: all 0.2s ease;
    }}

    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: #ffffff !important;
        border-bottom: 3px solid var(--accent-red) !important;
        background: rgba(225, 6, 0, 0.08);
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: #0e121a;
        border-right: 1px solid var(--border-color);
    }}

    .f1-sidebar-brand {{
        text-align: center;
        padding: 16px 0 20px 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }}

    .f1-brand-title {{
        color: #ffffff;
        font-size: 1.35rem;
        font-weight: 900;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 0;
    }}

    .f1-brand-tagline {{
        color: var(--accent-red);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 3px;
    }}

    /* Data Table Styling */
    .dataframe {{
        background-color: var(--bg-card) !important;
        color: #ffffff !important;
        border: 1px solid var(--border-color) !important;
        font-family: var(--mono-font) !important;
        font-size: 0.85rem !important;
    }}

    /* Custom Callouts / Executive Insight Boxes */
    .f1-insight-box {{
        background: rgba(225, 6, 0, 0.06);
        border-left: 4px solid var(--accent-red);
        border-radius: 0 6px 6px 0;
        padding: 14px 18px;
        margin: 16px 0;
        color: #e5e7eb;
        font-size: 0.92rem;
        line-height: 1.5;
    }}

    .f1-insight-title {{
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_plotly_f1_layout(title: str = "", height: int = 420) -> dict:
    """Returns Plotly layout dictionary styled with Formula 1 dark pit-wall aesthetics."""
    return dict(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Titillium Web, sans-serif", size=15, color="#ffffff"),
            x=0.01,
            y=0.98,
        ),
        paper_bgcolor=THEME_COLORS["bg_card"],
        plot_bgcolor=THEME_COLORS["bg_card"],
        height=height,
        margin=dict(l=45, r=30, t=55 if title else 25, b=45),
        font=dict(family="Titillium Web, sans-serif", color=THEME_COLORS["text-secondary"] if "text-secondary" in THEME_COLORS else "#9aa4b2"),
        xaxis=dict(
            gridcolor="#222b3a",
            zerolinecolor="#283144",
            tickfont=dict(color="#9aa4b2", size=11),
            title_font=dict(color="#ffffff", size=12),
        ),
        yaxis=dict(
            gridcolor="#222b3a",
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
