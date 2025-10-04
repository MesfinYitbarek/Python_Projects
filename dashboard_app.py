import streamlit as st
import requests
import datetime

# -------------------------------
# Configuration
# -------------------------------
API_KEY = "1ce794bc4590f06cc5de54fc4a820bd0"  # 🔑 Replace with your OpenWeatherMap API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

st.set_page_config(page_title="🌦️ Weather Dashboard", layout="centered")

st.title("🌦️ Real-Time Weather Dashboard")
st.markdown("Enter a city name below to view the latest weather data.")

# -------------------------------
# Input
# -------------------------------
city = st.text_input("🏙️ City Name", placeholder="e.g. Addis Ababa, London, Tokyo")

# -------------------------------
# Fetch Weather Data
# -------------------------------
def get_weather(city_name):
    params = {"q": city_name, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

if city:
    data = get_weather(city)
    if data:
        # Extract info
        name = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        description = data["weather"][0]["description"].capitalize()
        icon = data["weather"][0]["icon"]

        # Display
        st.subheader(f"📍 {name}, {country}")
        st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png", width=100)
        st.metric("🌡️ Temperature (°C)", f"{temp:.1f}", delta=None)
        st.metric("💧 Humidity", f"{humidity}%")
        st.metric("🌬️ Wind Speed", f"{wind} m/s")
        st.write(f"**Condition:** {description}")
        st.write(f"Feels like: {feels_like:.1f}°C")

        # Timestamp
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Updated on: {now}")
    else:
        st.error("❌ City not found or API key invalid. Please check and try again.")
else:
    st.info("👆 Enter a city name to view the weather.")
