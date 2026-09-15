error inside the server terminal:

source /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/activate
bash: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/activate: No such file or directory
siddhant@siddhant-Vivobook-ASUSLaptop-K5504VA-S5504VA:~/project/onlystudies/OnlyStudy$ cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Put GOOGLE_API_KEY=... in server/.env
uvicorn app.main:app --reload
bash: /home/siddhant/project/onlystudies/OnlyStudy/server/.venv/bin/pip: cannot execute: required file not found
bash: /home/siddhant/project/onlystudies/OnlyStudy/server/.venv/bin/uvicorn: cannot execute: required file not found
(.venv) siddhant@siddhant-Vivobook-ASUSLaptop-K5504VA-S5504VA:~/project/onlystudies/OnlyStudy/server$ ^C
(.venv) siddhant@siddhant-Vivobook-ASUSLaptop-K5504VA-S5504VA:~/project/onlystudies/OnlyStudy/server$ 


error inside the client terminal: 

$ cd client
npm install
npm run dev
⠋^C

> onlystudies-client@1.0.0 dev
> vite

sh: 1: vite: not found
(.venv) siddhant@siddhant-Vivobook-ASUSLaptop-K5504VA-S5504VA:~/project/onlystudies/OnlyStudy/client$ ls
index.html  package.json  src  tsconfig.json
(.venv) siddhant@siddhant-Vivobook-ASUSLaptop-K5504VA-S5504VA:~/project/onlystudies/OnlyStudy/client$ npm install
⠏^C
(.venv) siddhant@siddhant-Vivobook-ASUSLaptop-K5504VA-S5504VA:~/project/onlystudies/OnlyStudy/client$ npm run dev]
npm error Missing script: "dev]"
npm error
npm error Did you mean this?
npm error   npm run dev # run the "dev" package script
npm error
npm error To see a list of scripts, run:
npm error   npm run
npm error A complete log of this run can be found in: /home/siddhant/.npm/_logs/2026-09-15T15_37_26_631Z-debug-0.log
(.venv) siddhant@siddhant-Vivobook-ASUSLaptop-K5504VA-S5504VA:~/project/onlystudies/OnlyStudy/client$ npm run dev

> onlystudies-client@1.0.0 dev
> vite

sh: 1: vite: not found
(.venv) siddhant@siddhant-Vivobook-ASUSLaptop-K5504VA-S5504VA:~/project/onlystudies/OnlyStudy/client$ 


logs:

2026-09-15 20:28:35.577 [info] Python-envs extension version: 1.36.0
2026-09-15 20:28:35.577 [info] 
=== Python Envs Configuration Levels ===
2026-09-15 20:28:35.577 [info] {
  "section": "Python Envs Configuration Levels",
  "defaultEnvManager": {
    "workspaceFolderValue": "undefined",
    "workspaceValue": "undefined",
    "globalValue": "undefined",
    "defaultValue": "ms-python.python:venv"
  },
  "defaultPackageManager": {
    "workspaceFolderValue": "undefined",
    "workspaceValue": "undefined",
    "globalValue": "undefined",
    "defaultValue": "ms-python.python:pip"
  }
}
2026-09-15 20:28:35.577 [info] [pet] Starting Python Locator /home/siddhant/.vscode/extensions/ms-python.vscode-python-envs-1.36.0-linux-x64/python-env-tools/bin/pet server
2026-09-15 20:28:35.577 [info] Registering pyenv manager (environments will be discovered lazily)
2026-09-15 20:28:35.577 [info] Registering pipenv manager (environments will be discovered lazily)
2026-09-15 20:28:35.577 [info] Registering poetry manager (environments will be discovered lazily)
2026-09-15 20:28:35.577 [info] Using conda from persistent state: /home/siddhant/miniconda3/condabin/conda
2026-09-15 20:28:35.577 [info] Conda Sourcing Status:
├─ Conda Path: /home/siddhant/miniconda3/condabin/conda
├─ Conda Folder: /home/siddhant/miniconda3
├─ Active on Launch: true
└─ No Shell-specific Sourcing Scripts Found
2026-09-15 20:28:35.577 [info] [interpreterSelection] Applying initial environment selection for 1 workspace folder(s)
2026-09-15 20:28:35.577 [info] [pet] configure: Sending configuration update: {"workspaceDirectories":["/home/siddhant/project/onlystudies/OnlyStudy"],"environmentDirectories":["/home/siddhant/project/onlystudies/OnlyStudy/.venv","/home/siddhant/project/onlystudies/OnlyStudy/*/.venv"],"pipenvExecutable":"pipenv","poetryExecutable":"poetry","cacheDirectory":"/home/siddhant/.config/Code/User/globalStorage/ms-python.vscode-python-envs/pythonLocator"}
2026-09-15 20:28:35.600 [info] Refreshing Pyenv Environments
2026-09-15 20:28:35.600 [info] Refreshing pyenv environments
2026-09-15 20:28:35.600 [info] Refreshing Pipenv Environments
2026-09-15 20:28:35.600 [info] Refreshing pipenv environments
2026-09-15 20:28:35.600 [info] Refreshing Poetry Environments
2026-09-15 20:28:35.600 [info] Refreshing poetry environments
2026-09-15 20:28:35.600 [info] Refreshing Conda Environments
2026-09-15 20:28:35.600 [info] Refreshing conda environments (hardRefresh=true)
2026-09-15 20:28:35.605 [info] Discovered env: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 20:28:36.782 [error] [pet] [2m   0.100102742s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Python in "/home/siddhant/miniconda3", trying slower approach
[2m   0.102047071s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Conda in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:37.443 [info] Discovered manager: (Conda) /home/siddhant/miniconda3/bin/conda
2026-09-15 20:28:37.510 [info] Discovered env: /home/siddhant/project/Langchain/Chatbot/venv/bin/python
2026-09-15 20:28:37.626 [info] Discovered env: /home/siddhant/miniconda3/bin/python
2026-09-15 20:28:37.648 [info] Discovered env: /usr/bin/python3
2026-09-15 20:28:37.723 [error] [pet] [2m   2.190386770s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Python in "/home/siddhant/miniconda3", trying slower approach
[2m   2.191122019s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Conda in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:37.753 [info] Discovered env: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 20:28:37.773 [info] Discovered manager: (Conda) /home/siddhant/miniconda3/bin/conda
2026-09-15 20:28:37.825 [info] Found venv environment: venv (3.12.3)
2026-09-15 20:28:37.849 [info] Discovered env: /home/siddhant/project/Langchain/Chatbot/venv/bin/python
2026-09-15 20:28:38.060 [info] Discovered env: /home/siddhant/miniconda3/bin/python
2026-09-15 20:28:38.305 [info] Discovered env: /usr/bin/python3
2026-09-15 20:28:38.306 [info] Python API: Changed environment from undefined to venv (3.12.3) for: /home/siddhant/project/onlystudies/OnlyStudy
2026-09-15 20:28:38.306 [info] Internal: Changed environment from undefined to venv (3.12.3) for: /home/siddhant/project/onlystudies/OnlyStudy
2026-09-15 20:28:38.306 [info] [interpreterSelection] OnlyStudy: venv (3.12.3) (source: autoDiscovery)
2026-09-15 20:28:38.306 [info] [interpreterSelection] Workspace env resolved, deferring global scope to background
2026-09-15 20:28:38.896 [info] Python API: Changed environment from undefined to Python 3.12.3.final.0 for: global
2026-09-15 20:28:38.896 [info] Internal: Changed environment from undefined to Python 3.12.3.final.0 for: global
2026-09-15 20:28:38.896 [info] [interpreterSelection] global: Python 3.12.3.final.0 (source: autoDiscovery)
2026-09-15 20:28:38.946 [error] [pet] [2m   3.417573422s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Python in "/home/siddhant/miniconda3", trying slower approach
[2m   3.418637132s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Conda in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:38.947 [info] Discovered env: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 20:28:38.963 [info] Discovered env: /usr/bin/python3
2026-09-15 20:28:38.985 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:28:39.006 [info] Discovered manager: (Conda) /home/siddhant/miniconda3/bin/conda
2026-09-15 20:28:39.036 [info] Discovered env: /home/siddhant/miniconda3/bin/python
2026-09-15 20:28:39.051 [info] Discovered env: /home/siddhant/project/Langchain/Chatbot/venv/bin/python
2026-09-15 20:28:39.057 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:28:39.059 [info] Found venv environment: venv (3.12.3)
2026-09-15 20:28:39.064 [info] Python API: Changed environment from venv (3.12.3) to venv (3.12.3) for: /home/siddhant/project/onlystudies/OnlyStudy
2026-09-15 20:28:39.064 [info] Internal: Changed environment from venv (3.12.3) to venv (3.12.3) for: /home/siddhant/project/onlystudies/OnlyStudy
2026-09-15 20:28:39.065 [info] Refreshing pyenv environments
2026-09-15 20:28:39.068 [info] Discovered env: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 20:28:39.087 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:28:39.088 [info] Refreshing conda environments (hardRefresh=false)
2026-09-15 20:28:39.089 [info] Using conda from cache: /home/siddhant/miniconda3/condabin/conda
2026-09-15 20:28:39.090 [info] === Conda Shell Activation Map Generation ===
Environment Configuration:
    - Identifier: "base"
    - Prefix: "/home/siddhant/miniconda3"
    - Name: "base"

✓ Conda already active on launch, using default activation commands
==========================================
2026-09-15 20:28:39.090 [info] === Conda Shell Activation Map Generation ===
Environment Configuration:
    - Identifier: "/home/siddhant/project/Langchain/Chatbot/venv"
    - Prefix: "/home/siddhant/project/Langchain/Chatbot/venv"
    - Name: "undefined"

✓ Conda already active on launch, using default activation commands
==========================================
2026-09-15 20:28:39.090 [info] Found base environment: /home/siddhant/miniconda3
2026-09-15 20:28:39.090 [info] Found prefix environment: /home/siddhant/project/Langchain/Chatbot/venv
2026-09-15 20:28:39.091 [error] [pet] [2m   3.575255044s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Python in "/home/siddhant/miniconda3", trying slower approach
[2m   3.575745239s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Conda in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:39.093 [info] Discovered env: /usr/bin/python3
2026-09-15 20:28:39.093 [info] Discovered manager: (Conda) /home/siddhant/miniconda3/bin/conda
2026-09-15 20:28:39.093 [info] Discovered env: /home/siddhant/miniconda3/bin/python
2026-09-15 20:28:39.093 [info] Discovered env: /home/siddhant/project/Langchain/Chatbot/venv/bin/python
2026-09-15 20:28:39.098 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:28:39.103 [info] Pipenv not found via settings, cache, or PATH
2026-09-15 20:28:39.103 [info] Refreshing pipenv environments
2026-09-15 20:28:39.105 [info] Pipenv not found via settings, cache, or PATH
2026-09-15 20:28:39.105 [info] Found 0 pipenv environments
2026-09-15 20:28:39.107 [info] Discovered env: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 20:28:39.107 [info] Pipenv not found via settings, cache, or PATH
2026-09-15 20:28:39.132 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:28:39.133 [error] [pet] [2m   3.618019592s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Python in "/home/siddhant/miniconda3", trying slower approach
[2m   3.618836091s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Conda in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:39.134 [info] Discovered env: /usr/bin/python3
2026-09-15 20:28:39.134 [info] Discovered manager: (Conda) /home/siddhant/miniconda3/bin/conda
2026-09-15 20:28:39.134 [info] Discovered env: /home/siddhant/project/Langchain/Chatbot/venv/bin/python
2026-09-15 20:28:39.134 [info] Discovered env: /home/siddhant/miniconda3/bin/python
2026-09-15 20:28:39.134 [info] Refreshing poetry environments
2026-09-15 20:28:39.135 [info] Poetry executable not found
2026-09-15 20:28:39.141 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:28:39.143 [info] Pipenv not found via settings, cache, or PATH
2026-09-15 20:28:39.143 [info] Found 0 pipenv environments
2026-09-15 20:28:39.146 [info] Discovered env: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 20:28:39.166 [error] [pet] [2m   3.652373295s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Python in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:39.167 [error] [pet] [2m   3.652992606s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Conda in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:39.168 [info] Discovered env: /usr/bin/python3
2026-09-15 20:28:39.168 [info] Discovered manager: (Conda) /home/siddhant/miniconda3/bin/conda
2026-09-15 20:28:39.168 [info] Discovered env: /home/siddhant/miniconda3/bin/python
2026-09-15 20:28:39.168 [info] Discovered env: /home/siddhant/project/Langchain/Chatbot/venv/bin/python
2026-09-15 20:28:39.177 [info] Poetry executable not found
2026-09-15 20:28:39.192 [info] Discovered env: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 20:28:39.203 [error] [pet] [2m   3.688652842s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Python in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:39.203 [error] [pet] [2m   3.689243899s[0m [33m WARN[0m [2mpet_conda::package[0m[2m:[0m Unable to find conda package Conda in "/home/siddhant/miniconda3", trying slower approach

2026-09-15 20:28:39.203 [info] Discovered env: /usr/bin/python3
2026-09-15 20:28:39.204 [info] Discovered manager: (Conda) /home/siddhant/miniconda3/bin/conda
2026-09-15 20:28:39.204 [info] Discovered env: /home/siddhant/project/Langchain/Chatbot/venv/bin/python
2026-09-15 20:28:39.204 [info] Discovered env: /home/siddhant/miniconda3/bin/python
2026-09-15 20:28:39.210 [info] Using conda from cache: /home/siddhant/miniconda3/condabin/conda
2026-09-15 20:28:39.210 [info] === Conda Shell Activation Map Generation ===
Environment Configuration:
    - Identifier: "/home/siddhant/project/Langchain/Chatbot/venv"
    - Prefix: "/home/siddhant/project/Langchain/Chatbot/venv"
    - Name: "undefined"

✓ Conda already active on launch, using default activation commands
==========================================
2026-09-15 20:28:39.211 [info] === Conda Shell Activation Map Generation ===
Environment Configuration:
    - Identifier: "base"
    - Prefix: "/home/siddhant/miniconda3"
    - Name: "base"

✓ Conda already active on launch, using default activation commands
==========================================
2026-09-15 20:28:39.211 [info] Found prefix environment: /home/siddhant/project/Langchain/Chatbot/venv
2026-09-15 20:28:39.211 [info] Found base environment: /home/siddhant/miniconda3
2026-09-15 20:28:43.311 [error] Shell execution timed out:  source /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/activate
2026-09-15 20:28:43.312 [info] Terminal is activated: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 20:28:43.315 [info] Environment discovery complete: 4 environments found (Global: 1, venv: 1, Conda: 2)
2026-09-15 20:30:04.710 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:30:04.719 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:30:04.726 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:30:04.734 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:30:04.741 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:30:04.747 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:57:07.734 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:57:07.740 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:57:07.745 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:57:07.750 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:57:07.755 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:57:07.760 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 20:57:08.371 [info] Running: uv --version
2026-09-15 20:57:08.371 [info] Running: uv --version
2026-09-15 20:57:08.382 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json
2026-09-15 20:57:08.391 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json --not-required
2026-09-15 20:57:08.524 [info] python: [{"name": "altair", "version": "6.2.2"}, {"name": "annotated-types", "version": "0.8.0"}, {"name": "anyio", "version": "4.15.1"}, {"name": "attrs", "version": "26.1.0"}, {"name": "av", "version": "18.1.0"}, {"name": "beautifulsoup4", "version": "4.15.0"}, {"name": "certifi", "version": "2026.7.22"}, {"name": "cffi", "version": "2.1.1"}, {"name": "charset-normalizer", "version": "3.5.1"}, {"name": "click", "version": "8.1.8"}, {"name": "cloup", "version": "3.1.0"}, {"name": "cryptography", "version": "50.0.1"}, {"name": "decorator", "version": "5.3.1"}, {"name": "distro", "version": "1.9.0"}, {"name": "dotenv", "version": "0.9.9"}, {"name": "glcontext", "version": "3.0.0"}, {"name": "google-ai-generativelanguage", "version": "0.6.15"}, {"name": "google-api-core", "version": "2.33.0"}, {"name": "google-api-python-client", "version": "2.200.0"}, {"name": "google-auth", "version": "2.57.1"}, {"name": "google-auth-httplib2", "version": "0.4.2"}, {"name": "google-genai", "version": "2.22.0"}, {"name": "google-generativeai", "version": "0.8.6"}, {"name": "googleapis-common-protos", "version": "1.75.0"}, {"name": "grpcio", "version": "1.83.1"}, {"name": "grpcio-status", "version": "1.71.2"}, {"name": "gTTS", "version": "2.5.4"}, {"name": "h11", "version": "0.16.0"}, {"name": "httpcore", "version": "1.0.9"}, {"name": "httplib2", "version": "0.32.0"}, {"name": "httptools", "version": "0.8.0"}, {"name": "httpx", "version": "0.28.1"}, {"name": "idna", "version": "3.19"}, {"name": "isosurfaces", "version": "0.1.2"}, {"name": "itsdangerous", "version": "2.2.0"}, {"name": "Jinja2", "version": "3.1.6"}, {"name": "jsonschema", "version": "4.26.0"}, {"name": "jsonschema-specifications", "version": "2025.9.1"}, {"name": "manim", "version": "0.21.0"}, {"name": "manim-voiceover", "version": "0.4.0"}, {"name": "ManimPango", "version": "0.6.1"}, {"name": "mapbox_earcut", "version": "2.1.0"}, {"name": "markdown-it-py", "version": "4.2.0"}, {"name": "MarkupSafe", "version": "3.0.3"}, {"name": "mdurl", "version": "0.1.2"}, {"name": "moderngl", "version": "5.12.0"}, {"name": "moderngl-window", "version": "3.1.1"}, {"name": "mutagen", "version": "1.48.1"}, {"name": "narwhals", "version": "2.26.0"}, {"name": "networkx", "version": "3.6.1"}, {"name": "numpy", "version": "2.5.3"}, {"name": "packaging", "version": "26.3"}, {"name": "pandas", "version": "3.0.5"}, {"name": "pillow", "version": "12.3.0"}, {"name": "pip", "version": "26.2.1"}, {"name": "proto-plus", "version": "1.28.2"}, {"name": "protobuf", "version": "5.29.6"}, {"name": "pyarrow", "version": "25.0.1"}, {"name": "pyasn1", "version": "0.6.4"}, {"name": "pyasn1_modules", "version": "0.4.2"}, {"name": "pycairo", "version": "1.29.1"}, {"name": "pycparser", "version": "3.0"}, {"name": "pydantic", "version": "2.13.5"}, {"name": "pydantic_core", "version": "2.46.5"}, {"name": "pydeck", "version": "0.9.3"}, {"name": "pydub", "version": "0.25.1"}, {"name": "pyglet", "version": "2.1.16"}, {"name": "pyglm", "version": "2.8.3"}, {"name": "Pygments", "version": "2.21.0"}, {"name": "pyparsing", "version": "3.3.2"}, {"name": "python-dateutil", "version": "2.9.0.post0"}, {"name": "python-dotenv", "version": "1.2.3"}, {"name": "python-multipart", "version": "0.0.32"}, {"name": "python-slugify", "version": "8.0.4"}, {"name": "referencing", "version": "0.37.0"}, {"name": "requests", "version": "2.34.2"}, {"name": "rich", "version": "15.0.0"}, {"name": "rpds-py", "version": "2026.6.3"}, {"name": "scipy", "version": "1.18.1"}, {"name": "screeninfo", "version": "0.8.1"}, {"name": "six", "version": "1.17.0"}, {"name": "skia-pathops", "version": "0.9.2"}, {"name": "sniffio", "version": "1.3.1"}, {"name": "soupsieve", "version": "2.9.2"}, {"name": "sox", "version": "1.5.0"}, {"name": "srt", "version": "3.5.3"}, {"name": "starlette", "version": "1.6.0"}, {"name": "streamlit", "version": "1.63.0"}, {"name": "svgelements", "version": "1.9.6"}, {"name": "tenacity", "version": "9.1.4"}, {"name": "text-unidecode", "version": "1.3"}, {"name": "toml", "version": "0.10.2"}, {"name": "tqdm", "version": "4.70.0"}, {"name": "typing_extensions", "version": "4.16.0"}, {"name": "typing-inspection", "version": "0.4.4"}, {"name": "uritemplate", "version": "4.2.0"}, {"name": "urllib3", "version": "2.7.0"}, {"name": "uvicorn", "version": "0.52.4"}, {"name": "watchdog", "version": "6.0.0"}, {"name": "websockets", "version": "16.1.1"}]

2026-09-15 20:57:08.562 [info] python: [{"name": "dotenv", "version": "0.9.9"}, {"name": "google-genai", "version": "2.22.0"}, {"name": "google-generativeai", "version": "0.8.6"}, {"name": "grpcio-status", "version": "1.71.2"}, {"name": "gTTS", "version": "2.5.4"}, {"name": "manim-voiceover", "version": "0.4.0"}, {"name": "streamlit", "version": "1.63.0"}]

2026-09-15 20:57:27.796 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json
2026-09-15 20:57:27.810 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json --not-required
2026-09-15 20:57:27.931 [info] python: [{"name": "altair", "version": "6.2.2"}, {"name": "annotated-types", "version": "0.8.0"}, {"name": "anyio", "version": "4.15.1"}, {"name": "attrs", "version": "26.1.0"}, {"name": "av", "version": "18.1.0"}, {"name": "beautifulsoup4", "version": "4.15.0"}, {"name": "certifi", "version": "2026.7.22"}, {"name": "cffi", "version": "2.1.1"}, {"name": "charset-normalizer", "version": "3.5.1"}, {"name": "click", "version": "8.1.8"}, {"name": "cloup", "version": "3.1.0"}, {"name": "cryptography", "version": "50.0.1"}, {"name": "decorator", "version": "5.3.1"}, {"name": "distro", "version": "1.9.0"}, {"name": "dotenv", "version": "0.9.9"}, {"name": "glcontext", "version": "3.0.0"}, {"name": "google-ai-generativelanguage", "version": "0.6.15"}, {"name": "google-api-core", "version": "2.33.0"}, {"name": "google-api-python-client", "version": "2.200.0"}, {"name": "google-auth", "version": "2.57.1"}, {"name": "google-auth-httplib2", "version": "0.4.2"}, {"name": "google-genai", "version": "2.22.0"}, {"name": "google-generativeai", "version": "0.8.6"}, {"name": "googleapis-common-protos", "version": "1.75.0"}, {"name": "grpcio", "version": "1.83.1"}, {"name": "grpcio-status", "version": "1.71.2"}, {"name": "gTTS", "version": "2.5.4"}, {"name": "h11", "version": "0.16.0"}, {"name": "httpcore", "version": "1.0.9"}, {"name": "httplib2", "version": "0.32.0"}, {"name": "httptools", "version": "0.8.0"}, {"name": "httpx", "version": "0.28.1"}, {"name": "idna", "version": "3.19"}, {"name": "isosurfaces", "version": "0.1.2"}, {"name": "itsdangerous", "version": "2.2.0"}, {"name": "Jinja2", "version": "3.1.6"}, {"name": "jsonschema", "version": "4.26.0"}, {"name": "jsonschema-specifications", "version": "2025.9.1"}, {"name": "manim", "version": "0.21.0"}, {"name": "manim-voiceover", "version": "0.4.0"}, {"name": "ManimPango", "version": "0.6.1"}, {"name": "mapbox_earcut", "version": "2.1.0"}, {"name": "markdown-it-py", "version": "4.2.0"}, {"name": "MarkupSafe", "version": "3.0.3"}, {"name": "mdurl", "version": "0.1.2"}, {"name": "moderngl", "version": "5.12.0"}, {"name": "moderngl-window", "version": "3.1.1"}, {"name": "mutagen", "version": "1.48.1"}, {"name": "narwhals", "version": "2.26.0"}, {"name": "networkx", "version": "3.6.1"}, {"name": "numpy", "version": "2.5.3"}, {"name": "packaging", "version": "26.3"}, {"name": "pandas", "version": "3.0.5"}, {"name": "pillow", "version": "12.3.0"}, {"name": "pip", "version": "26.2.1"}, {"name": "proto-plus", "version": "1.28.2"}, {"name": "protobuf", "version": "5.29.6"}, {"name": "pyarrow", "version": "25.0.1"}, {"name": "pyasn1", "version": "0.6.4"}, {"name": "pyasn1_modules", "version": "0.4.2"}, {"name": "pycairo", "version": "1.29.1"}, {"name": "pycparser", "version": "3.0"}, {"name": "pydantic", "version": "2.13.5"}, {"name": "pydantic_core", "version": "2.46.5"}, {"name": "pydeck", "version": "0.9.3"}, {"name": "pydub", "version": "0.25.1"}, {"name": "pyglet", "version": "2.1.16"}, {"name": "pyglm", "version": "2.8.3"}, {"name": "Pygments", "version": "2.21.0"}, {"name": "pyparsing", "version": "3.3.2"}, {"name": "python-dateutil", "version": "2.9.0.post0"}, {"name": "python-dotenv", "version": "1.2.3"}, {"name": "python-multipart", "version": "0.0.32"}, {"name": "python-slugify", "version": "8.0.4"}, {"name": "referencing", "version": "0.37.0"}, {"name": "requests", "version": "2.34.2"}, {"name": "rich", "version": "15.0.0"}, {"name": "rpds-py", "version": "2026.6.3"}, {"name": "scipy", "version": "1.18.1"}, {"name": "screeninfo", "version": "0.8.1"}, {"name": "six", "version": "1.17.0"}, {"name": "skia-pathops", "version": "0.9.2"}, {"name": "sniffio", "version": "1.3.1"}, {"name": "soupsieve", "version": "2.9.2"}, {"name": "sox", "version": "1.5.0"}, {"name": "srt", "version": "3.5.3"}, {"name": "starlette", "version": "1.6.0"}, {"name": "streamlit", "version": "1.63.0"}, {"name": "svgelements", "version": "1.9.6"}, {"name": "tenacity", "version": "9.1.4"}, {"name": "text-unidecode", "version": "1.3"}, {"name": "toml", "version": "0.10.2"}, {"name": "tqdm", "version": "4.70.0"}, {"name": "typing_extensions", "version": "4.16.0"}, {"name": "typing-inspection", "version": "0.4.4"}, {"name": "uritemplate", "version": "4.2.0"}, {"name": "urllib3", "version": "2.7.0"}, {"name": "uvicorn", "version": "0.52.4"}, {"name": "watchdog", "version": "6.0.0"}, {"name": "websockets", "version": "16.1.1"}]

2026-09-15 20:57:27.958 [info] python: [{"name": "dotenv", "version": "0.9.9"}, {"name": "google-genai", "version": "2.22.0"}, {"name": "google-generativeai", "version": "0.8.6"}, {"name": "grpcio-status", "version": "1.71.2"}, {"name": "gTTS", "version": "2.5.4"}, {"name": "manim-voiceover", "version": "0.4.0"}, {"name": "streamlit", "version": "1.63.0"}]

2026-09-15 20:58:04.204 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json
2026-09-15 20:58:04.214 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json --not-required
2026-09-15 20:58:04.331 [info] python: [{"name": "altair", "version": "6.2.2"}, {"name": "annotated-types", "version": "0.8.0"}, {"name": "anyio", "version": "4.15.1"}, {"name": "attrs", "version": "26.1.0"}, {"name": "av", "version": "18.1.0"}, {"name": "beautifulsoup4", "version": "4.15.0"}, {"name": "certifi", "version": "2026.7.22"}, {"name": "cffi", "version": "2.1.1"}, {"name": "charset-normalizer", "version": "3.5.1"}, {"name": "click", "version": "8.1.8"}, {"name": "cloup", "version": "3.1.0"}, {"name": "cryptography", "version": "50.0.1"}, {"name": "decorator", "version": "5.3.1"}, {"name": "distro", "version": "1.9.0"}, {"name": "dotenv", "version": "0.9.9"}, {"name": "glcontext", "version": "3.0.0"}, {"name": "google-ai-generativelanguage", "version": "0.6.15"}, {"name": "google-api-core", "version": "2.33.0"}, {"name": "google-api-python-client", "version": "2.200.0"}, {"name": "google-auth", "version": "2.57.1"}, {"name": "google-auth-httplib2", "version": "0.4.2"}, {"name": "google-genai", "version": "2.22.0"}, {"name": "google-generativeai", "version": "0.8.6"}, {"name": "googleapis-common-protos", "version": "1.75.0"}, {"name": "grpcio", "version": "1.83.1"}, {"name": "grpcio-status", "version": "1.71.2"}, {"name": "gTTS", "version": "2.5.4"}, {"name": "h11", "version": "0.16.0"}, {"name": "httpcore", "version": "1.0.9"}, {"name": "httplib2", "version": "0.32.0"}, {"name": "httptools", "version": "0.8.0"}, {"name": "httpx", "version": "0.28.1"}, {"name": "idna", "version": "3.19"}, {"name": "isosurfaces", "version": "0.1.2"}, {"name": "itsdangerous", "version": "2.2.0"}, {"name": "Jinja2", "version": "3.1.6"}, {"name": "jsonschema", "version": "4.26.0"}, {"name": "jsonschema-specifications", "version": "2025.9.1"}, {"name": "manim", "version": "0.21.0"}, {"name": "manim-voiceover", "version": "0.4.0"}, {"name": "ManimPango", "version": "0.6.1"}, {"name": "mapbox_earcut", "version": "2.1.0"}, {"name": "markdown-it-py", "version": "4.2.0"}, {"name": "MarkupSafe", "version": "3.0.3"}, {"name": "mdurl", "version": "0.1.2"}, {"name": "moderngl", "version": "5.12.0"}, {"name": "moderngl-window", "version": "3.1.1"}, {"name": "mutagen", "version": "1.48.1"}, {"name": "narwhals", "version": "2.26.0"}, {"name": "networkx", "version": "3.6.1"}, {"name": "numpy", "version": "2.5.3"}, {"name": "packaging", "version": "26.3"}, {"name": "pandas", "version": "3.0.5"}, {"name": "pillow", "version": "12.3.0"}, {"name": "pip", "version": "26.2.1"}, {"name": "proto-plus", "version": "1.28.2"}, {"name": "protobuf", "version": "5.29.6"}, {"name": "pyarrow", "version": "25.0.1"}, {"name": "pyasn1", "version": "0.6.4"}, {"name": "pyasn1_modules", "version": "0.4.2"}, {"name": "pycairo", "version": "1.29.1"}, {"name": "pycparser", "version": "3.0"}, {"name": "pydantic", "version": "2.13.5"}, {"name": "pydantic_core", "version": "2.46.5"}, {"name": "pydeck", "version": "0.9.3"}, {"name": "pydub", "version": "0.25.1"}, {"name": "pyglet", "version": "2.1.16"}, {"name": "pyglm", "version": "2.8.3"}, {"name": "Pygments", "version": "2.21.0"}, {"name": "pyparsing", "version": "3.3.2"}, {"name": "python-dateutil", "version": "2.9.0.post0"}, {"name": "python-dotenv", "version": "1.2.3"}, {"name": "python-multipart", "version": "0.0.32"}, {"name": "python-slugify", "version": "8.0.4"}, {"name": "referencing", "version": "0.37.0"}, {"name": "requests", "version": "2.34.2"}, {"name": "rich", "version": "15.0.0"}, {"name": "rpds-py", "version": "2026.6.3"}, {"name": "scipy", "version": "1.18.1"}, {"name": "screeninfo", "version": "0.8.1"}, {"name": "six", "version": "1.17.0"}, {"name": "skia-pathops", "version": "0.9.2"}, {"name": "sniffio", "version": "1.3.1"}, {"name": "soupsieve", "version": "2.9.2"}, {"name": "sox", "version": "1.5.0"}, {"name": "srt", "version": "3.5.3"}, {"name": "starlette", "version": "1.6.0"}, {"name": "streamlit", "version": "1.63.0"}, {"name": "svgelements", "version": "1.9.6"}, {"name": "tenacity", "version": "9.1.4"}, {"name": "text-unidecode", "version": "1.3"}, {"name": "toml", "version": "0.10.2"}, {"name": "tqdm", "version": "4.70.0"}, {"name": "typing_extensions", "version": "4.16.0"}, {"name": "typing-inspection", "version": "0.4.4"}, {"name": "uritemplate", "version": "4.2.0"}, {"name": "urllib3", "version": "2.7.0"}, {"name": "uvicorn", "version": "0.52.4"}, {"name": "watchdog", "version": "6.0.0"}, {"name": "websockets", "version": "16.1.1"}]

2026-09-15 20:58:04.345 [info] python: [{"name": "dotenv", "version": "0.9.9"}, {"name": "google-genai", "version": "2.22.0"}, {"name": "google-generativeai", "version": "0.8.6"}, {"name": "grpcio-status", "version": "1.71.2"}, {"name": "gTTS", "version": "2.5.4"}, {"name": "manim-voiceover", "version": "0.4.0"}, {"name": "streamlit", "version": "1.63.0"}]

2026-09-15 21:04:44.506 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:44.512 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:44.520 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:44.527 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:44.534 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:44.542 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:53.383 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:53.389 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:53.393 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:53.399 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:53.404 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:04:53.410 [info] Resolved Python Environment /usr/bin/python3
2026-09-15 21:05:42.514 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json
2026-09-15 21:05:42.523 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json --not-required
2026-09-15 21:05:42.524 [error] Error spawning python: Error: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:05:42.524 [error] Error spawning python: Error: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:05:42.524 [error] Error running pip list Error spawning python: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:05:42.524 [info] Package list retrieval attempted using pip, action can be done with uv if installed and setting `alwaysUseUv` is enabled.
2026-09-15 21:05:42.525 [error] Error running pip list Error spawning python: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:05:42.525 [info] Package list retrieval attempted using pip, action can be done with uv if installed and setting `alwaysUseUv` is enabled.
2026-09-15 21:05:42.525 [error] Error refreshing packages Error spawning python: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:06:22.906 [info] Terminal is activated: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python
2026-09-15 21:08:35.365 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json
2026-09-15 21:08:35.374 [info] Running: /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python -m pip list --format=json --not-required
2026-09-15 21:08:35.374 [error] Error spawning python: Error: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:08:35.374 [error] Error spawning python: Error: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:08:35.374 [error] Error running pip list Error spawning python: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:08:35.374 [info] Package list retrieval attempted using pip, action can be done with uv if installed and setting `alwaysUseUv` is enabled.
2026-09-15 21:08:35.375 [error] Error running pip list Error spawning python: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT
2026-09-15 21:08:35.375 [info] Package list retrieval attempted using pip, action can be done with uv if installed and setting `alwaysUseUv` is enabled.
2026-09-15 21:08:35.375 [error] Error refreshing packages Error spawning python: spawn /home/siddhant/project/onlystudies/OnlyStudy/venv/bin/python ENOENT



fix these issues and implement them and write the learnings inside the spec02.learning.md