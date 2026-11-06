import os
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

SOURCE_PPTX = "C:/Users/karth/.gemini/antigravity/brain/9afef7b8-0ee9-42ed-9193-5daec5fcff53/.user_uploaded/media_1793960892107_3f5943f5.pptx"
ASSETS_DIR = "G:/DAV/F1_Race_Strategy_Dashboard/presentation_assets"
OUTPUT_PPTX = "G:/DAV/F1_Race_Strategy_Dashboard/F1_Data_Analytics_and_Visualization_Presentation.pptx"

def set_slide_header(slide, tag_text, title_text, slide_num):
    for sh in slide.shapes:
        if sh.has_text_frame:
            # Tag (red small header at top left)
            if 0.1 < sh.left.inches < 1.0 and 0.15 < sh.top.inches < 0.45:
                sh.text_frame.text = tag_text
                if sh.text_frame.paragraphs and sh.text_frame.paragraphs[0].runs:
                    sh.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xE1, 0x06, 0x00)
            # Title (large bold title)
            elif 0.1 < sh.left.inches < 1.0 and 0.45 <= sh.top.inches < 1.1:
                sh.text_frame.text = title_text
            # Slide number (bottom right)
            elif sh.left.inches > 11.5 and sh.top.inches > 6.8 and sh.width.inches < 1.0:
                sh.text_frame.text = f"{slide_num:02d}"

def populate_bullet_list(text_frame, items):
    text_frame.clear()
    for i, item in enumerate(items):
        p = text_frame.add_paragraph() if i > 0 else text_frame.paragraphs[0]
        p.space_after = Pt(8)
        p.line_spacing = 1.15
        
        if ":" in item:
            header, body = item.split(":", 1)
            r1 = p.add_run()
            r1.text = "• " + header.strip() + ": "
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            r1.font.size = Pt(11.5)
            
            r2 = p.add_run()
            r2.text = body.strip()
            r2.font.bold = False
            r2.font.color.rgb = RGBColor(0xCF, 0xD6, 0xE0)
            r2.font.size = Pt(11.5)
        else:
            r = p.add_run()
            r.text = "• " + item.strip()
            r.font.size = Pt(11.5)
            r.font.color.rgb = RGBColor(0xCF, 0xD6, 0xE0)

def main():
    prs = Presentation(SOURCE_PPTX)
    print(f"Loaded {len(prs.slides)} slides from template.")

    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------------------
    s1 = prs.slides[0]
    for sh in s1.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if "B.TECH" in txt:
                sh.text_frame.text = "B.TECH • COMPUTER SCIENCE & ENGINEERING (AI & ML)"
            elif "F1 DATA ANALYTICS" in txt:
                sh.text_frame.text = "F1 RACE STRATEGY\n& TELEMETRY PLATFORM"
            elif "interactive dashboard" in txt:
                sh.text_frame.text = "A Unified Multi-Dataset Architecture for High-Performance Race Intelligence & Visual Analytics (14 Kaggle Repositories, 1950–2026)"
            elif "PROJECT DOMAIN" in txt:
                sh.text_frame.text = "PROJECT DOMAIN"
            elif "Data Analytics and Visualization" in txt:
                sh.text_frame.text = "Data Analytics & Visualization | Python • Streamlit • Pandas • Plotly Express"
            elif "FROM RACE DATA" in txt:
                sh.text_frame.text = "FROM RAW TELEMETRY\nTO RACE STRATEGY"

    # -------------------------------------------------------------------------
    # SLIDE 2: Problem Statement
    # -------------------------------------------------------------------------
    s2 = prs.slides[1]
    set_slide_header(s2, "WHY THIS PLATFORM WAS ENGINEERED", "Problem Statement & Technical Challenges", 2)
    for sh in s2.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if "Formula 1 produces" in txt:
                sh.text_frame.text = "Formula 1 generates high-velocity data (100 Hz car telemetry, pit lane timing, tyre life) that remains siloed across isolated sources."
            elif "SCATTERED DATA" in txt:
                sh.text_frame.text = "14 HETEROGENEOUS REPOSITORIES"
            elif "Information is spread across" in txt:
                sh.text_frame.text = "Data is scattered across 14 independent Kaggle archives spanning 77 seasons (1950–2026) with conflicting schemas, identifiers, and granularities."
            elif "COMPLEX COMPARISONS" in txt:
                sh.text_frame.text = "TIMING & ENTITY DRIFT"
            elif "Comparing drivers, teams" in txt:
                sh.text_frame.text = "Non-standardized timedelta strings ('1:23.456', ISO, ms), 70 years of team rebrands, and inconsistent driver codes make joint analysis failure-prone."
            elif "LIMITED INSIGHT" in txt:
                sh.text_frame.text = "LATENT STRATEGY TRADE-OFFS"
            elif "Raw tables alone" in txt:
                sh.text_frame.text = "Tabular data hides critical trade-offs: tyre thermal degradation slopes, pit-lane transit vs stationary losses, and strategic undercut windows."
            elif "Project challenge" in txt:
                sh.text_frame.text = "Our Solution: Engineered an end-to-end data pipeline uniting 14 Kaggle repositories into clean data lakes with real-time cascading filters and 20+ specialized charts."

    # -------------------------------------------------------------------------
    # SLIDE 3: Objectives of the Project
    # -------------------------------------------------------------------------
    s3 = prs.slides[2]
    set_slide_header(s3, "ARCHITECTURAL GOALS & ENGINEERING SCOPE", "Objectives of the Project", 3)
    for sh in s3.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if "Integrate multiple Formula 1" in txt:
                sh.text_frame.text = "Unify 14 Kaggle repositories (26k+ classifications, 107k+ laps, 12k+ pit stops) into relational in-memory lakes."
            elif "Study race results" in txt:
                sh.text_frame.text = "Support 77 historical seasons (1950–2026) with dual-direction year-wise sorting and cascading entity filters."
            elif "Compare pit-stop patterns" in txt:
                sh.text_frame.text = "Model pit stop strategies, tyre degradation slopes (y = mx + c), and undercut/overcut windows statistically."
            elif "Understand lap-time" in txt:
                sh.text_frame.text = "Process 100 Hz telemetry signals (Speed, Throttle, Brake, Gear) aligned with micro-distance track coordinates."
            elif "Filter by year" in txt:
                sh.text_frame.text = "Engineer global cascading filters syncing Year, Constructor, Driver, Grand Prix, and Tyre Compound across views."
            elif "Present useful comparisons" in txt:
                sh.text_frame.text = "Provide 20+ visual types (Sitographs, Violins, Sunbursts, Radar, Waterfalls) and a Left Dashboard Custom Graph Studio."

    # -------------------------------------------------------------------------
    # SLIDE 4: Data Cleaning & Normalization Pipeline
    # -------------------------------------------------------------------------
    s4 = prs.slides[3]
    set_slide_header(s4, "HOW WE CLEANED & NORMALIZED KAGGLE DATASETS", "Data Cleaning & Normalization Pipeline (data_cleaning.py)", 4)
    for sh in s4.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if "1. COLLECTION" in txt:
                sh.text_frame.text = "1. TIME & DURATION PARSING"
            elif "The project brings together 14" in txt:
                sh.text_frame.text = "Engineered parse_timedelta_to_seconds() regex engine resolving mixed formats ('1:23.456', ISO timedeltas, ms) into float seconds; nullifies '\\N' anomalies."
            elif "2. CLEANING" in txt:
                sh.text_frame.text = "2. CONSTRUCTOR & DRIVER MAPPING"
            elif "CSV data is loaded and prepared" in txt:
                sh.text_frame.text = "Implemented canonical mappings (TEAM_NAME_MAP, DRIVER_MAP) resolving 70 years of team rebrands (Racing Point -> Aston Martin) and unifying driver codes."
            elif "3. INTEGRATION" in txt:
                sh.text_frame.text = "3. TYRE TAXONOMY & PIT SEGREGATION"
            elif "Related race, driver, team" in txt:
                sh.text_frame.text = "Standardized historical tyres (clean_compound_name) into 5 classes with FIA hex colors; segregated stationary wheel-change time from pit-lane transit loss."
            elif "Historical race results and classifications" in txt:
                sh.text_frame.text = "• Outlier Lap Filtering: Excludes in/out laps and Safety Car periods (>125% race pace) via IsOutlierLap to avoid skewing tyre degradation slopes.\n• DNF & Classification Normalization: Harmonizes finishes, DNFs, DNS, DSQs, and laps down without dropping records."
            elif "Filter data using selected dashboard" in txt:
                sh.text_frame.text = "• Type Coercion Engine: Enforces strict numeric types across 38 tables with robust error fallbacks to guarantee calculation integrity.\n• Null Imputation: Imputes missing tyre life and stint numbers based on chronological lap index and pit event markers."

    # -------------------------------------------------------------------------
    # SLIDE 5: Technologies & System Architecture
    # -------------------------------------------------------------------------
    s5 = prs.slides[4]
    set_slide_header(s5, "SYSTEM ARCHITECTURE & ANALYTICS PIPELINE", "Technologies & Engineering Architecture", 5)
    for sh in s5.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if "Core programming language for data handling" in txt:
                sh.text_frame.text = "Python 3.13: Central computational backbone powering custom analytics algorithms and data pipelines."
            elif "Builds the interactive web dashboard" in txt:
                sh.text_frame.text = "Streamlit: Reactive web dashboard framework with zero-latency cascading state and custom dark pit-wall CSS."
            elif "Loads, cleans, filters and transforms" in txt:
                sh.text_frame.text = "Pandas & NumPy: High-speed vectorized data operations, grouping, pivots, and statistical transformations."
            elif "Stores and exchanges structured racing" in txt:
                sh.text_frame.text = "In-Memory Data Lakes: Cached parquet & arrow memory buffers via @st.cache_data eliminating disk I/O bottlenecks."
            elif "Charts and graphs communicate trends" in txt:
                sh.text_frame.text = "Plotly Express & Graph Objects: 20+ reactive motorsport visualizations with interactive tooltips and dark layout."
            elif "Version control and project source-code" in txt:
                sh.text_frame.text = "FastAPI & Uvicorn: Asynchronous REST backend API (/api/analytics, /api/health) powering multi-client data access."
            elif "Exact package versions should be" in txt:
                sh.text_frame.text = "Architecture: Raw Kaggle CSVs (14 Repos) -> data_cleaning.py -> In-Memory Unified Lakes -> apply_global_filters() -> Visual Views & Custom Graph Studio"

    # -------------------------------------------------------------------------
    # SLIDE 6: Race Overview
    # -------------------------------------------------------------------------
    s6 = prs.slides[5]
    set_slide_header(s6, "EXECUTIVE RACE INTELLIGENCE & REAL-TIME KPI CONTROL", "Race Overview — Unified Multi-Dataset Intelligence", 6)
    for sh in s6.shapes:
        if sh.has_text_frame and sh.left.inches > 8.0 and sh.width.inches > 2.0:
            populate_bullet_list(sh.text_frame, [
                "Unified 77-Season Data Lake: Merges Ergast, FastF1, and modern Kaggle archives to display live KPIs: 77 Seasons, 1,167 GPs, 821 Drivers, 205 Teams, 107,807 Laps.",
                "Single-Line HTML KPI Grid: Prevents markdown code-block parsing while delivering responsive metric cards with dynamic trend deltas.",
                "Constructor Points Donut: Visualizes team championship shares (hole=0.48) mapped to official constructor livery colors.",
                "Championship Sunburst: Hierarchical visualization (Constructor -> Driver -> Points) with interactive multi-layer zoom.",
                "Cumulative Points Area: Tracks multi-round championship momentum and lead shifts across the season.",
                "Driver Finish Heatmap: Categorical round-by-round matrix revealing driver consistency across Grand Prix circuits."
            ])

    # -------------------------------------------------------------------------
    # SLIDE 7: Left Dashboard Custom Graph Studio (Upgraded in place of duplicate slide)
    # -------------------------------------------------------------------------
    s7 = prs.slides[6]
    set_slide_header(s7, "ON-THE-FLY CUSTOM VISUALIZATION ENGINE", "Custom Graph Studio for Selected Data (Left Dashboard)", 7)
    
    # Replace picture on slide 7 with the custom graph screenshot
    custom_img_path = os.path.join(ASSETS_DIR, "custom_graph_screenshot.png")
    if os.path.exists(custom_img_path):
        for shape in list(s7.shapes):
            if shape.shape_type == 13: # Picture
                left, top, width, height = shape.left, shape.top, shape.width, shape.height
                sp = shape._element
                sp.getparent().remove(sp)
                s7.shapes.add_picture(custom_img_path, Inches(0.65), Inches(1.45), Inches(7.50), Inches(4.95))
                break

    # Clean up old small KPI shapes from duplicate slide 7 (keep slide number badge)
    shapes_to_remove = []
    for sh in s7.shapes:
        if sh.has_text_frame and sh.left.inches > 8.0 and not (sh.top.inches > 6.8 and sh.width.inches < 1.0):
            shapes_to_remove.append(sh)
    for sh in shapes_to_remove:
        sp = sh._element
        sp.getparent().remove(sp)

    # Add single clean text box for the Custom Graph Studio on right side
    tx_box = s7.shapes.add_textbox(Inches(8.55), Inches(1.55), Inches(4.25), Inches(5.20))
    populate_bullet_list(tx_box.text_frame, [
        "Embedded Sidebar Studio: Built directly into the Left Dashboard, enabling on-demand graph generation for any filtered slice.",
        "Real-Time Data Stream Selection: Dynamically queries Race Results, Lap Times & Pace, Pit Stops, Stints, or Career Standings.",
        "Live Filter-Coupled Row Counter: Instantly displays matching records (e.g. ⚡ 44 records in selection) as filters change.",
        "8 Specialized Visual Types: Bar Chart, Line Chart, Sitograph (OLS Trendline + Pearson r), Pie/Donut, Histogram, Box Plot, Violin, and Area Chart.",
        "Custom Aggregations: Dynamic mathematical reductions (Sum, Mean, Count, Max, Min, or Raw data).",
        "Dual Display Architecture: Renders compact interactive preview in the sidebar + full-width high-resolution modal on the main dashboard."
    ])

    # -------------------------------------------------------------------------
    # SLIDE 8: Race Strategy Analysis
    # -------------------------------------------------------------------------
    s8 = prs.slides[7]
    set_slide_header(s8, "STATISTICAL MODELING OF PIT DECIDERS & STINTS", "Race Strategy Analysis — Pit Strategies & Correlations", 8)
    for sh in s8.shapes:
        if sh.has_text_frame and sh.left.inches > 8.0 and sh.width.inches > 2.0:
            populate_bullet_list(sh.text_frame, [
                "Stint Classification Algorithm: Evaluates pit stop records to segment race executions into 0-stop, 1-stop, 2-stop, 3-stop, and multi-stop groups.",
                "Finish by Strategy Type: Compares average finishing ranks across strategy categories to identify the mathematically optimal tactic.",
                "Starting Tyre Advantage: Cross-tabulates starting tyre compounds against GP wins (e.g. Medium compound accounting for 58 wins).",
                "Strategy Mix Donut Chart: Displays the strategic pit stop split across the field (1-stop: 39.3%, 2-stop: 41%, 3-stop: 11.9%).",
                "Sitograph (Scatter + Trendline): Computes Pearson correlation (r = -0.05) between pit stop count and finishing position to evaluate tactical penalty.",
                "Grid-to-Finish Waterfall: Diverging bar chart showing position delta from starting grid to chequered flag."
            ])

    # -------------------------------------------------------------------------
    # SLIDE 9: Tyre and Stint Analysis
    # -------------------------------------------------------------------------
    s9 = prs.slides[8]
    set_slide_header(s9, "MATHEMATICAL MODELING OF TYRE WEAR & DEGRADATION", "Tyre and Stint Analysis — Thermal Wear & Stints", 9)
    for sh in s9.shapes:
        if sh.has_text_frame and sh.left.inches > 8.0 and sh.width.inches > 2.0:
            populate_bullet_list(sh.text_frame, [
                "Linear Regression Degradation Slopes (y = mx + c): Computes thermal wear per lap (s/lap) after filtering outlier and caution laps:\n  - Hard: +0.124 s/lap (37,081 laps | Max: 44L)\n  - Intermediate: +0.188 s/lap (4,635 laps | Max: 44L)\n  - Medium: +0.194 s/lap (30,652 laps | Max: 44L)\n  - Soft: +0.297 s/lap (11,264 laps | Max: 44L)\n  - Wet: +0.862 s/lap (103 laps | Max: 20L)",
                "Stint Length Violin Density: Plots kernel density estimates (KDE) and quartile spreads showing compound durability cliffs.",
                "Tyre Allocation Treemap: Hierarchical constructor tyre allocation mapping compound shares across teams.",
                "Driver Aggression Integration: Merges 7,374 Kaggle stint aggression records to model driver pace multipliers."
            ])

    # -------------------------------------------------------------------------
    # SLIDE 10: Pit Stop Analytics
    # -------------------------------------------------------------------------
    s10 = prs.slides[9]
    set_slide_header(s10, "STATIONARY CREW PERFORMANCE VS PIT-LANE LOSS", "Pit Stop Analytics — Stationary vs Transit Duration", 10)
    for sh in s10.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if "STRATEGY DISTRIBUTION" in txt:
                sh.text_frame.text = "DUAL-DURATION SEGREGATION"
            elif "The dashboard visualizes the share" in txt:
                sh.text_frame.text = "Segregates stationary wheel-change duration (Median ~14.13s Ergast / ~2.3s Kaggle events) from total pit-lane transit loss (~23.32s)."
            elif "STOP COUNT VS RESULT" in txt:
                sh.text_frame.text = "CREW VARIANCE & VIOLIN DENSITY"
            elif "A scatter plot compares the number" in txt:
                sh.text_frame.text = "Violin plots evaluate pit crew standard deviation and IQR variance by constructor, identifying operational mistakes."
            elif "RACE DECISIONS" in txt:
                sh.text_frame.text = "REAL-TIME LEADERBOARD & SITOGRAPH"
            elif "These views help discuss how pit" in txt:
                sh.text_frame.text = "Ranked leaderboards highlight sub-13s pit stops, while stationary vs transit sitographs analyze pit-lane entry/exit delta."

    # -------------------------------------------------------------------------
    # SLIDE 11: Lap-Time and Telemetry Analysis
    # -------------------------------------------------------------------------
    s11 = prs.slides[10]
    set_slide_header(s11, "100 Hz SIGNAL PROCESSING & TRACE VISUALIZATION", "Lap-Time & Telemetry Analysis — Signal Decomposition", 11)
    for sh in s11.shapes:
        if sh.has_text_frame and sh.left.inches > 8.0 and sh.width.inches > 2.0:
            populate_bullet_list(sh.text_frame, [
                "Multi-Channel Telemetry Alignment: Synchronizes 100 Hz signals (Speed, Throttle %, Brake, Gear) along track distance (meters).",
                "Braking & Apex Detection: Telemetry troughs isolate exact threshold braking points, minimum corner apex speeds, and throttle pick-up points.",
                "Step-Function Gear Traces: Tracks transmission shift patterns, downshift engine braking, and high-speed gear optimization.",
                "Driver Pace Consistency (CV %): Computes the Coefficient of Variation (CV = σ / μ) of lap times to measure driver pace reliability.",
                "5-Axis Driver Spider / Radar: Normalizes Scoring Power, Overtaking Delta, Consistency, Podium Conversion, and Qualifying Rank."
            ])

    # -------------------------------------------------------------------------
    # SLIDE 12: Driver and Team Performance
    # -------------------------------------------------------------------------
    s12 = prs.slides[11]
    set_slide_header(s12, "EVALUATING DRIVERS IN IDENTICAL MACHINERY", "Driver & Team Performance — Intra-Team Normalization", 12)
    for sh in s12.shapes:
        if sh.has_text_frame and sh.left.inches > 8.0 and sh.width.inches > 2.0:
            populate_bullet_list(sh.text_frame, [
                "Intra-Team Performance Normalization: Isolates driver talent from car advantage by comparing teammate pairs driving identical cars.",
                "Head-to-Head Headcount & Points Share: Computes intra-team finishing records, qualifying battle records, and team points share.",
                "Pace Consistency Rankings: Ranks drivers across seasons using lap pace standard deviation (StdDevSec) and coefficient of variation.",
                "All-Time Historical Milestones: Joins Kaggle Drivers Career (868 drivers) and Podiums (1,158 records) to track lifetime win percentages.",
                "Grid-to-Finish Delta Waterfall: Quantifies race day overtaking conversion from Saturday qualifying positions."
            ])

    # -------------------------------------------------------------------------
    # SLIDE 13: Season and Race Explorer
    # -------------------------------------------------------------------------
    s13 = prs.slides[12]
    set_slide_header(s13, "YEAR-WISE QUERY ENGINE & ARCHIVE EXPLORATION", "Season and Race Explorer — 77 Years of Official Data", 13)
    for sh in s13.shapes:
        if sh.has_text_frame and sh.left.inches > 8.0 and sh.width.inches > 2.0:
            populate_bullet_list(sh.text_frame, [
                "77-Season Query Engine: Enables instant filtering across 26,268 historical race records spanning from 1950 to 2026.",
                "Dual Year-Wise Sort Direction: Supports reverse chronological sorting (2026 -> 1950) for modern analysis and chronological sorting for historical research.",
                "Automated Position Gain Metrics: Calculates positions gained/lost (GridPosition - PositionOrder) for every competitor per round.",
                "Relational Foreign Key Traversal: Seamlessly links classifications with circuit names, driver IDs, and constructor affiliations.",
                "One-Click CSV Export: Provides direct scientific CSV downloads of filtered tabular slices for secondary research modeling."
            ])

    # -------------------------------------------------------------------------
    # SLIDE 14: Dataset Explorer & Data Quality
    # -------------------------------------------------------------------------
    s14 = prs.slides[13]
    set_slide_header(s14, "MULTI-REPOSITORY METADATA & DATA HEALTH AUDITING", "Dataset Explorer & Data Quality Architecture", 14)
    for sh in s14.shapes:
        if sh.has_text_frame and sh.left.inches > 8.0 and sh.width.inches > 2.0:
            populate_bullet_list(sh.text_frame, [
                "14 Kaggle Repositories Hub: Full metadata registry documenting year coverage, repository slug, local folder, and primary tables.",
                "Relational Schema Detection (schema_detection.py): Automatically maps 38 datasets and discovers 7 primary-to-foreign key links.",
                "Automated Data Health Profiling: Computes column-level null percentages, type conformance, duplicate rows, and schema drift.",
                "Broad Temporal Coverage: Unifies 1950–2026 World Championship, 2010–2026 Race Intelligence, and 2024–2026 Live Trackers.",
                "Research Lineage & Integrity: Guarantees complete data lineage and traceability from raw Kaggle CSVs to visual dashboard components."
            ])

    # -------------------------------------------------------------------------
    # SLIDE 15: Conclusion & Technical Contributions
    # -------------------------------------------------------------------------
    s15 = prs.slides[14]
    set_slide_header(s15, "KEY TECHNICAL CONTRIBUTIONS & FUTURE SCOPE", "Conclusion & Engineering Impact", 15)
    for sh in s15.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if "The F1 Data Analytics and Visualization" in txt:
                sh.text_frame.text = "The Formula 1 Race Strategy & Telemetry Analytics Platform transforms 14 disparate Kaggle archives into a high-performance visual intelligence system."
            elif "INTEGRATED VIEW" in txt:
                sh.text_frame.text = "DATA ENGINEERING EXCELLENCE"
            elif "Combines multiple Formula 1 data" in txt:
                sh.text_frame.text = "Unified 14 Kaggle repositories (1950–2026) and 100 Hz telemetry through automated cleaning, entity mapping, and timedelta normalization."
            elif "INTERACTIVE ANALYSIS" in txt:
                sh.text_frame.text = "RIGOROUS STATISTICAL ANALYTICS"
            elif "Enables filtering and comparison across" in txt:
                sh.text_frame.text = "Engineered OLS tyre degradation slopes (s/lap), pit stop correlation (r), pace consistency (CV), and intra-team performance normalization."
            elif "VISUAL INSIGHTS" in txt:
                sh.text_frame.text = "INTERACTIVE VISUAL STUDIO"
            elif "Uses charts, tables and telemetry views" in txt:
                sh.text_frame.text = "Delivered 20+ specialized dark motorsport visualizations alongside an on-the-fly Custom Graph Studio integrated into the Left Dashboard."
            elif "Add further validation and automated" in txt:
                sh.text_frame.text = (
                    "• Real-Time Telemetry Streaming: Ingestion of live session telemetry via FastF1 WebSockets.\n"
                    "• Predictive Machine Learning: Random Forest / XGBoost models predicting optimal pit stop windows and tyre life cliffs.\n"
                    "• Monte Carlo Strategy Simulation: Probabilistic modeling of race outcomes under Safety Car interventions."
                )
            elif "THANK YOU!" in txt:
                sh.text_frame.text = "🏁 THANK YOU!\nQuestions & Technical Discussion"

    # Save
    prs.save(OUTPUT_PPTX)
    print(f"Successfully generated updated presentation: {OUTPUT_PPTX}")

if __name__ == "__main__":
    main()
