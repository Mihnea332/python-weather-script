import os
import requests
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Ntfy Weather App")

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

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
        
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None


def send_ntfy(weather_message):
    topic = os.getenv("NTFY_TOPIC", "vremea_secret_123")
    url = f"https://ntfy.sh/{topic}"
    headers = {
        "Title": "Weather report",
        "Tags": "partly_sunny"
    }

def send_whatsapp(weather_message):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    your_number = os.getenv("YOUR_PHONE_NUMBER")
    
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

    success = send_ntfy(weather_message)

    if not success:
        raise HTTPException(
            status_code=500, detail="Couldn't send ntfy message")

    return {
        "success": True,
        "message": "The notification was sent successfully via ntfy!"
    }
        print(f"Message sent successfully! ID: {message.sid}")
    except TwilioRestException as e:
        print(f"Twilio Error: {e.msg}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    print("Se rulează automatizarea de pe GitHub...")
    mesaj = fetch_weather()
    if mesaj:
        rezultat = send_ntfy(mesaj)
        if rezultat:
            print("Notificarea ntfy a fost trimisă cu succes!")
        else:
            print("Eroare la trimiterea notificării.")
    else:
        print("Nu s-au putut extrage datele meteo.")
