from datetime import datetime
import streamlit as st
import altair as alt
import pandas as pd

# ---------------------------------
# Load Data (Online CSV)
# ---------------------------------
DATA_URL = "https://raw.githubusercontent.com/vega/vega-datasets/master/data/seattle-weather.csv"

full_df = pd.read_csv(
    DATA_URL,
    parse_dates=["date"]
)

# ---------------------------------
# Page Config
# ---------------------------------
st.set_page_config(
    page_title="Seattle Weather Analytics",
    page_icon="🌦️",
    layout="wide",
)

# ---------------------------------
# Custom CSS
# ---------------------------------
st.markdown("""
<style>
.main {
    background-color: #f8f9fa;
}
.stMetric {
    background-color: black;
    padding: 15px;
    border-radius: 10px;
}
h1 { color: #1f77b4; }
h2 { color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# Title
# ---------------------------------
st.title("🌦️ Aesthetic Weather Analytics Dashboard")
st.markdown("*Comprehensive weather patterns and trends analysis*")

st.divider()

# ---------------------------------
# Year Selector
# ---------------------------------
st.subheader("📅 Select Years to Analyze")

YEARS = sorted(full_df["date"].dt.year.unique())
selected_years = st.multiselect(
    "Choose one or more years",
    YEARS,
    default=YEARS
)

if not selected_years:
    st.warning("⚠️ Please select at least one year.")
    st.stop()

df = full_df[full_df["date"].dt.year.isin(selected_years)]

st.divider()

# ---------------------------------
# Key Metrics
# ---------------------------------
st.subheader("📊 Key Weather Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_temp = df[["temp_max", "temp_min"]].mean().mean()
    st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f} °C")

with col2:
    total_precip = df["precipitation"].sum()
    st.metric("💧 Total Precipitation", f"{total_precip:.0f} mm")

with col3:
    avg_wind = df["wind"].mean()
    st.metric("💨 Avg Wind Speed", f"{avg_wind:.1f} m/s")

with col4:
    rainy_days = (df["precipitation"] > 0).sum()
    total_days = len(df)
    st.metric("🌧️ Rainy Days", f"{rainy_days}/{total_days}")

st.divider()

# =========================================================
# 🌥️ WEATHER TYPE DISTRIBUTION (DETAILED SECTION)
# =========================================================
st.subheader("☁️ Weather Type Distribution")
st.caption("Frequency and percentage of different weather conditions")

# Count days for each weather type
weather_counts = df["weather"].value_counts().reset_index()
weather_counts.columns = ["weather", "days"]

# Calculate percentages
total_days = weather_counts["days"].sum()
weather_counts["percentage"] = (
    weather_counts["days"] / total_days * 100
).round(2)

col1, col2 = st.columns([1.3, 2])

# ---- LEFT: Metrics ----
with col1:
    st.markdown("### 📊 Summary")

    weather_icons = {
        "sun": "☀️",
        "rain": "🌧️",
        "snow": "❄️",
        "fog": "🌫️",
        "drizzle": "🌦️"
    }

    for _, row in weather_counts.iterrows():
        icon = weather_icons.get(row["weather"], "🌈")
        st.metric(
            label=f"{icon} {row['weather'].title()}",
            value=f"{row['days']} days",
            delta=f"{row['percentage']}%"
        )

# ---- RIGHT: Pie Chart ----
with col2:
    weather_chart = alt.Chart(weather_counts).mark_arc(
        innerRadius=60,
        outerRadius=140
    ).encode(
        theta=alt.Theta("days:Q", title="Days"),
        color=alt.Color(
            "weather:N",
            scale=alt.Scale(scheme="tableau10"),
            legend=alt.Legend(title="Weather Type")
        ),
        tooltip=[
            alt.Tooltip("weather:N", title="Weather"),
            alt.Tooltip("days:Q", title="Days"),
            alt.Tooltip("percentage:Q", title="Percentage (%)")
        ]
    ).properties(
        height=400,
        title="Weather Type Breakdown"
    )

    st.altair_chart(weather_chart, use_container_width=True)

 #Optional table
#with st.expander("📋 View Weather Distribution Data"):
 #   st.dataframe(weather_counts, use_container_width=True)

st.divider()

# ---------------------------------
# Temperature Trends
# ---------------------------------
st.subheader("🌡️ Temperature Trends")

temp_chart = alt.Chart(df).mark_area(opacity=0.7).encode(
    x="date:T",
    y=alt.Y("temp_max:Q", scale=alt.Scale(zero=False)),
    y2="temp_min:Q",
    color="year(date):N",
    tooltip=[
        alt.Tooltip("date:T", format="%b %d, %Y"),
        alt.Tooltip("temp_max:Q", title="Max Temp"),
        alt.Tooltip("temp_min:Q", title="Min Temp"),
    ]
).properties(height=400).interactive()

st.altair_chart(temp_chart, use_container_width=True)

st.divider()

# ---------------------------------
# Monthly Precipitation
# ---------------------------------
st.subheader("💧 Monthly Precipitation")

precip_chart = alt.Chart(df).mark_bar().encode(
    x="month(date):O",
    y="sum(precipitation):Q",
    color="year(date):N",
    tooltip=["month(date):O", "sum(precipitation):Q"]
).properties(height=350)

st.altair_chart(precip_chart, use_container_width=True)

st.divider()

# ---------------------------------
# Wind Speed (7-day avg)
# ---------------------------------
st.subheader("💨 Wind Speed (7-Day Average)")

df_sorted = df.sort_values("date")
df_sorted["wind_avg_7d"] = df_sorted.groupby(
    df_sorted["date"].dt.year
)["wind"].transform(lambda x: x.rolling(7, min_periods=1).mean())

wind_chart = alt.Chart(df_sorted).mark_line(strokeWidth=2).encode(
    x="date:T",
    y="wind_avg_7d:Q",
    color="year(date):N",
    tooltip=["date:T", "wind_avg_7d:Q"]
).properties(height=350).interactive()

st.altair_chart(wind_chart, use_container_width=True)

st.divider()

# ---------------------------------
# Raw Data
# ---------------------------------
with st.expander("📋 View Raw Data"):
    st.dataframe(df, use_container_width=True)
    st.download_button(
        label="⬇️ Download Data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="seattle_weather_data.csv",
        mime="text/csv"
    )