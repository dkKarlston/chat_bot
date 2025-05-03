from argparse import Action
from pipes import quote
from tkinter import Text
from typing import Dict, List, Any

from google.auth.transport import requests
from rasa_sdk import Tracker, logger
from rasa_sdk.executor import CollectingDispatcher
import datetime
import random
from urllib.parse import quote


class ActionGetWeather(Action):
    def name(self) -> str:
        return "action_get_weather"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            dispatcher.utter_message(text="Не удалось определить город. Пожалуйста, уточните.")
            return []

        api_key = "c4aec831b9f8a6d4a4acc553848b76ff"

        try:

            city_encoded = quote(city)
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={api_key}&units=metric&lang=ru"

            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Проверяем HTTP-ошибки
            data = response.json()

            if data.get("cod") != 200:
                raise Exception(f"API error: {data.get('message', 'Unknown error')}")

            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            dispatcher.utter_message(text=f"В {city} сейчас {weather_desc}, {temp}°C")

        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Сервис погоды временно недоступен. Попробуйте позже.")
            logger.error(f"Weather API error: {e}")

        except Exception as e:
            dispatcher.utter_message(text="Произошла ошибка при получении погоды.")
            logger.error(f"Action error: {e}")

        return []

        api_key = "c4aec831b9f8a6d4a4acc553848b76ff"

        try:
            city_encoded = quote(city)
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={api_key}&units=metric&lang=ru"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            pressure = data["main"]["pressure"]
            sunrise_timestamp = data["sys"]["sunrise"]
            sunset_timestamp = data["sys"]["sunset"]

            sunrise_time = datetime.datetime.fromtimestamp(sunrise_timestamp).strftime("%H:%M")
            sunset_time = datetime.datetime.fromtimestamp(sunset_timestamp).strftime("%H:%M")

            weather_responses = [
                (f"В городе {city} сейчас {weather_desc}, температура {temp}°C, "
                 f"атмосферное давление {pressure} гПа.\n"
                 f"Время восхода: {sunrise_time}, время заката: {sunset_time}"),
                (f"Погода в {city}: {weather_desc}, {temp}°C, давление {pressure} гПа. "
                 f"Восход в {sunrise_time}, закат в {sunset_time}."),
                (f"Сейчас в {city} {weather_desc}, температура воздуха {temp} градусов Цельсия, "
                 f"давление {pressure} гектопаскалей. Солнце встало в {sunrise_time}, а сядет в {sunset_time}.")
            ]

            dispatcher.utter_message(text=random.choice(weather_responses))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                dispatcher.utter_message(text="Город не найден. Пожалуйста, уточните название города.")
            else:
                dispatcher.utter_message(text="Произошла ошибка при получении данных о погоде.")
        except Exception as e:
            dispatcher.utter_message(text=f"Произошла ошибка: {e}")

        return [SlotSet("city", None)]
