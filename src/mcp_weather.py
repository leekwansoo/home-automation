from typing import Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import os
import sys 
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("weather", dependencies=["requests"])

@mcp.tool()
def get_weather(city: str) -> dict[str, Any]:
    """Get current weather for a location"""
    # Using https://openweathermap.org/current#geo
    print(f"Fetching weather for city: {city}")
    api_key = os.getenv("OPENWEATHER_API_KEY")
    print(api_key)
    # Get the latitude and longitude of the city.
    geo_url = (
        f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    )
    # print(f"city weather: {city}")
    response = requests.get(geo_url)
    geo_data = response.json()
    print(geo_data)
    if not geo_data:
        raise ValueError(f"Could not find location: {city}")
    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    # Get the current weather for the city.
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    weather_data = requests.get(weather_url).json()
    temperature = weather_data["main"]["temp"]
    description = weather_data["weather"][0]["main"]

    return {
        "location": city,
        "temperature": temperature,
        "description": description,
    }


if __name__ == "__main__":
    print("get_weather is running")
    mcp.run()
