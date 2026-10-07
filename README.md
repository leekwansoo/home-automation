# Prerequisite before Starting this Project

if the Ollama is installed, install ollama  in your PC

Step1: Goto Ollama download site from your browser
```text
https://github.com/ollama/ollama/releases/tag/v0.35.0
```
Download the file
.  OllamaSetup.exe

Execute the Downloaded setup file

Verify the installed version
```text
ollama --version
```
Step2:

Download the Qwen-Model from PowerShell Terminal
```text
ollama pull qwen2.5:05b
```
Then you are Ready to start your project

# Home-Automation

Step1: clone this repository

Open a Power Shell Terminal in the Desktop Window 

```text
git clone https://github.com/leekwansoo/home-automation.git
```
Step2: Open the downloaded file with VS Code

Step3: Create a VS Code terminal and initiate uv in the VS Code terminal:

```text
uv init
```

if you do not have installed uv package in your pc install uv package: 
```text
pip install uv
```

Step4: create venv: 
```text
uv venv
```

Step5: activate the venv environment with 
```text
.venv/Scripts/activate
```

Step6: install dependencies. 

```text
uv pip install -r requirements.txt
```

Step7: copy the environment variables from env_example.txt into your .env file:

Step8: Create an another command terminal in DeskTop window and Run the server from your terminal:
```text
python src/mcp_homeserver.py
```

Step9: Create another terminal and run the client program: 

```text
python client.py
```

Voila!! 
You will see "Light_Table UI" popped up.
Now you can navigate thru the "LIGHT_TABLE UI"
