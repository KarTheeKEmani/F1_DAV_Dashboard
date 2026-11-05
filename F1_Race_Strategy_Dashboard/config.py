import os
from pathlib import Path

# Base Paths
PROJECT_DIR = Path(__file__).resolve().parent
DAV_DATA_DIR = Path(r"G:\DAV")
CACHE_DIR = PROJECT_DIR / "cache"
TELEMETRY_CACHE_DIR = CACHE_DIR / "telemetry"
RAW_KAGGLE_DIR = DAV_DATA_DIR / "f1-project" / "notebooks" / "data" / "raw"

# Dataset Paths in G:\DAV
F1_ZIP = DAV_DATA_DIR / "F1.zip"
F1_2_ZIP = DAV_DATA_DIR / "F1 2.zip"
F1_3_ZIP = DAV_DATA_DIR / "F1 3.zip"
ARCHIVE_ZIP = DAV_DATA_DIR / "archive.zip"
ARCHIVE_DIR = DAV_DATA_DIR / "archive"

# 14 Integrated Kaggle Formula 1 Repositories
F1_WORLD_1950_2026_DIR = RAW_KAGGLE_DIR / "f1_world_1950_2026"
STRATEGY_DATASET_CSV = RAW_KAGGLE_DIR / "strategy" / "f1_strategy_final_dataset.csv"
STINT_AGGRESSION_CSV = RAW_KAGGLE_DIR / "stint_aggression" / "f1_pitstops_2018_2024.csv"
PIT_STOP_ANALYTICS_DIR = RAW_KAGGLE_DIR / "pit_stop_analytics"
PIT_STOP_PREDICTION_CSV = RAW_KAGGLE_DIR / "pit_stop_prediction" / "f1_strategy_dataset_v4.csv"
RACE_INTELLIGENCE_DIR = RAW_KAGGLE_DIR / "race_intelligence"
LIVE_TRACKER_DIR = RAW_KAGGLE_DIR / "live_tracker_2024_2026"
GP_WINNERS_CSV = RAW_KAGGLE_DIR / "gp_winners_1950_2025" / "winners_f1_1950_2025_v2.csv"
WEATHER_2018_2023_CSV = RAW_KAGGLE_DIR / "weather_2018_2023" / "F1 Weather(2023-2018).csv"
ROHANRAO_F1_DIR = RAW_KAGGLE_DIR / "rohanrao_f1"
FORMULA1_DIR = RAW_KAGGLE_DIR / "formula1"
PODIUMS_CSV = RAW_KAGGLE_DIR / "podiums" / "f1_podiums_1950_2026.csv"
RACE_EVENTS_DIR = RAW_KAGGLE_DIR / "race_events"
SAFETY_CARS_CSV = RACE_EVENTS_DIR / "safety_cars.csv"
RED_FLAGS_CSV = RACE_EVENTS_DIR / "red_flags.csv"
DRIVERS_CAREER_CSV = RAW_KAGGLE_DIR / "drivers_career" / "F1Drivers_Dataset.csv"

COMBINED_DRIVER_RACE_CSV = (
    DAV_DATA_DIR / "f1-project" / "notebooks" / "data" / "processed" / "f1_driver_race_combined.csv"
)
ARCHIVE_LAPDATA_DIR = ARCHIVE_DIR / "Directories" / "LapData"
ARCHIVE_CALCVARS_DIR = ARCHIVE_DIR / "Directories" / "calculated_variables"

# Color Scheme (Clean Motorsport Pit-Wall Dark Theme)
THEME_COLORS = {
    "bg_dark": "#0a0d12",
    "bg_card": "#131822",
    "bg_card_secondary": "#1c2230",
    "border": "#283144",
    "accent_red": "#e10600",
    "accent_red_glow": "rgba(225, 6, 0, 0.35)",
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
    "Red Bull": "#3671C6",
    "Ferrari": "#F80000",
    "Mercedes": "#6CD3BF",
    "McLaren": "#FF8000",
    "Aston Martin": "#229971",
    "Alpine": "#0093CC",
    "Alpine F1 Team": "#0093CC",
    "Williams": "#64C4FF",
    "AlphaTauri": "#5E8FAA",
    "RB": "#6692FF",
    "RB F1 Team": "#6692FF",
    "Alfa Romeo": "#C92D4B",
    "Kick Sauber": "#52E252",
    "Sauber": "#52E252",
    "Haas F1 Team": "#B6BABD",
    "Haas": "#B6BABD",
    "Renault": "#FFF500",
    "Racing Point": "#F596C8",
    "Force India": "#F596C8",
    "Toro Rosso": "#469BFF",
    "Lotus F1": "#FFB800",
}

# Team Name Normalizer across Kaggle datasets
TEAM_NAME_MAP = {
    "Red Bull": "Red Bull Racing",
    "Red Bull Racing Honda RBPT": "Red Bull Racing",
    "Oracle Red Bull Racing": "Red Bull Racing",
    "Alpine F1 Team": "Alpine",
    "Haas": "Haas F1 Team",
    "MoneyGram Haas F1 Team": "Haas F1 Team",
    "Alfa Romeo Racing": "Alfa Romeo",
    "RB F1 Team": "RB",
    "RB (AlphaTauri)": "RB",
    "Scuderia Ferrari": "Ferrari",
    "Mercedes-AMG Petronas": "Mercedes",
    "McLaren F1 Team": "McLaren",
    "Aston Martin Aramco": "Aston Martin",
    "Williams Racing": "Williams",
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

DRIVER_CODE_TO_FULLNAME = {
    "VER": "Max Verstappen",
    "PER": "Sergio Perez",
    "ALO": "Fernando Alonso",
    "STR": "Lance Stroll",
    "LEC": "Charles Leclerc",
    "SAI": "Carlos Sainz",
    "HAM": "Lewis Hamilton",
    "RUS": "George Russell",
    "NOR": "Lando Norris",
    "PIA": "Oscar Piastri",
    "GAS": "Pierre Gasly",
    "OCO": "Esteban Ocon",
    "ALB": "Alexander Albon",
    "SAR": "Logan Sargeant",
    "BOT": "Valtteri Bottas",
    "ZHO": "Guanyu Zhou",
    "MAG": "Kevin Magnussen",
    "HUL": "Nico Hulkenberg",
    "TSU": "Yuki Tsunoda",
    "DEV": "Nyck de Vries",
    "RIC": "Daniel Ricciardo",
    "LAW": "Liam Lawson",
    "VET": "Sebastian Vettel",
    "RAI": "Kimi Raikkonen",
    "MSC": "Mick Schumacher",
    "LAT": "Nicholas Latifi",
    "GIO": "Antonio Giovinazzi",
    "KUB": "Robert Kubica",
    "MAZ": "Nikita Mazepin",
    "COL": "Franco Colapinto",
    "BEA": "Oliver Bearman",
    "DOO": "Jack Doohan",
    "ANT": "Andrea Kimi Antonelli",
    "BOR": "Gabriel Bortoleto",
    "HAD": "Isack Hadjar",
}

# Status mapping for DNFs
DNF_STATUSES = [
    "Retired", "Accident", "Collision", "Engine", "Gearbox", "Transmission",
    "Brakes", "Suspension", "Electrical", "Hydraulics", "Power Unit", "Disqualified"
]
