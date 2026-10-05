import asyncio
import os
import nest_asyncio
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

nest_asyncio.apply()
load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL")
HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")

if not HOME_ASSISTANT_URL or not HOME_ASSISTANT_TOKEN or "put_your" in HOME_ASSISTANT_TOKEN:
    print("❌ Please copy .env.example to .env and fill HOME_ASSISTANT_URL and HOME_ASSISTANT_TOKEN")
    print("   HA > Profile > Security > Long-lived access tokens > Create")
    exit(1)

llm = ChatOllama(
    model=MODEL,
    temperature=0,
)

# --- BEGINNER MODE: stdio vs http ---
# Option A: Official HA integration from your screenshot (HTTP)
# Use this if you did Settings > Add integration > Model Context Protocol Server
# http_client = MultiServerMCPClient(
#    {
#        "homeassistant": {
#            "url": f"{HOME_ASSISTANT_URL}/api/mcp",  # try /mcp_server/sse if 404
#            "transport": "streamable_http",
#            "headers": {"Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}"}
#        }
#    }
#)

# Option B: Minimal GitHub repo (STDIO) - uncomment to use instead
# git clone https://github.com/envilleplease/ha_oc_mcp_server
# stdio_client = MultiServerMCPClient(
#     {
#         "homeassistant": {
#             "command": "python",
#             "args": ["ha_mcp_server.py"],
#             "transport": "stdio",
#             "env": {"HOME_ASSISTANT_URL": HOME_ASSISTANT_URL, "HOME_ASSISTANT_TOKEN": HOME_ASSISTANT_TOKEN}
#         }
#     }
# )

# Option C: Connecting to a simulated Home Assistant instance (gateway_simulator.py)
gateway_simulator_client = MultiServerMCPClient(
    {
        "homeassistant": {
            "command": "python",
            "args": ["gateway_simulator.py"],
            "url": "http://localhost:8000/sse",  # try /mcp_server/sse if 404
            "transport": "stdio",
            "env": {"HOME_ASSISTANT_URL": HOME_ASSISTANT_URL, "HOME_ASSISTANT_TOKEN": HOME_ASSISTANT_TOKEN}
        }
    }
)

client = gateway_simulator_client  # switch to stdio_client for even simpler mode

async def main():
    print(f"🤖 Model: {MODEL}")
    print(f"🏠 Connecting to {HOME_ASSISTANT_URL}...")
    try:
        tools = await client.get_tools()
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("Tip: If you get 404, change url to /mcp_server/sse and transport to 'sse'")
        return

    print(f"✅ Found {len(tools)} tools: {[t.name for t in tools[:10]]}")

    agent = create_agent(model = llm, tools = tools)

    print("\n💬 Type your request (e.g. 'list all lights', 'turn off kitchen')")
    print("   Type 'exit' to quit\n")

    while True:
        q = input("You: ")
        if q.lower() in ["exit", "quit"]:
            break
        try:
            response = await agent.ainvoke({"messages": [{"role": "user", "content": q}]})
            print(f"\nAgent: {response['messages'][-1].content}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
