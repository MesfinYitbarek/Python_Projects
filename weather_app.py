import tkinter as tk
from tkinter import messagebox
import requests

# Replace with your own OpenWeatherMap API key
API_KEY = "1ce794bc4590f06cc5de54fc4a820bd0"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data["cod"] != 200:
            messagebox.showerror("Error", f"City not found: {city}")
            return

        city_name = data["name"]
        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        result = f"🌍 {city_name}\n🌡️ Temp: {temp}°C\n☁️ {weather}\n💧 Humidity: {humidity}%\n🌬️ Wind: {wind} m/s"
        label_result.config(text=result)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch weather:\n{e}")

def on_search():
    city = entry_city.get().strip()
    if city:
        get_weather(city)
    else:
        messagebox.showwarning("Input needed", "Please enter a city name.")

# GUI
root = tk.Tk()
root.title("Weather App")
root.geometry("350x400")

label_title = tk.Label(root, text="🌤 Weather App", font=("Arial", 18, "bold"))
label_title.pack(pady=10)

entry_city = tk.Entry(root, font=("Arial", 14), justify="center")
entry_city.pack(pady=10)

btn_search = tk.Button(root, text="Search", font=("Arial", 14), command=on_search)
btn_search.pack(pady=10)

label_result = tk.Label(root, text="", font=("Arial", 14), justify="left")
label_result.pack(pady=20)

root.mainloop()
