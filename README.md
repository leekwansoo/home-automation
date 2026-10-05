# Home-Automation

src/mcp_homeserver.py: homegateway server

client.py: read and control the lights and fan switches thru homegateway server

Step1: clone this repository

```text
git clone https://github.com/leekwansoo/home-automation.git
```

Step2: initiate uv  with "uv init"

if you do not have installed uv package in your pc install uv package with "pip install uv"

Step3: create venv with "uv venv": this will create .venv directory

Step4: activate the venv environment with ".venv/Scripts/activate"

Step5: install dependencies with "uv pip install -r requirements.txt"

Step6: copy the environment variables from env_example.txt into your .env file

Step7: Run the server from your terminal with "python src/mcp_homeserver.py"

Step8: Create another terminal and run the client program with "python client.py"

You will see "Light_Table UI" popped up