# 🏎️ Formula 1 Race Telemetry & Strategy Analytics Platform

**Dashboard Name:** Race Strategy Dashboard  
**Research Question:** *How do race strategies influence Formula 1 performance?*  
**Academic Course:** Data Analytics and Visualization (DAV)

---

## 📌 Executive Summary

The **Formula 1 Race Telemetry & Strategy Analytics Platform** is a professional motorsport engineering analytics suite built to dissect the intricate factors determining Grand Prix outcomes.

By unifying official FIA FastF1 modern telemetry, the comprehensive multi-year Pirelli tyre stint dataset (2021–2024), and the historical Ergast relational database (10,945+ stationary pit stops), this platform models and visualizes:
1. **The Strategic Trade-Off:** Quantifying the pit-lane time penalty (~20–24 seconds) versus the fresh-rubber pace differential (+0.8s to +1.4s per lap).
2. **Tyre Degradation Curves:** Empirical linear regression slopes (seconds lost per lap of tyre age) across Soft, Medium, and Hard compounds.
3. **Pit Stop Optimization:** Evaluating stationary pit times (median 2.45s; sub-2.0s world records) and team pit crew consistency.
4. **Undercut & Overcut Mechanics:** Detecting and evaluating track-position swaps triggered by pit window timing.
5. **High-Frequency ECU Telemetry:** Synchronized traces of speed (km/h), throttle pedal position (%), braking hydraulic activation, sequential gear selection, and DRS deployment.

---

## 📁 Repository Structure

```text
G:\DAV\F1_Race_Strategy_Dashboard\
│
├── app.py                            # Main application entry point (Direct launch, NO login barrier)
├── config.py                         # Theme tokens, tyre colors, team palettes, and dataset paths
├── views.py                          # Page view orchestrator for all 8 analysis sections
├── extract_telemetry.py              # High-performance telemetry extraction and parquet converter
├── launch_dashboard.bat              # One-click Windows batch launcher
├── launch_dashboard.ps1              # One-click PowerShell launcher script
├── requirements.txt                  # Python dependencies
├── README.md                         # Documentation and launch instructions
│
├── cache\                            # High-speed query cache
│   └── telemetry\
│       ├── fastest_laps_telemetry.parquet  # Fastest laps telemetry across all 22 rounds
│       └── telemetry_round1.parquet        # Full-grid telemetry for Bahrain GP
│
├── data_processing\
│   ├── __init__.py
│   ├── data_loader.py                # Cached, robust data loader for all G:\DAV formats
│   ├── data_cleaning.py              # Timedelta parsers, compound normalizer, outlier lap filter
│   ├── data_integration.py           # Multi-dataset joins, stint aggregator, undercut detector
│   ├── schema_detection.py           # Automated schema discovery, null audits, key detection
│   └── analytics.py                  # Degradation regression, strategy impacts, consistency metrics
│
├── components\
│   ├── __init__.py
│   ├── styling.py                    # Motorsport pit-wall CSS, glowing KPI cards, badges, Plotly themes
│   ├── sidebar.py                    # Cascading filters (Season, Event, Driver, Team, Compound)
│   ├── kpi_cards.py                  # F1 KPI grid and delta cards
│   ├── charts.py                     # Plotly interactive charts (Pace, Degradation, Gantt, Telemetry)
│   └── tables.py                     # Searchable data tables with CSV download controls
│
├── pages\                            # Streamlit multipage view modules
│   ├── 1_Race_Overview.py
│   ├── 2_Race_Strategy.py
│   ├── 3_Tyre_Analysis.py
│   ├── 4_Pit_Stop_Analytics.py
│   ├── 5_Telemetry_Analysis.py
│   ├── 6_Driver_Team_Performance.py
│   ├── 7_Season_Race_Explorer.py
│   └── 8_Dataset_Explorer.py
│
└── tests\
    ├── test_data_cleaning.py         # Unit tests for time conversion and normalizers
    ├── test_data_loading.py          # Unit tests verifying real datasets in G:\DAV
    └── test_analytics.py             # Unit tests for degradation slopes and consistency CV
```

---

## 📊 Datasets Discovered & Integrated (`G:\DAV`)

The platform automatically discovers and ingests all relevant files in `G:\DAV`:

| Dataset Source | Files / Format | Records | Content & Role in Platform |
| :--- | :--- | :--- | :--- |
| **`F1.zip`** (Official FastF1) | `Events.csv`, `Results.csv`, `Laps.csv`, `Fastest_Laps.csv`, `Weather.csv`, `Telemetry.csv` | 24,400 laps<br>16.18M telemetry pts | Official 2023 FIA season: Lap-by-lap timing, sector splits, speed trap velocities, weather records, and car telemetry. |
| **Kaggle: `yajatpawar/formula-1-strategy-dataset`** | `f1_strategy_final_dataset.csv` | 80,767 laps | 2021–2024 multi-season tyre stint data with tyre age, compound codes, stint numbers, and SC/VSC status. |
| **Kaggle: `rohanrao/formula-1-world-championship-1950-2020` (v24: 1950–2024)** | 14 CSV tables (`pit_stops`, `qualifying`, `sprint_results`, `lap_times`, `circuits`, `results`, `races`, `drivers`, `constructors`...) | 11,371 pit stops<br>10,494 qualifying<br>589,081 lap times<br>26,759 results | Millisecond-accurate stationary pit stop durations, knockout qualifying splits, 360 Sprint results, and 77 GPS circuits. |
| **Kaggle: `melissamonfared/formula-1`** | 14 CSV relational tables | 680,000+ rows | Historical Formula 1 relational schema & cross-validation tables. |
| **Kaggle: `maulikgajera/formula-one-race-podiums-19502026`** | `f1_podiums_1950_2026.csv` | 1,158 Grands Prix | All-time Grand Prix podium trios (Winner, 2nd, 3rd) from 1950 to 2026. |
| **Kaggle: `jtrotman/formula-1-race-events`** | `safety_cars.csv`, `red_flags.csv` | 380 Safety Cars<br>103 Red Flags | Historical Safety Car deployments (causes, laps deployed/retreated) and Red Flag stoppages. |
| **Kaggle: `petalme/f1-drivers-dataset`** | `F1Drivers_Dataset.csv` | 868 All-Time Drivers | Career Championships, Entries, Starts, Poles, Wins, Podiums, Win Rate %, Pole Rate %, and Points/Entry. |
| **Processed Warehouse & 2024 Archive** | `f1_driver_race_combined.csv` & `G:\DAV\archive` | 26,499 combined starts<br>20 GP 2024 summaries | Multi-dataset warehouse combining historical results + strategy + podiums, plus 2024 season sector/pace data. |
| **`F1 2.zip`** | `weather.csv`, `weather.json` | 733 MB packets | F1 gaming/simulation telemetry with dynamic track temperature and pit stop window forecasts. |
| **`F1 3.zip`** | `F1_tweets.csv` | 239 MB | Grand Prix fan engagement, social reaction, and sentiment during race events. |
| **`Excluded Lab File`** | `DAV_Lab_02_Raw_Customer_Data.xlsx` | 100 rows | **Excluded:** Non-motorsport customer sales practice lab file, documented in audit log. |

---

## 🖥️ Key Dashboard Sections

### 1. 🏁 Race Overview — Main Dashboard
- High-impact F1 KPI Cards: Seasons analyzed, Grands Prix count, recorded laps, total pit stops, fastest lap time.
- Driver Championship standings colored by official constructor liveries.
- Grid position versus finishing position scatter parity plot (Positions gained/lost).
- Ambient air versus track surface temperature trends.

### 2. ⏱️ Race Strategy Analysis (Central Research Question)
- **Research Finding:** Correlation analysis between pit stop count and finishing position.
- Finishing position distribution across 1-Stop, 2-Stop, and Multi-Stop strategies.
- Interactive **Grand Prix Stint Timeline (Gantt Chart)** tracking every driver's tyre compound choice across laps.
- **Undercut & Overcut Detector:** Identifies position swaps between cars pitting within 1–3 laps of each other.
- Starting tyre compound advantage and podium conversion rates.

### 3. 🛞 Tyre & Stint Analysis
- Empirical tyre degradation curves ($s/\text{lap}$ wear rate) derived via linear regression on green-flag laps.
- Stint duration box plots comparing longevity across Soft, Medium, and Hard compounds.
- Constructor tyre compound allocation and stint strategies.

### 4. 🛑 Pit Stop Analytics
- Stationary duration distribution (median 2.45s) and sub-2.5s elite pit stop proportion.
- Top 10 fastest pit stops Hall of Fame (showcasing sub-2.0s benchmarks).
- Constructor pit crew reliability and consistency rankings.

### 5. ⚡ Lap-Time & Telemetry Analysis
- Real high-frequency ECU telemetry traces: Speed (km/h), Throttle (%), Brake (On/Off), and Gear (1–8) synchronized by track distance.
- Head-to-head driver comparisons (e.g. Verstappen vs Perez vs Alonso).
- Sector speed trap comparisons ($Speed_{I1}, Speed_{I2}, Speed_{FL}, Speed_{ST}$).
- Lap-by-lap pace evolution across selected drivers.

### 6. 🏆 Driver & Team Performance
- Teammate head-to-head battle matrix (qualifying wins, race finishes, points share).
- Driver pace consistency rankings based on Coefficient of Variation ($CV = \frac{\sigma}{\mu} \times 100\%$).
- Net positions gained from grid (Overtaking Index).

### 7. 🗺️ Season & Race Explorer
- Cascading dynamic selectors for Season, Grand Prix, Driver, and Team.
- Searchable and sortable official race classifications.
- Full lap-by-lap telemetry/timing table with **one-click CSV export**.

### 8. 🔍 Dataset Explorer & Data Quality Audit
- Complete transparent inventory of all discovered files in `G:\DAV`.
- Audit tables showing column schemas, inferred types, null counts, null percentages, and duplicate counts.
- Detected Entity-Relationship (ER) linkages connecting race results, pit stops, and telemetry.
- Direct CSV download for cleaned and aggregated datasets.

---

## 🚀 How to Launch Locally

### Quick Launch Command (Windows PowerShell / Command Prompt)

```powershell
cd /d G:\DAV\F1_Race_Strategy_Dashboard
& "G:\DAV\.venv\Scripts\streamlit.exe" run app.py
```

### Setup in a Fresh Virtual Environment

If creating a new virtual environment:

```powershell
cd /d G:\DAV\F1_Race_Strategy_Dashboard
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The application will immediately open in your browser at `http://localhost:8501` **without requiring any login or credentials**.

---

## 🧪 Validation & Automated Testing

Run the automated test suite with pytest:

```powershell
& "G:\DAV\.venv\Scripts\python.exe" -m pytest tests -v
```

Or run the full pipeline & chart integration test:

```powershell
& "G:\DAV\.venv\Scripts\python.exe" test_views_execution.py
```

Or sync/verify all 6 Kaggle datasets via `kagglehub`:

```powershell
& "G:\DAV\.venv\Scripts\python.exe" download_kaggle_datasets.py
```

**Results:**
- `tests/test_data_cleaning.py`: **PASSED** (Time conversions, compound normalizer, outlier lap filter)
- `tests/test_data_loading.py`: **PASSED** (Verified real data loading from `F1.zip`, `f1_strategy_final_dataset.csv`, `rohanrao_f1\`)
- `tests/test_analytics.py`: **PASSED** (Degradation slope estimation, pit strategy impact, consistency CV, race strategy simulation)
- `tests/test_kaggle_datasets.py`: **PASSED** (All 6 Kaggle repositories, 2024 archive, multi-year warehouse analytics, and FastAPI endpoints)
- **20 passed in 3.44s with 100% test success.**
