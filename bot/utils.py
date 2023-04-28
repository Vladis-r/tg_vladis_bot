import os

import aiohttp
from dotenv import load_dotenv

load_dotenv()


async def get_weather(city: str) -> str | None:
    """
    Функция для получения данных с API openweathermap.
    Принимает: имя города.
    Возвращает: строку о погоде или None
    """
    access_key = os.environ.get("OWM_API_KEY")
    url = os.environ.get("OWM_API_URL")

    async with aiohttp.ClientSession() as session:
        async with session.get(url.format(city, access_key)) as resp:
            if resp.status == 200:
                weather_data = await resp.json()

                weather_description = weather_data['weather'][0]['description']
                temperature = weather_data['main']['temp']
                city = weather_data["name"]
                humidity = weather_data["main"]["humidity"]
                pressure_hpa = weather_data["main"]["pressure"]
                pressure_mmhg = pressure_hpa * float(os.getenv("MILIMETRE_OF_MERCURY"))

                return f"В городе {city} {weather_description}, температура воздуха {round(temperature)}°C, влажность {humidity}%, давление {pressure_mmhg} мм рт.ст."
            else:
                return None


async def get_exchange_rate(amount: int, cur_from: str, cur_to: str) -> str:
    """
    Функция для конвертирования валюты.
    Принимает:
        :param amount: количество
        :param cur_from: из какой валюты конверт.
        :param cur_to: в какую валюту конверт.
    Возвращает: результат конвертации или сообщение об ошибке.
    """
    access_key = os.getenv("EXCHANGE_RATE_API_KEY")
    url = os.getenv("EXCHANGE_RATE_API_URL")
    async with aiohttp.ClientSession() as session:
        headers = {
            "apikey": access_key
        }
        async with session.get(url.format(amount, cur_from, cur_to),
                               headers=headers) as resp:
            if resp.status == 401:
                exchange_rate = await resp.json()
                error = exchange_rate["message"]
                return f"Ошибка авторизации: {error}"

            if resp.status == 200:
                exchange_rate = await resp.json()
                result = exchange_rate["result"]
                rate = exchange_rate["info"]["rate"]
                return f"Результат: {result}. По курсу: {rate}"
            else:
                return f"Сервер в данный момент недоступен (статус:{resp.status}). Попробуйте позднее."


async def get_image() -> None | str:
    """
    Функция для показа случайной картинки по поисковому запросу.
    Возвращает картинку или None.
    """
    access_key = os.getenv("UNSP_ACCESS_KEY")
    url = os.getenv("UNSP_API_URL")
    query = os.getenv("UNSP_QUERY")

    async with aiohttp.ClientSession() as session:
        async with session.get(url.format(access_key, query)) as resp:
            if resp.status == 200:
                image_json = await resp.json()
                image = image_json["urls"]["small"]
                return image
            else:
                return None

