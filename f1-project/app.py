from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="F1 Strategy Dashboard", layout="wide")

@st.cache_data
def load_data():
    file = Path("data/processed/f1_driver_race_combined.csv")
    return pd.read_csv(file)

df = load_data()

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["position"] = pd.to_numeric(df["position"], errors="coerce")
df["grid"] = pd.to_numeric(df["grid"], errors="coerce")

st.title("Formula 1 Strategy Dashboard")
st.write("Explore race results, starting positions, and pit-stop strategy data.")

years = sorted(df["year"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Choose seasons",
    years,
    default=years[-5:]
)

filtered = df[df["year"].isin(selected_years)]

col1, col2, col3 = st.columns(3)
col1.metric("Driver-race records", f"{len(filtered):,}")
col2.metric("Races", filtered["raceId"].nunique())
col3.metric("Wins", int((filtered["position"] == 1).sum()))

st.subheader("Average finishing position by starting grid position")

grid_data = (
    filtered.dropna(subset=["grid", "position"])
    .groupby("grid", as_index=False)["position"]
    .mean()
    .sort_values("grid")
)

st.bar_chart(grid_data.set_index("grid"))

st.subheader("Average pit stops by season")

pit_data = (
    filtered.dropna(subset=["pit_stops"])
    .groupby("year", as_index=False)["pit_stops"]
    .mean()
    .sort_values("year")
)

st.line_chart(pit_data.set_index("year"))

st.subheader("Race data")
st.dataframe(
    filtered[
        ["year", "round", "name", "driver_code", "grid",
         "position", "points", "pit_stops", "avg_lap_time_sec"]
    ],
    use_container_width=True
)