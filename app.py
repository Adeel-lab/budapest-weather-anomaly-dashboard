import streamlit as st
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

st.set_page_config(page_title="Budapest Weather Anomaly Dashboard", layout="wide")
st.title("🌦️ Budapest Weather Anomaly Dashboard")
st.caption("Live hourly data from Open-Meteo — anomalies detected using Z-score (threshold: ±3σ)")

@st.cache_data(ttl=3600)
def load_data():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 47.4979,
        "longitude": 19.0402,
        "start_date": "2020-01-01",
        "end_date": pd.Timestamp.today().strftime("%Y-%m-%d"),
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m", "apparent_temperature"],
        "timezone": "Europe/Budapest"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()

    df = pd.DataFrame({
        "date":                 pd.date_range(start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                                              end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                                              freq=pd.Timedelta(seconds=hourly.Interval()), inclusive="left"),
        "temperature_2m":       hourly.Variables(0).ValuesAsNumpy(),
        "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
        "precipitation":        hourly.Variables(2).ValuesAsNumpy(),
        "wind_speed_10m":       hourly.Variables(3).ValuesAsNumpy(),
        "apparent_temperature": hourly.Variables(4).ValuesAsNumpy(),
    })

    df["date"] = df["date"].dt.tz_convert("Europe/Budapest")
    df["Month"] = df["date"].dt.month
    df["Hour"]  = df["date"].dt.hour

    for col, label in [
        ("temperature_2m",       "temp"),
        ("relative_humidity_2m", "humidity"),
        ("precipitation",        "precipitation"),
        ("wind_speed_10m",       "wind_speed"),
        ("apparent_temperature", "apparent_temperature"),
    ]:
        df[f"expected_mean_{label}"] = df.groupby(["Month", "Hour"])[col].transform("mean")
        df[f"expected_std_{label}"]  = df.groupby(["Month", "Hour"])[col].transform("std")
        df[f"anomaly_score_{label}"] = (df[col] - df[f"expected_mean_{label}"]) / df[f"expected_std_{label}"]

    anomaly_cols = [f"anomaly_score_{l}" for l in ["temp", "humidity", "precipitation", "wind_speed", "apparent_temperature"]]
    df["is_anomaly"] = (df[anomaly_cols].abs() > 3).any(axis=1)

    return df

with st.spinner("Loading live data..."):
    df = load_data()

latest = df.iloc[-1]
anomaly_rate = df["is_anomaly"].mean() * 100

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🌡️ Temperature",  f"{latest['temperature_2m']:.1f} °C")
col2.metric("💧 Humidity",      f"{latest['relative_humidity_2m']:.0f} %")
col3.metric("🌧️ Precipitation", f"{latest['precipitation']:.1f} mm")
col4.metric("💨 Wind Speed",    f"{latest['wind_speed_10m']:.1f} km/h")
col5.metric("🚨 Anomaly Rate",  f"{anomaly_rate:.2f} %")

st.divider()

st.subheader("📈 Last 72 Hours — Temperature")
last_72 = df.tail(72)
st.line_chart(last_72.set_index("date")[["temperature_2m", "expected_mean_temp"]])

st.divider()

st.subheader("🚨 Most Recent Anomalies")
anomalies = df[df["is_anomaly"]].tail(20)[["date", "temperature_2m", "relative_humidity_2m",
                                            "precipitation", "wind_speed_10m",
                                            "anomaly_score_temp", "anomaly_score_precipitation",
                                            "anomaly_score_wind_speed"]].sort_values("date", ascending=False)
st.dataframe(anomalies, use_container_width=True)

st.divider()

st.subheader("📅 Anomalies by Month")
monthly = df[df["is_anomaly"]].groupby("Month").size().reset_index(name="count")
monthly["Month"] = monthly["Month"].map({1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                                          7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"})
st.bar_chart(monthly.set_index("Month"))
