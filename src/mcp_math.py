from typing import Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import os
import sys 
from math import sqrt
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("math", dependencies=["requests"])

@mcp.tool()
def square(number: float) -> float:
    """
    Calculate the square of a number.

    Args:
        number (float): Input number

    Returns:
        float: Square of the input number
    """
    return number * number

@mcp.tool()
def square_root(number: float) -> float:
    """
    Calculate the square root of a number.

    Args:
        number (float): Input number

    Returns:
        float: Square root of the input number

    Raises:
        ValueError: If the number is negative
    """
    if number < 0:
        raise ValueError("Square root of negative numbers is not allowed.")

    return sqrt(number)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")