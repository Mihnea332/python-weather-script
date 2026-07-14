import os
import requests
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Ntfy Weather App")


def fetch_weather():
    api_key = os.getenv("WEATHER_API_KEY")
    city = "Tălmaciu, RO"

    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=en"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=en"

    try:
        current_response = requests.get(current_url, timeout=10)
        current_response.raise_for_status()
        current_data = current_response.json()

        forecast_response = requests.get(forecast_url, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        current_temp = round(current_data["main"]["temp"])
        feels_like = round(current_data["main"]["feels_like"])
        description = current_data["weather"][0]["description"].capitalize()

        pop_decimal = forecast_data["list"][0].get("pop", 0)
        rain_chance = int(pop_decimal * 100)

        custom_message = (
            f"📍 Weather report for {city}:\n\n"
            f"🌡️ Temperature: {current_temp}°C (feels like {feels_like}°C)\n"
            f"🌤️ Conditions: {description}\n"
            f"☔ Chance of precipitation: {rain_chance}%\n\n"
            f"Have a great day! ☕"
        )

        return custom_message

    except requests.exceptions.Timeout:
        print("Internal error: OpenWeatherMap timeout.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except KeyError as e:
        print(f"Internal error (data structure): Missing key {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing weather: {e}")
        return None


def send_ntfy(weather_message):
    # Aici pui numele topicului la care te-ai abonat în aplicația de pe iOS
    # Îl extragem din .env sau punem o valoare directă (înlocuiește 'vremea_secret_123' cu al tău)
    topic = os.getenv("NTFY_TOPIC", "vremea_secret_123")
    url = f"https://ntfy.sh/{topic}"

    # Configurăm aspectul notificării (Titlu și un icon)
    headers = {
        "Title": "☀️ Raport Meteo",
        "Tags": "partly_sunny"
    }

    try:
        response = requests.post(
            url,
            data=weather_message.encode('utf-8'),
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending ntfy notification: {e}")
        return False


@app.get("/")
def home():
    return {"message": "The server is running"}


@app.get("/send-weather")
def trigger_notification():
    weather_message = fetch_weather()

    if not weather_message:
        raise HTTPException(
            status_code=500, detail="We couldn't extract the weather information."
        )

    # Apelăm noua funcție ntfy
    success = send_ntfy(weather_message)

    if not success:
        raise HTTPException(
            status_code=500, detail="Couldn't send ntfy message")

    return {
        "success": True,
        "message": "The notification was sent successfully via ntfy!"
    }
