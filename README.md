# Home-Automation

src/mcp_homeserver.py: homegateway server

client.py: read and control the lights and fan switches thru homegateway server

Step1: clone this repository

```text
git clone https://github.com/leekwansoo/home-automation.git
```

Step2: initiate uv  with 
```text
uv init
```

if you do not have installed uv package in your pc install uv package with 
```text
pip install uv
```

Step3: create venv with 
```text
uv venv
```

Step4: activate the venv environment with 
```text
.venv/Scripts/activate
```

Step5: install dependencies with 
```text
uv pip install -r requirements.txt
```

Step6: copy the environment variables from env_example.txt into your .env file

Step7: Run the server from your terminal with
```text
python src/mcp_homeserver.py
```

Step8: Create another terminal and run the client program with 

```text
python client.py
```

Voila!! 
You will see "Light_Table UI" popped up.
Now you can navigate thru the "LIGHT_TABLE UI"