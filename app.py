from datetime import datetime
import streamlit as st
import altair as alt
import vega_datasets
import pandas as pd

full_df = vega_datasets.data("seattle_weather")

st.set_page_config(
    page_title="Seattle Weather Analytics",
    page_icon="🌦️",
    layout="wide",
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        font-weight: 700;
    }
    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 2rem;
    }
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌦️Asthetic Weather Analytics Of  Dashboard")
st.markdown("*Comprehensive weather patterns and trends analysis*")

st.divider()

# Year selector at the top
st.subheader("📅 Select Years to Analyze")
YEARS = sorted(full_df["date"].dt.year.unique())
selected_years = st.pills(
    "Choose one or more years",
    YEARS,
    default=YEARS,
    selection_mode="multi"
)

if not selected_years:
    st.warning("⚠️ Please select at least one year to view the data.", icon="⚠️")
    st.stop()

df = full_df[full_df["date"].dt.year.isin(selected_years)]

st.divider()

# Key Metrics Section
st.subheader("📊 Key Weather Statistics")
st.caption(f"Summary for selected year(s): {', '.join(map(str, selected_years))}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_temp = df[["temp_max", "temp_min"]].mean().mean()
    st.metric(
        "Average Temperature",
        f"{avg_temp:.1f}°C",
        help="Mean of daily high and low temperatures"
    )

with col2:
    total_precip = df["precipitation"].sum()
    st.metric(
        "Total Precipitation",
        f"{total_precip:.0f} mm",
        help="Cumulative rainfall across selected period"
    )

with col3:
    avg_wind = df["wind"].mean()
    st.metric(
        "Average Wind Speed",
        f"{avg_wind:.1f} m/s",
        help="Mean wind speed across all days"
    )

with col4:
    rainy_days = len(df[df["precipitation"] > 0])
    total_days = len(df)
    st.metric(
        "Rainy Days",
        f"{rainy_days} / {total_days}",
        f"{(rainy_days/total_days*100):.0f}%",
        help="Days with measurable precipitation"
    )

st.divider()

# Weather Distribution
st.subheader("☁️ Weather Type Distribution")
weather_counts = df["weather"].value_counts().reset_index()
weather_counts.columns = ["weather", "count"]

weather_icons = {
    "sun": "☀️",
    "snow": "❄️",
    "rain": "🌧️",
    "fog": "🌫️",
    "drizzle": "🌦️",
}

col1, col2 = st.columns([2, 3])

with col1:
    for _, row in weather_counts.iterrows():
        weather_type = row["weather"]
        count = row["count"]
        pct = (count / total_days) * 100
        icon = weather_icons.get(weather_type, "🌈")
        st.metric(
            f"{icon} {weather_type.title()}",
            f"{count} days",
            f"{pct:.1f}%"
        )

with col2:
    # Add percentage column for tooltip
    weather_counts["percentage"] = (weather_counts["count"] / total_days * 100).round(1)
    
    pie_chart = alt.Chart(weather_counts).mark_arc(innerRadius=50, outerRadius=120).encode(
        theta=alt.Theta("count:Q", stack=True),
        color=alt.Color("weather:N", 
                       scale=alt.Scale(scheme='tableau10'),
                       legend=alt.Legend(title="Weather Type", orient="right")),
        tooltip=[
            alt.Tooltip("weather:N", title="Type"),
            alt.Tooltip("count:Q", title="Days"),
            alt.Tooltip("percentage:Q", title="Percentage", format=".1f")
        ]
    ).properties(
        width=350,
        height=350,
        title="Weather Type Breakdown"
    )
    st.altair_chart(pie_chart, use_container_width=True)

st.divider()

# Temperature Time Series
st.subheader("🌡️ Temperature Patterns Over Time")
st.caption("Daily temperature ranges showing highs and lows")

temp_chart = alt.Chart(df).mark_area(opacity=0.7).encode(
    x=alt.X("date:T", title="Date", axis=alt.Axis(format="%b %Y", labelAngle=-45)),
    y=alt.Y("temp_max:Q", title="Temperature (°C)", scale=alt.Scale(zero=False)),
    y2=alt.Y2("temp_min:Q"),
    color=alt.Color("year(date):N", 
                   scale=alt.Scale(scheme='category10'),
                   legend=alt.Legend(title="Year", orient="top")),
    tooltip=[
        alt.Tooltip("date:T", title="Date", format="%b %d, %Y"),
        alt.Tooltip("temp_max:Q", title="High", format=".1f"),
        alt.Tooltip("temp_min:Q", title="Low", format=".1f"),
        alt.Tooltip("weather:N", title="Weather")
    ]
).properties(
    height=400
).interactive()

st.altair_chart(temp_chart, use_container_width=True)

st.divider()

# Precipitation and Wind Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("💧 Monthly Precipitation Totals")
    
    precip_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("month(date):O", title="Month", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("sum(precipitation):Q", title="Total Precipitation (mm)"),
        color=alt.Color("year(date):N", 
                       scale=alt.Scale(scheme='blues'),
                       legend=alt.Legend(title="Year", orient="top")),
        xOffset=alt.XOffset("year(date):N"),
        tooltip=[
            alt.Tooltip("month(date):O", title="Month"),
            alt.Tooltip("year(date):N", title="Year"),
            alt.Tooltip("sum(precipitation):Q", title="Precipitation (mm)", format=".1f")
        ]
    ).properties(
        height=350
    )
    
    st.altair_chart(precip_chart, use_container_width=True)

with col2:
    st.subheader("💨 Wind Speed Trends")
    
    # Calculate 7-day rolling average
    df_sorted = df.sort_values("date")
    df_sorted["wind_avg_7d"] = df_sorted.groupby(df_sorted["date"].dt.year)["wind"].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    
    wind_chart = alt.Chart(df_sorted).mark_line(strokeWidth=2).encode(
        x=alt.X("date:T", title="Date", axis=alt.Axis(format="%b %Y", labelAngle=-45)),
        y=alt.Y("wind_avg_7d:Q", title="Wind Speed (m/s) - 7-day avg"),
        color=alt.Color("year(date):N", 
                       scale=alt.Scale(scheme='set2'),
                       legend=alt.Legend(title="Year", orient="top")),
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%b %d, %Y"),
            alt.Tooltip("wind_avg_7d:Q", title="7-day Avg Wind", format=".2f")
        ]
    ).properties(
        height=350
    ).interactive()
    
    st.altair_chart(wind_chart, use_container_width=True)

st.divider()

# Monthly Weather Breakdown
st.subheader("📅 Monthly Weather Patterns")
st.caption("Proportion of weather types throughout the year")

monthly_weather = alt.Chart(df).mark_bar().encode(
    x=alt.X("month(date):O", title="Month", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("count():Q", title="Proportion of Days", stack="normalize"),
    color=alt.Color("weather:N", 
                   scale=alt.Scale(scheme='tableau10'),
                   legend=alt.Legend(title="Weather Type", orient="top")),
    tooltip=[
        alt.Tooltip("month(date):O", title="Month"),
        alt.Tooltip("weather:N", title="Weather"),
        alt.Tooltip("count():Q", title="Days")
    ]
).properties(
    height=300
)

st.altair_chart(monthly_weather, use_container_width=True)

st.divider()

# Raw Data Section
with st.expander("📋 View Raw Data", expanded=False):
    st.dataframe(
        df.sort_values("date", ascending=False),
        use_container_width=True,
        height=400
    )