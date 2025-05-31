import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPEN_WEATHER_MAP_API_KEY')

# App configuration
st.set_page_config(page_title="Weather Alert System", page_icon="⛈️", layout="wide")

# Title and description
st.title("🌦️ Real-Time Weather Alert System")
st.write("Get alerts when weather conditions exceed your thresholds")

# Sidebar inputs
city = st.sidebar.text_input("City Name", "London")
temp_threshold = st.sidebar.slider("Temperature Threshold (°C)", -20.0, 50.0, 30.0)
wind_threshold = st.sidebar.slider("Wind Speed Threshold (m/s)", 0.0, 30.0, 10.0)
update_frequency = st.sidebar.selectbox("Update Frequency (minutes)", [1, 5, 10, 15], index=1)

# Auto-refresh
count = st_autorefresh(interval=update_frequency * 60 * 1000, key="datarefresh")

status_placeholder = st.empty()
alert_placeholder = st.empty()

def fetch_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None

def check_alerts(data, temp_thresh, wind_thresh):
    if not data:
        return None

    temp = data['main']['temp']
    wind = data['wind']['speed']
    alerts = []

    if temp > temp_thresh:
        alerts.append(f"🌡️ High temperature: {temp}°C (threshold: {temp_thresh}°C)")
    if wind > wind_thresh:
        alerts.append(f"💨 Strong wind: {wind} m/s (threshold: {wind_thresh} m/s)")

    icon = data['weather'][0]['icon'] if data.get('weather') else None

    return {'temp': temp, 'wind': wind, 'alerts': alerts, 'icon': icon}

# Fetch and display weather 
if city:
    weather_data = fetch_weather(city)
    if weather_data:
        result = check_alerts(weather_data, temp_threshold, wind_threshold)

        # Display current weather
        col1, col2 = status_placeholder.columns(2)
        with col1:
            if result['icon']:
                st.image(f"http://openweathermap.org/img/wn/{result['icon']}@2x.png", width=100)
            st.metric("Temperature", f"{result['temp']}°C")
        with col2:
            st.metric("Wind Speed", f"{result['wind']} m/s")

        # Display alerts
        if result['alerts']:
            alert_placeholder.warning("## ⚠️ Weather Alerts")
            for alert in result['alerts']:
                alert_placeholder.error(alert)
        else:
            alert_placeholder.success("## ✅ All conditions normal")