"""
Home Assistant MCP Gateway Simulator
- No real hardware needed
- Works with your main.py (VSCode + LangChain + Ollama)
- Exposes same tools as real HA MCP server

Usage:
  pip install fastmcp
  python mcp_homeserver.py --server_type sse --port 8000

Then in main.py change to:
  "url": "http://localhost:8000/sse",
  "transport": "sse"
"""
import json
import os
from pathlib import Path
import argparse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ha-gateway")

# In-memory lights - this is your virtual home
with open(Path(__file__).parent / "lights.json", encoding="utf-8") as f:
    DEFAULT_LIGHTS = json.load(f)  # initial light definitions (list), shared with client.py

# Working state keyed by entity_id; copies keep DEFAULT_LIGHTS pristine
LIGHTS = {entity["entity_id"]: entity.copy() for entity in DEFAULT_LIGHTS}

@mcp.tool()
def get_default_lights() -> list:
    """Get the initial light definitions (entity_id, name, state, brightness, area, status)."""
    return DEFAULT_LIGHTS

@mcp.tool()
def ha_list_entities(domain: str = "", area: str = "", search: str = "") -> list:
    """List all entities. Filter by domain (light, switch), area, or search text."""
    result = []
    for entity_id, data in LIGHTS.items():
        if domain and not entity_id.startswith(domain):
            continue
        if area and data.get("area") != area:
            continue
        if search and search.lower() not in data["name"].lower():
            continue
        result.append({
            "entity_id": entity_id,
            "name": data["name"],
            "state": data["state"],
            "area": data["area"],
            "brightness": data.get("brightness", 0)
        })
    return result

@mcp.tool()
def ha_get_state(entity_id: str) -> dict:
    """Get current state of a specific light/switch."""
    if entity_id not in LIGHTS:
        return {"error": f"Entity {entity_id} not found"}
    return {"entity_id": entity_id, **LIGHTS[entity_id]}

@mcp.tool()
def ha_get_all_state() -> dict:
    """Get current state of all light/switches."""
    current_lights_state = []
    for entity_id, data in LIGHTS.items():
        LIGHTS[entity_id] = data
        current_lights_state.append({
            "entity_id": entity_id,
            "name": data["name"],
            "state": data["state"],
            "area": data["area"],
            "brightness": data.get("brightness", 0),
            "status": data.get("status", "normal")
        })
    print(f"Current lights state: {current_lights_state}")
    return current_lights_state

@mcp.tool()
def ha_call_service(domain: str, service: str, entity_id: str, brightness: int | None = None, status: str = "") -> dict:
    """Call service to turn on/off light. service = turn_on or turn_off. Optional brightness (0-9) and status."""
    if entity_id not in LIGHTS:
        return {"error": "not found"}
    
    light = LIGHTS[entity_id]
    if service == "turn_on":
        light["state"] = "on"
        print(f"💡 SIMULATOR: {light['name']} -> ON")
    elif service == "turn_off":
        light["state"] = "off"
        print(f"🌙 SIMULATOR: {light['name']} -> OFF")
    if brightness is not None:
        light["brightness"] = brightness
    if status:
        light["status"] = status

    return {"success": True, "entity_id": entity_id, "new_state": light}

@mcp.tool()
def ha_get_config() -> dict:
    """Get  HA config"""
    return {
        "version": "2026.10.0",
        "location": "Seongnam, Korea",
        "entities_count": len(LIGHTS),
        "mode": "SIMULATOR - No real hardware"
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_type", type=str, default="sse", choices=["sse", "stdio"])
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    mcp.settings.port = args.port
    
    print(f"🚀 HA Gateway Simulator running on port {args.port}")
    print(f"   Lights: {list(LIGHTS)}")
    print(f"   Connect your main.py to http://localhost:{args.port}/sse")
    mcp.run(args.server_type)
