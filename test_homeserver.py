import json
import sys
import unittest
from typing import Any

from fastmcp import Client

from src.mcp_homeserver import mcp

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class HomeServerMCPTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = Client(mcp)
        await self.client.__aenter__()

    async def asyncTearDown(self):
        await self.client.__aexit__(None, None, None)

    async def call_tool(self, name: str, arguments: dict[str, object]) -> Any:
        result = await self.client.call_tool(name, arguments)
        self.assertFalse(result.is_error, f"{name} returned an MCP tool error")
        self.assertTrue(
            all(content.type == "text" for content in result.content),
            f"{name} returned non-text MCP content",
        )
        values = [json.loads(content.text) for content in result.content]
        return values[0] if len(values) == 1 else values

    async def test_registered_tools_and_light_service_flow(self):
        tools = await self.client.list_tools()
        self.assertEqual(
            {tool.name for tool in tools},
            {
                "ha_list_entities",
                "ha_get_state",
                "ha_call_service",
                "ha_get_config",
            },
        )

        lights = await self.call_tool("ha_list_entities", {"domain": "light"})
        self.assertEqual(len(lights), 5)
        self.assertIn("light.living_room", {light["entity_id"] for light in lights})

        state = await self.call_tool(
            "ha_get_state", {"entity_id": "light.living_room"}
        )
        self.assertEqual(state["state"], "off")

        turned_on = await self.call_tool(
            "ha_call_service",
            {
                "domain": "light",
                "service": "turn_on",
                "entity_id": "light.living_room",
                "brightness": 128,
            },
        )
        self.assertTrue(turned_on["success"])
        self.assertEqual(turned_on["new_state"]["state"], "on")
        self.assertEqual(turned_on["new_state"]["brightness"], 128)

        turned_off = await self.call_tool(
            "ha_call_service",
            {
                "domain": "light",
                "service": "turn_off",
                "entity_id": "light.living_room",
            },
        )
        self.assertTrue(turned_off["success"])
        self.assertEqual(turned_off["new_state"]["state"], "off")

        config = await self.call_tool("ha_get_config", {})
        self.assertEqual(config["entities_count"], 6)
        self.assertEqual(config["mode"], "SIMULATOR - No real hardware")


if __name__ == "__main__":
    unittest.main()
