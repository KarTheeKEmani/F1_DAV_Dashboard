import streamlit as st
from typing import Optional, List, Dict, Any


def render_kpi_card(title: str, value: str, subtitle: Optional[str] = None, delta_text: Optional[str] = None, delta_positive: Optional[bool] = None):
    """Generates HTML for a single high-impact F1 KPI card."""
    delta_html = ""
    if delta_text:
        color = "#00d26a" if delta_positive is True else ("#e10600" if delta_positive is False else "#9aa4b2")
        icon = "▲" if delta_positive is True else ("▼" if delta_positive is False else "•")
        delta_html = f'<span style="color: {color}; font-weight: 700; margin-left: 6px;">{icon} {delta_text}</span>'

    subtitle_content = f"{subtitle or ''} {delta_html}".strip()
    subtitle_div = f'<div class="f1-kpi-subtitle">{subtitle_content}</div>' if subtitle_content else ''

    return f"""
    <div class="f1-kpi-card">
        <div class="f1-kpi-title">{title}</div>
        <div class="f1-kpi-value">{value}</div>
        {subtitle_div}
    </div>
    """


def render_kpi_grid(kpis: List[Dict[str, Any]]):
    """Renders a responsive CSS grid of F1 KPI cards."""
    cards_html = "".join([
        render_kpi_card(
            title=item.get("title", ""),
            value=item.get("value", ""),
            subtitle=item.get("subtitle", None),
            delta_text=item.get("delta_text", None),
            delta_positive=item.get("delta_positive", None)
        )
        for item in kpis
    ])
    grid_html = f'<div class="f1-kpi-grid">{cards_html}</div>'
    st.markdown(grid_html, unsafe_allow_html=True)
