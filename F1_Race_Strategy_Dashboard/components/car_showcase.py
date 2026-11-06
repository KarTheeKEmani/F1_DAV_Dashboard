import streamlit as st
import pandas as pd
import numpy as np
import base64
from typing import Dict, Any, Optional

from config import TEAM_COLORS, DRIVER_MAP


def _clean_markup(raw: str) -> str:
    """Collapses multi-line HTML/SVG markup into a single continuous string to prevent Markdown pre/code block parsing."""
    lines = [line.strip() for line in raw.splitlines() if line.strip() and not line.strip().startswith("<!--")]
    return "".join(lines)


# Comprehensive Technical Specifications for Formula 1 Constructors
TEAM_METADATA = {
    "Red Bull Racing": {
        "chassis": "RB20 / RB19",
        "power_unit": "Honda RBPTH002 1.6L V6 Turbo Hybrid",
        "base": "Milton Keynes, United Kingdom",
        "principal": "Christian Horner",
        "primary_color": "#3671c6",
        "accent_color": "#f50537",
        "drivers": ["Max Verstappen (1)", "Sergio Perez (11)"],
        "world_titles": "6 Constructors (2010-2013, 2022-2023)",
    },
    "Ferrari": {
        "chassis": "SF-24 / SF-23",
        "power_unit": "Ferrari 066/12 1.6L V6 Turbo Hybrid",
        "base": "Maranello, Italy",
        "principal": "Frédéric Vasseur",
        "primary_color": "#e10600",
        "accent_color": "#ffffff",
        "drivers": ["Charles Leclerc (16)", "Carlos Sainz (55)"],
        "world_titles": "16 Constructors (Record Champion)",
    },
    "Mercedes": {
        "chassis": "W15 / W14 E Performance",
        "power_unit": "Mercedes-AMG F1 M15 1.6L V6 Turbo Hybrid",
        "base": "Brackley, United Kingdom",
        "principal": "Toto Wolff",
        "primary_color": "#00d2be",
        "accent_color": "#c0c0c0",
        "drivers": ["Lewis Hamilton (44)", "George Russell (63)"],
        "world_titles": "8 Consecutive Constructors (2014-2021)",
    },
    "McLaren": {
        "chassis": "MCL38 / MCL60",
        "power_unit": "Mercedes-AMG F1 M15 1.6L V6 Turbo Hybrid",
        "base": "Woking, United Kingdom",
        "principal": "Andrea Stella",
        "primary_color": "#ff8000",
        "accent_color": "#47c7fc",
        "drivers": ["Lando Norris (4)", "Oscar Piastri (81)"],
        "world_titles": "8 Constructors Championships",
    },
    "Aston Martin": {
        "chassis": "AMR24 / AMR23",
        "power_unit": "Mercedes-AMG F1 M15 1.6L V6 Turbo Hybrid",
        "base": "Silverstone, United Kingdom",
        "principal": "Mike Krack",
        "primary_color": "#006f62",
        "accent_color": "#cedc00",
        "drivers": ["Fernando Alonso (14)", "Lance Stroll (18)"],
        "world_titles": "British Racing Heritage & Tech Hub",
    },
    "Alpine": {
        "chassis": "A524 / A523",
        "power_unit": "Renault E-Tech RE24 1.6L V6 Turbo Hybrid",
        "base": "Enstone, United Kingdom / Viry, France",
        "principal": "Oliver Oakes",
        "primary_color": "#0090ff",
        "accent_color": "#ff87bc",
        "drivers": ["Pierre Gasly (10)", "Esteban Ocon (31)"],
        "world_titles": "2 Constructors (2005-2006 as Renault)",
    },
    "Williams": {
        "chassis": "FW46 / FW45",
        "power_unit": "Mercedes-AMG F1 M15 1.6L V6 Turbo Hybrid",
        "base": "Grove, Oxfordshire, United Kingdom",
        "principal": "James Vowles",
        "primary_color": "#005aff",
        "accent_color": "#00a0dd",
        "drivers": ["Alexander Albon (23)", "Carlos Sainz (2025+)"],
        "world_titles": "9 Constructors Championships",
    },
    "AlphaTauri": {
        "chassis": "VCARB 01 / AT04",
        "power_unit": "Honda RBPTH002 1.6L V6 Turbo Hybrid",
        "base": "Faenza, Italy",
        "principal": "Laurent Mekies",
        "primary_color": "#6692ff",
        "accent_color": "#ffffff",
        "drivers": ["Yuki Tsunoda (22)", "Daniel Ricciardo (3)"],
        "world_titles": "Red Bull Junior & Aerodynamic Proving Ground",
    },
    "RB": {
        "chassis": "VCARB 01 / AT04",
        "power_unit": "Honda RBPTH002 1.6L V6 Turbo Hybrid",
        "base": "Faenza, Italy",
        "principal": "Laurent Mekies",
        "primary_color": "#6692ff",
        "accent_color": "#ffffff",
        "drivers": ["Yuki Tsunoda (22)", "Liam Lawson (30)"],
        "world_titles": "Visa Cash App RB Formula One Team",
    },
    "Alfa Romeo": {
        "chassis": "C44 / C43",
        "power_unit": "Ferrari 066/12 1.6L V6 Turbo Hybrid",
        "base": "Hinwil, Switzerland",
        "principal": "Alessandro Alunni Bravi",
        "primary_color": "#52e252",
        "accent_color": "#000000",
        "drivers": ["Valtteri Bottas (77)", "Guanyu Zhou (24)"],
        "world_titles": "Historic Constructor & Audi 2026 Works Team",
    },
    "Kick Sauber": {
        "chassis": "C44 / C43",
        "power_unit": "Ferrari 066/12 1.6L V6 Turbo Hybrid",
        "base": "Hinwil, Switzerland",
        "principal": "Mattia Binotto",
        "primary_color": "#52e252",
        "accent_color": "#000000",
        "drivers": ["Nico Hulkenberg (27)", "Gabriel Bortoleto (2025+)"],
        "world_titles": "Future Audi F1 Factory Project",
    },
    "Haas F1 Team": {
        "chassis": "VF-24 / VF-23",
        "power_unit": "Ferrari 066/12 1.6L V6 Turbo Hybrid",
        "base": "Kannapolis, North Carolina, USA",
        "principal": "Ayao Komatsu",
        "primary_color": "#b6babd",
        "accent_color": "#e10600",
        "drivers": ["Kevin Magnussen (20)", "Nico Hulkenberg (27)"],
        "world_titles": "American F1 Team with Maranello Tech Alliance",
    },
}


def get_f1_car_svg(
    primary_color: str = "#e10600",
    accent_color: str = "#ffffff",
    driver_number: Optional[str] = None,
    width: int = 500,
    height: int = 135
) -> str:
    """Generates clean, single-line SVG string of a modern Ground-Effect Formula 1 Car."""
    num_badge = str(driver_number) if driver_number else ""
    raw = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 140" width="{width}" height="{height}" style="filter: drop-shadow(0px 8px 16px rgba(0, 0, 0, 0.6));">'
        f'<defs>'
        f'<linearGradient id="bodyGrad_{primary_color.replace("#", "")}" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{primary_color}" stop-opacity="0.95"/>'
        f'<stop offset="60%" stop-color="{primary_color}" stop-opacity="1.0"/>'
        f'<stop offset="100%" stop-color="{accent_color}" stop-opacity="0.85"/>'
        f'</linearGradient>'
        f'<linearGradient id="carbonGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#2a303c"/>'
        f'<stop offset="100%" stop-color="#12161f"/>'
        f'</linearGradient>'
        f'<linearGradient id="tyreGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#1f242e"/>'
        f'<stop offset="50%" stop-color="#0f1217"/>'
        f'<stop offset="100%" stop-color="#050608"/>'
        f'</linearGradient>'
        f'<linearGradient id="speedLines" x1="100%" y1="0%" x2="0%" y2="0%">'
        f'<stop offset="0%" stop-color="{primary_color}" stop-opacity="0.7"/>'
        f'<stop offset="100%" stop-color="{primary_color}" stop-opacity="0.0"/>'
        f'</linearGradient>'
        f'</defs>'
        f'<path d="M 20 50 Q 80 50 140 58" stroke="url(#speedLines)" stroke-width="2" fill="none" opacity="0.4"/>'
        f'<path d="M 10 75 Q 70 75 130 80" stroke="url(#speedLines)" stroke-width="3" fill="none" opacity="0.6"/>'
        f'<path d="M 30 100 Q 90 98 150 102" stroke="url(#speedLines)" stroke-width="1.5" fill="none" opacity="0.3"/>'
        f'<path d="M 70 108 L 470 108 L 485 95 L 495 106 L 65 106 Z" fill="url(#carbonGrad)" stroke="#1a202c" stroke-width="1"/>'
        f'<path d="M 45 104 L 75 104 L 75 108 L 45 108 Z" fill="#e10600" opacity="0.8"/>'
        f'<path d="M 45 42 L 85 45 L 82 85 L 58 98 Z" fill="url(#carbonGrad)"/>'
        f'<path d="M 38 40 L 98 40 L 92 48 L 42 48 Z" fill="{primary_color}"/>'
        f'<path d="M 40 32 L 95 32 L 90 38 L 42 38 Z" fill="url(#carbonGrad)" stroke="{accent_color}" stroke-width="1"/>'
        f'<path d="M 35 30 L 72 30 L 68 85 L 40 85 Z" fill="{primary_color}" opacity="0.85"/>'
        f'<path d="M 85 52 L 230 45 L 285 68 L 150 82 Z" fill="{primary_color}"/>'
        f'<path d="M 90 52 L 210 46 L 160 75 Z" fill="url(#carbonGrad)" opacity="0.5"/>'
        f'<path d="M 225 35 L 245 35 L 240 42 L 223 42 Z" fill="#000000"/>'
        f'<path d="M 215 42 Q 235 38 250 48 L 245 68 L 210 68 Z" fill="{accent_color}"/>'
        f'<ellipse cx="232" cy="50" rx="6" ry="7" fill="#0b0e14"/>'
        f'<path d="M 235 60 Q 280 58 315 70 L 255 72 Z" fill="#05070a"/>'
        f'<circle cx="260" cy="62" r="9" fill="{accent_color}"/>'
        f'<path d="M 260 59 L 268 62 L 263 66 Z" fill="#00d2be"/>'
        f'<path d="M 242 62 Q 275 50 305 68 Q 285 58 245 66 Z" fill="url(#carbonGrad)" stroke="{primary_color}" stroke-width="1.5"/>'
        f'<line x1="285" y1="58" x2="285" y2="70" stroke="#12161f" stroke-width="3"/>'
        f'<path d="M 195 72 Q 260 68 310 75 Q 365 82 380 95 L 170 98 Z" fill="url(#bodyGrad_{primary_color.replace("#", "")})"/>'
        f'<path d="M 290 73 Q 320 74 340 85 L 270 85 Z" fill="url(#carbonGrad)" opacity="0.6"/>'
        f'<path d="M 310 73 Q 380 75 460 92 Q 495 98 520 100 L 515 104 Q 460 102 380 96 Z" fill="url(#bodyGrad_{primary_color.replace("#", "")})"/>'
        f'<path d="M 455 98 L 530 101 L 532 105 L 450 103 Z" fill="url(#carbonGrad)"/>'
        f'<path d="M 470 96 L 535 99 L 533 103 L 468 100 Z" fill="{primary_color}"/>'
        f'<path d="M 505 92 L 535 94 L 530 108 L 500 106 Z" fill="{accent_color}"/>'
        f'<line x1="390" y1="84" x2="435" y2="98" stroke="#4a5568" stroke-width="2"/>'
        f'<line x1="395" y1="92" x2="435" y2="102" stroke="#2d3748" stroke-width="2"/>'
        f'<line x1="160" y1="78" x2="115" y2="96" stroke="#4a5568" stroke-width="2.5"/>'
        f'{"<text x=\"445\" y=\"90\" font-family=\"Titillium Web, sans-serif\" font-weight=\"900\" font-size=\"16\" fill=\"" + accent_color + "\" font-style=\"italic\">" + num_badge + "</text>" if num_badge else ""}'
        f'<g transform="translate(115, 96)">'
        f'<circle cx="0" cy="0" r="32" fill="url(#tyreGrad)" stroke="#111" stroke-width="1"/>'
        f'<circle cx="0" cy="0" r="27" fill="none" stroke="{primary_color}" stroke-width="2.5" opacity="0.9"/>'
        f'<circle cx="0" cy="0" r="19" fill="#12161f" stroke="#333" stroke-width="1"/>'
        f'<circle cx="0" cy="0" r="14" fill="url(#carbonGrad)"/>'
        f'<circle cx="0" cy="0" r="5" fill="#f50537"/>'
        f'<circle cx="0" cy="0" r="2" fill="#fff"/>'
        f'</g>'
        f'<g transform="translate(435, 98)">'
        f'<circle cx="0" cy="0" r="30" fill="url(#tyreGrad)" stroke="#111" stroke-width="1"/>'
        f'<circle cx="0" cy="0" r="25" fill="none" stroke="{primary_color}" stroke-width="2.5" opacity="0.9"/>'
        f'<circle cx="0" cy="0" r="18" fill="#12161f" stroke="#333" stroke-width="1"/>'
        f'<circle cx="0" cy="0" r="13" fill="url(#carbonGrad)"/>'
        f'<circle cx="0" cy="0" r="5" fill="#f50537"/>'
        f'<circle cx="0" cy="0" r="2" fill="#fff"/>'
        f'</g>'
        f'</svg>'
    )
    return raw


def get_f1_car_img_tag(
    primary_color: str = "#e10600",
    accent_color: str = "#ffffff",
    driver_number: Optional[str] = None,
    width: int = 460,
    height: int = 125,
) -> str:
    """
    Returns an HTML <img> tag with Base64 encoded SVG.
    This completely eliminates Markdown parsing bugs and prevents raw SVG <path> code from ever appearing on the frontend.
    """
    svg_str = get_f1_car_svg(primary_color, accent_color, driver_number, width, height)
    b64_str = base64.b64encode(svg_str.encode("utf-8")).decode("ascii")
    return (
        f'<img src="data:image/svg+xml;base64,{b64_str}" '
        f'alt="F1 Livery Car" width="{width}" height="{height}" '
        f'style="max-width: 100%; height: auto; display: block; margin: 0 auto; '
        f'filter: drop-shadow(0px 8px 16px rgba(0, 0, 0, 0.6));" />'
    )


def inject_f1_ambient_background(filters: Dict[str, Any]):
    """
    Injects high-grade Formula 1 circuit & carbon weave background styling with dynamic team ambient lighting.
    Completely eliminates plain blank backgrounds and integrates motorsport aesthetic.
    """
    sel_team = filters.get("selected_team", "All Teams")
    primary_color = "#e10600" # F1 default red
    accent_color = "#ffffff"

    if sel_team in TEAM_METADATA:
        primary_color = TEAM_METADATA[sel_team]["primary_color"]
        accent_color = TEAM_METADATA[sel_team]["accent_color"]
    elif sel_team in TEAM_COLORS:
        primary_color = TEAM_COLORS[sel_team]

    h = primary_color.lstrip('#')
    if len(h) == 6:
        r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    else:
        r, g, b = (225, 6, 0)

    # Clean single-line dynamic CSS for Streamlit background
    css_content = (
        f"<style>"
        f".stApp {{"
        f"  background-color: #0b0e14 !important;"
        f"  background-image: "
        f"    radial-gradient(circle at 90% 12%, rgba({r}, {g}, {b}, 0.16) 0%, transparent 48%), "
        f"    radial-gradient(circle at 8% 88%, rgba({r}, {g}, {b}, 0.10) 0%, transparent 45%), "
        f"    radial-gradient(ellipse at 50% 50%, rgba(13, 17, 24, 0.45) 0%, rgba(5, 7, 10, 0.96) 100%), "
        f"    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px), "
        f"    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px) !important;"
        f"  background-size: 100% 100%, 100% 100%, 100% 100%, 48px 48px, 48px 48px !important;"
        f"  background-attachment: fixed !important;"
        f"}}"
        f"</style>"
    )
    st.markdown(css_content, unsafe_allow_html=True)


def render_team_driver_showcase(filters: Dict[str, Any], data_bundle: Dict[str, Any]):
    """
    Renders an eye-catching, responsive Hero Paddock Banner showcasing the selected F1 Team / Driver.
    Emits single-line HTML to strictly prevent Markdown pre/code block parsing.
    """
    sel_team = filters.get("selected_team", "All Teams")
    sel_drivers = filters.get("selected_drivers", ["All Drivers"])
    sel_year = filters.get("selected_year", "All Years")

    primary_driver = None
    if sel_drivers and sel_drivers != ["All Drivers"] and len(sel_drivers) == 1:
        primary_driver = sel_drivers[0]

    driver_number = None
    if primary_driver:
        clean_name = primary_driver.split(" (")[0].strip()
        for num, info in DRIVER_MAP.items():
            if info["name"].lower() == clean_name.lower():
                driver_number = str(num)
                if sel_team == "All Teams":
                    sel_team = info["team"]
                break

    if sel_team in TEAM_METADATA:
        meta = TEAM_METADATA[sel_team]
        primary_color = meta["primary_color"]
        accent_color = meta["accent_color"]
        chassis_str = meta["chassis"]
        engine_str = meta["power_unit"]
        base_str = meta["base"]
    else:
        primary_color = TEAM_COLORS.get(sel_team, "#e10600")
        accent_color = "#ffffff"
        chassis_str = f"Formula 1 {sel_year} Prototype" if sel_year != "All Years" else "F1 Hybrid Era Ground-Effect"
        engine_str = "1.6L Turbocharged V6 Hybrid"
        base_str = "FIA Formula 1 World Championship Paddock"

    results_df = data_bundle.get("results", pd.DataFrame())
    win_count = 0
    podium_count = 0
    points_total = 0.0

    if results_df is not None and not results_df.empty:
        df_sub = results_df.copy()
        if sel_year != "All Years":
            df_sub = df_sub[df_sub["Year"] == int(sel_year)]
        if sel_team != "All Teams":
            df_sub = df_sub[df_sub["TeamName"] == sel_team]
        if primary_driver:
            c_name = primary_driver.split(" (")[0].strip()
            df_sub = df_sub[df_sub["FullName"].str.contains(c_name, case=False, na=False)]

        if not df_sub.empty:
            points_total = pd.to_numeric(df_sub["Points"], errors="coerce").fillna(0).sum()
            pos = pd.to_numeric(df_sub["Position"], errors="coerce")
            win_count = int((pos == 1).sum())
            podium_count = int((pos <= 3).sum())

    car_img = get_f1_car_img_tag(
        primary_color=primary_color,
        accent_color=accent_color,
        driver_number=driver_number,
        width=460,
        height=125
    )

    if sel_team != "All Teams" or primary_driver:
        driver_label = f"#{driver_number} {primary_driver}" if primary_driver else f"{sel_team} Team Profile"
        html = (
            f'<div style="background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(11, 14, 20, 0.95) 100%); '
            f'border: 1px solid rgba(255, 255, 255, 0.1); border-left: 5px solid {primary_color}; '
            f'border-radius: 12px; padding: 14px 20px; margin-bottom: 18px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5); '
            f'display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px;">'
            f'<div style="flex: 1 1 400px; min-width: 280px;">'
            f'<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">'
            f'<span style="background: {primary_color}; color: #ffffff; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.8px;">'
            f'{sel_team.upper()}'
            f'</span>'
            f'<span style="font-size: 0.78rem; color: #9aa4b2;">📍 {base_str}</span>'
            f'</div>'
            f'<div style="font-size: 1.4rem; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; margin-bottom: 2px;">'
            f'🏎️ {driver_label}'
            f'</div>'
            f'<div style="font-size: 0.8rem; color: #cfd6e0; line-height: 1.4;">'
            f'<b>Chassis:</b> <span style="color: {primary_color}; font-weight: 600;">{chassis_str}</span> &nbsp;|&nbsp; <b>Power Unit:</b> {engine_str}'
            f'</div>'
            f'<div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 8px;">'
            f'<span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; color: #fff;">'
            f'🏆 <b>{win_count}</b> Wins in Filter'
            f'</span>'
            f'<span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; color: #fff;">'
            f'🥇 <b>{podium_count}</b> Podiums'
            f'</span>'
            f'<span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; color: #00d26a;">'
            f'⚡ <b>{points_total:,.1f}</b> Championship Points'
            f'</span>'
            f'</div>'
            f'</div>'
            f'<div style="flex: 0 1 auto; display: flex; align-items: center; justify-content: center;">'
            f'{car_img}'
            f'</div>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
    else:
        html = (
            f'<div style="background: linear-gradient(135deg, rgba(19, 24, 34, 0.95) 0%, rgba(13, 16, 23, 0.95) 100%); '
            f'border: 1px solid rgba(255, 255, 255, 0.08); border-left: 5px solid #e10600; '
            f'border-radius: 12px; padding: 12px 18px; margin-bottom: 18px; '
            f'display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px;">'
            f'<div style="flex: 1 1 360px;">'
            f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">'
            f'<span style="background: #e10600; color: #fff; padding: 2px 7px; border-radius: 4px; font-size: 0.7rem; font-weight: 800;">'
            f'FIA FORMULA 1 WORLD CHAMPIONSHIP'
            f'</span>'
            f'<span style="font-size: 0.75rem; color: #9aa4b2;">1950 – 2026 ERA (77 SEASONS)</span>'
            f'</div>'
            f'<div style="font-size: 1.25rem; font-weight: 800; color: #ffffff;">'
            f'🏁 Paddock Strategy & Telemetry Command Center'
            f'</div>'
            f'<div style="font-size: 0.78rem; color: #9aa4b2; margin-top: 2px;">'
            f'Select any <b>Constructor</b> or <b>Driver</b> in the left sidebar to dynamically reskin the paddock with live liveries, technical chassis specs, and driver numbers.'
            f'</div>'
            f'</div>'
            f'<div style="flex: 0 1 auto; display: flex; align-items: center; justify-content: center;">'
            f'{car_img}'
            f'</div>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
