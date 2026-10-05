import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
from src.mcp_weather import get_weather
from src.mcp_math import add, multiply, square, square_root
city = "Seoul"
response =get_weather(city)
print(response)

response = add(3, 5)
print(response)

response = multiply(3, 5)
print(response)

response = square(4)
print(response)

response = square_root(16)
print(response)