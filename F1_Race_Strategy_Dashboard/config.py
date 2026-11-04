import os
from pathlib import Path

# Base Paths
PROJECT_DIR = Path(__file__).resolve().parent
DAV_DATA_DIR = Path(r"G:\DAV")
CACHE_DIR = PROJECT_DIR / "cache"
TELEMETRY_CACHE_DIR = CACHE_DIR / "telemetry"

# Dataset Paths in G:\DAV
F1_ZIP = DAV_DATA_DIR / "F1.zip"
F1_2_ZIP = DAV_DATA_DIR / "F1 2.zip"
F1_3_ZIP = DAV_DATA_DIR / "F1 3.zip"
ARCHIVE_ZIP = DAV_DATA_DIR / "archive.zip"
ARCHIVE_DIR = DAV_DATA_DIR / "archive"

STRATEGY_DATASET_CSV = (
    DAV_DATA_DIR / "f1-project" / "notebooks" / "data" / "raw" / "strategy" / "f1_strategy_final_dataset.csv"
)
FORMULA1_DIR = DAV_DATA_DIR / "f1-project" / "notebooks" / "data" / "raw" / "formula1"
PODIUMS_CSV = DAV_DATA_DIR / "f1-project" / "notebooks" / "data" / "raw" / "podiums" / "f1_podiums_1950_2026.csv"
COMBINED_DRIVER_RACE_CSV = (
    DAV_DATA_DIR / "f1-project" / "notebooks" / "data" / "processed" / "f1_driver_race_combined.csv"
)

# Color Scheme (Premium F1 Pit-Wall Dark Theme)
THEME_COLORS = {
    "bg_dark": "#0a0d12",
    "bg_card": "#131822",
    "bg_card_secondary": "#1c2230",
    "border": "#283144",
    "accent_red": "#e10600",
    "accent_red_glow": "rgba(225, 6, 0, 0.4)",
    "text_primary": "#ffffff",
    "text_secondary": "#9aa4b2",
    "text_muted": "#626d7f",
    "gold": "#ffb800",
    "silver": "#c0c0c0",
    "bronze": "#cd7f32",
    "success": "#00d26a",
    "warning": "#f5a623",
    "danger": "#e10600",
    "info": "#00b2fe",
}

# Formula 1 Tyre Compound Colors
TYRE_COMPOUND_COLORS = {
    "SOFT": "#e10600",
    "MEDIUM": "#ffd600",
    "HARD": "#f0f2f5",
    "INTERMEDIATE": "#39b54a",
    "WET": "#00a0dd",
    "UNKNOWN": "#6b7280",
}

# Constructor / Team Colors (Official FIA / FastF1 Palette)
TEAM_COLORS = {
    "Red Bull Racing": "#3671C6",
    "Ferrari": "#F80000",
    "Mercedes": "#6CD3BF",
    "McLaren": "#FF8000",
    "Aston Martin": "#229971",
    "Alpine": "#0093CC",
    "Williams": "#64C4FF",
    "AlphaTauri": "#5E8FAA",
    "RB": "#6692FF",
    "Alfa Romeo": "#C92D4B",
    "Kick Sauber": "#52E252",
    "Haas F1 Team": "#B6BABD",
    "Haas": "#B6BABD",
}

# Driver Numbers to Codes / Full Names
DRIVER_MAP = {
    1: {"code": "VER", "name": "Max Verstappen", "team": "Red Bull Racing"},
    11: {"code": "PER", "name": "Sergio Perez", "team": "Red Bull Racing"},
    14: {"code": "ALO", "name": "Fernando Alonso", "team": "Aston Martin"},
    18: {"code": "STR", "name": "Lance Stroll", "team": "Aston Martin"},
    16: {"code": "LEC", "name": "Charles Leclerc", "team": "Ferrari"},
    55: {"code": "SAI", "name": "Carlos Sainz", "team": "Ferrari"},
    44: {"code": "HAM", "name": "Lewis Hamilton", "team": "Mercedes"},
    63: {"code": "RUS", "name": "George Russell", "team": "Mercedes"},
    4: {"code": "NOR", "name": "Lando Norris", "team": "McLaren"},
    81: {"code": "PIA", "name": "Oscar Piastri", "team": "McLaren"},
    10: {"code": "GAS", "name": "Pierre Gasly", "team": "Alpine"},
    31: {"code": "OCO", "name": "Esteban Ocon", "team": "Alpine"},
    23: {"code": "ALB", "name": "Alexander Albon", "team": "Williams"},
    2: {"code": "SAR", "name": "Logan Sargeant", "team": "Williams"},
    77: {"code": "BOT", "name": "Valtteri Bottas", "team": "Alfa Romeo"},
    24: {"code": "ZHO", "name": "Guanyu Zhou", "team": "Alfa Romeo"},
    20: {"code": "MAG", "name": "Kevin Magnussen", "team": "Haas F1 Team"},
    27: {"code": "HUL", "name": "Nico Hulkenberg", "team": "Haas F1 Team"},
    22: {"code": "TSU", "name": "Yuki Tsunoda", "team": "AlphaTauri"},
    21: {"code": "DEV", "name": "Nyck de Vries", "team": "AlphaTauri"},
    3: {"code": "RIC", "name": "Daniel Ricciardo", "team": "AlphaTauri"},
    40: {"code": "LAW", "name": "Liam Lawson", "team": "AlphaTauri"},
}

# Status mapping for DNFs
DNF_STATUSES = [
    "Retired", "Accident", "Collision", "Engine", "Gearbox", "Transmission",
    "Brakes", "Suspension", "Electrical", "Hydraulics", "Power Unit", "Disqualified"
]
