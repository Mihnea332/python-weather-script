import os
import requests
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

def send_whatsapp(weather_message):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    your_number = os.getenv("YOUR_PHONE_NUMBER")
    
    try:
        client = Client(sid, token)
        message = client.messages.create(
            body=weather_message,
            from_=twilio_number,
            to=your_number
        )
        print(f"Message sent successfully! ID: {message.sid}")
    except TwilioRestException as e:
        print(f"Twilio Error: {e.msg}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Punctul de intrare pentru GitHub Actions
if __name__ == "__main__":
    print("Fetching weather...")
    msg = fetch_weather()
    if msg:
        print("Sending WhatsApp message...")
        send_whatsapp(msg)
    else:
        print("Could not get weather data. Message not sent.")Tălmaciu, RO
