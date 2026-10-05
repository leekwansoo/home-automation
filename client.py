import asyncio
import os
import json
import threading
import tkinter as tk
from datetime import datetime
from dotenv import load_dotenv
import nest_asyncio
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

nest_asyncio.apply()
load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
URL = "http://localhost:8000/sse"


gateway_client = MultiServerMCPClient({"homeserver-mcp": {"url": URL, "transport": "sse"}})
client = gateway_client
agent = None
agent_loop = None

def fetch_default_lights():
    """Ask the home server (via MCP) for its default lights; empty list if unreachable."""
    async def fetch():
        tools = await client.get_tools()
        tool = next(t for t in tools if t.name == "get_default_lights")
        result = await tool.ainvoke({})
        if isinstance(result, str):
            return json.loads(result)
        blocks = [b["text"] if isinstance(b, dict) else b for b in result]
        parsed = [json.loads(b) if isinstance(b, str) else b for b in blocks]
        return parsed[0] if len(parsed) == 1 and isinstance(parsed[0], list) else parsed
    try:
        return asyncio.run(fetch())
    except Exception as e:
        print(f"Could not load default lights from {URL}: {e}")
        return []

DEFAULT_LIGHTS = fetch_default_lights()

async def init_agent():
    global agent
    try:
        tools = await client.get_tools()
        llm = ChatOllama(model=MODEL, temperature=0)
        agent = create_agent(model=llm, tools=tools)
    except Exception as e:
        print(f"UI-only mode: {e}")

def start_async_loop():
    global agent_loop
    agent_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(agent_loop)
    agent_loop.run_until_complete(init_agent())
    agent_loop.run_forever()

threading.Thread(target=start_async_loop, daemon=True).start()

class ToggleSwitch(tk.Canvas):
    """ON/OFF switch that lives INSIDE the cell - on=green, off=red"""
    def __init__(self, parent, initial_state="off", command=None, width=60, height=28):
        super().__init__(parent, width=width, height=height, bg="#2d2d2d", highlightthickness=0)
        self.state = initial_state
        self.command = command
        self.w = width
        self.h = height
        self.bind("<Button-1>", self.toggle)
        self.draw()

    def draw(self):
        self.delete("all")
        bg_color = "#2ecc71" if self.state == "on" else "#e74c3c"  # guideline
        self.create_oval(2, 2, self.h-2, self.h-2, fill=bg_color, outline=bg_color)
        self.create_oval(self.w-self.h+2, 2, self.w-2, self.h-2, fill=bg_color, outline=bg_color)
        self.create_rectangle(self.h//2, 2, self.w-self.h//2, self.h-2, fill=bg_color, outline=bg_color)
        knob_x = self.w - self.h//2 - 2 if self.state == "on" else self.h//2 + 2
        self.create_oval(knob_x-9, 4, knob_x+9, self.h-4, fill="white", outline="#ddd")

    def toggle(self, event=None):
        self.state = "on" if self.state == "off" else "off"
        self.draw()
        if self.command:
            self.command(self.state)

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.draw()

class LightTableUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LIGHT_TABLE - Switch + Brightness Slider")
        self.root.geometry("940x560")
        self.root.configure(bg="#1e1e1e")
        self.lights = {l["entity_id"]: l.copy() for l in DEFAULT_LIGHTS}
        self.rows_widgets = {}

        tk.Label(root, text="LIGHT_TABLE - ON/OFF Switch + Brightness Slider", bg="#1e1e1e", fg="white", font=("Arial", 13, "bold")).pack(pady=8)

        # Header
        header_frame = tk.Frame(root, bg="#111")
        header_frame.pack(fill="x", padx=10)
        headers = ["ENTITY_ID", "NAME", "ON/OFF [Switch]", "BRIGHTNESS [0-9]", "AREA", "STATUS"]
        for i, h in enumerate(headers):
            w = [22, 20, 18, 26, 12, 14][i]
            tk.Label(header_frame, text=h, bg="#111", fg="#03a9f4", width=w, font=("Arial", 9, "bold"), borderwidth=1, relief="solid").grid(row=0, column=i, padx=1, sticky="nsew")

        container = tk.Frame(root, bg="#1e1e1e")
        container.pack(fill="both", expand=True, padx=10, pady=5)
        canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, (ent_id, data) in enumerate(self.lights.items()):
            row_bg = "#2d2d2d" if idx % 2 == 0 else "#252525"
            row_frame = tk.Frame(scrollable_frame, bg=row_bg, borderwidth=1, relief="solid")
            row_frame.pack(fill="x", pady=1)

            tk.Label(row_frame, text=data["entity_id"], bg=row_bg, fg="#ccc", width=26, anchor="w", font=("Consolas", 9)).grid(row=0, column=0, padx=1, sticky="nsew")
            tk.Label(row_frame, text=data["name"], bg=row_bg, fg="white", width=20, anchor="w").grid(row=0, column=1, padx=1, sticky="nsew")

            # ON/OFF cell with switch inside
            on_off_cell = tk.Frame(row_frame, bg=row_bg, width=130, height=40)
            on_off_cell.grid(row=0, column=2, padx=1, sticky="nsew")
            on_off_cell.grid_propagate(False)
            switch = ToggleSwitch(on_off_cell, initial_state=data["state"], command=lambda new_state, eid=ent_id: self.on_switch_toggled(eid, new_state))
            switch.pack(expand=True)

            # BRIGHTNESS cell with SLIDER + UP/DOWN inside same cell (guideline 0-9)
            bright_cell = tk.Frame(row_frame, bg=row_bg, width=300, height=40)
            bright_cell.grid(row=0, column=3, padx=1, sticky="nsew")
            bright_cell.grid_propagate(False)

            # Inner frame to hold all brightness controls inside cell
            inner = tk.Frame(bright_cell, bg=row_bg)
            inner.pack(expand=True, fill="both")

            # Value label
            bright_label = tk.Label(inner, text=str(data["brightness"]), bg="#111", fg="white", width=2, font=("Arial", 11, "bold"))
            bright_label.pack(side="left", padx=2)

            # Down arrow
            btn_down = tk.Button(inner, text="▼", bg="#333", fg="white", font=("Arial", 7), width=2, height=1,
                                 command=lambda eid=ent_id: self.change_brightness(eid, -1))
            btn_down.pack(side="left", padx=1)

            # SLIDER inside cell (0-9) - key request
            slider = tk.Scale(inner, from_=0, to=9, orient="horizontal", bg=row_bg, fg="white",
                              highlightthickness=0, troughcolor="#444", activebackground="#03a9f4",
                              length=130, sliderlength=15, width=12, font=("Arial", 7),
                              command=lambda val, eid=ent_id: self.on_slider_change(eid, val))
            slider.set(data["brightness"])
            slider.pack(side="left", padx=2)

            # Up arrow
            btn_up = tk.Button(inner, text="▲", bg="#333", fg="white", font=("Arial", 7), width=2, height=1,
                               command=lambda eid=ent_id: self.change_brightness(eid, +1))
            btn_up.pack(side="left", padx=1)

            tk.Label(row_frame, text=data["area"], bg=row_bg, fg="#aaa", width=12).grid(row=0, column=4, padx=1, sticky="nsew")

            status_var = tk.StringVar(value=data["status"])
            status_menu = tk.OptionMenu(row_frame, status_var, "normal", "fault", "disconnected", command=lambda val, eid=ent_id: self.on_status_change(eid, val))
            status_menu.config(bg=row_bg, fg="white", width=12, highlightthickness=0)
            status_menu.grid(row=0, column=5, padx=1, sticky="nsew")

            self.rows_widgets[ent_id] = {
                "switch": switch,
                "brightness_label": bright_label,
                "slider": slider,
                "status_var": status_var,
            }

        log_frame = tk.Frame(root, bg="#1e1e1e")
        log_frame.pack(fill="both", padx=10, pady=5)
        tk.Label(log_frame, text="Agent Activation Log (switch & slider inside cell triggered):", bg="#1e1e1e", fg="#03a9f4", anchor="w", font=("Arial", 9, "bold")).pack(fill="x")
        self.log_text = tk.Text(log_frame, height=7, bg="#111", fg="#00ff88", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)

    def on_switch_toggled(self, entity_id, new_state):
        data = self.lights[entity_id]
        data["state"] = new_state
        if new_state == "on" and data["brightness"] == 0:
            data["brightness"] = 5
        if new_state == "off":
            data["brightness"] = 0
        w = self.rows_widgets[entity_id]
        w["brightness_label"].config(text=str(data["brightness"]))
        w["slider"].set(data["brightness"])
        self.log(f"🔘 [{entity_id}] switch inside cell -> {new_state.upper()} (green/red) | brightness={data['brightness']}")
        self.activate_agent(entity_id, new_state, data["brightness"])

    def on_slider_change(self, entity_id, val):
        # Avoid duplicate triggers from programmatic set
        try:
            new_val = int(float(val))
        except:
            return
        data = self.lights[entity_id]
        if new_val == data["brightness"]:
            return
        data["brightness"] = new_val
        data["state"] = "on" if new_val > 0 else "off"
        w = self.rows_widgets[entity_id]
        w["brightness_label"].config(text=str(new_val))
        w["switch"].set_state(data["state"])
        self.log(f"🎚️ [{entity_id}] slider inside cell -> brightness {new_val} (0-9) | state={data['state']}")
        self.activate_agent(entity_id, data["state"], new_val)

    def change_brightness(self, entity_id, delta):
        data = self.lights[entity_id]
        new_val = max(0, min(9, data["brightness"] + delta))
        if new_val == data["brightness"]:
            return
        data["brightness"] = new_val
        data["state"] = "on" if new_val > 0 else "off"
        w = self.rows_widgets[entity_id]
        w["brightness_label"].config(text=str(new_val))
        w["slider"].set(new_val)
        w["switch"].set_state(data["state"])
        self.log(f"🔆 [{entity_id}] ▲▼ inside cell -> {new_val}")
        self.activate_agent(entity_id, data["state"], new_val)

    def on_status_change(self, entity_id, new_status):
        self.lights[entity_id]["status"] = new_status
        self.log(f"📶 [{entity_id}] STATUS -> {new_status}")

    def log(self, msg):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.see("end")

    def activate_agent(self, entity_id, state, brightness):
        if not agent_loop or not agent:
            self.log(f"⚠️ UI-only: Would call turn_{state} {entity_id}")
            return
        async def call():
            try:
                prompt = f"User changed {entity_id} ({self.lights[entity_id]['name']}) to {state} brightness {brightness} area {self.lights[entity_id]['area']} status {self.lights[entity_id]['status']}. React."
                self.log(f"🤖 Activating {MODEL}...")
                resp = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
                content = resp["messages"][-1].content
                self.root.after(0, lambda: self.log(f"💬 Agent: {content[:200]}"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ {e}"))
        asyncio.run_coroutine_threadsafe(call(), agent_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = LightTableUI(root)
    root.mainloop()
