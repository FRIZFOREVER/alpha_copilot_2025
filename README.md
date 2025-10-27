## Setting up for dev

For windows: make sure you are running git bash terminal inside VS Code, not powershell

update pip and install uv 
```bash
pip install --upgrade pip
pip install uv
```

create venv via uv inside ml:
```bash
cd ml
uv venv
```

### Sync project

#### Linux

```bash
source .venv/bin/activate 
uv sync
```

#### Windows 

```bash
source .venv/scripts/activate
uv sync
```

### VS code setup
VS code exclude cache setup + quicks:
Open File -> Preferences -> Settings -> Search: exclude
Inside "files: exclude" -> add patterns: 
1. `**/__pycache__` - python cache
2. `**/*.pyc` - python runtime cache
3. `**/.pytest_cache` - pytest cache
4. (OPTIONAL) `/.venv` - local environment
5. (OPTIONAL) `/.git` - git folder (can be excluded via other setting, search git instead RECOMMENDED)

### VS Code .venv
Setup current local environment to make Pylance Shut up:
ctrl+shift+P -> Python: Select Interpreter -> Enter Interpreter path -> navigate according to OS:
- linux    - `agent-base/ml/.venv/bin/activate`
- windows  - `agent-base/ml/.venv/scripts/python.exe`

## Running the API

Make sure you are in project folder and venv is activated

```bash
cd ml
source .venv/bin/activate
uv sync
```

uvicorn canonical launch:
```bash
uv run uvicorn ml.main:app --host 0.0.0.0 --port 8000
```
Additional logging:
```bash
uv run uvicorn ml.main:app --host 0.0.0.0 --port 8000 --log-config ./src/ml/configs/logging.yaml --access-log
```
Ctrl+C to stop server

Test via making calls from another terminal (docker compose ver):
```bash
curl http://localhost:8000/ping 
# Should get inside curl terminal:
# {"message":"pong"} 
# and inside server terminal / logs: 
# INFO:     127.0.0.1:45744 - "GET /ping HTTP/1.1" 200 OK
curl http://localhost:8000/health 
# Should get inside curl terminal:
# {"status":"healthy"} 
# and inside server terminal / logs:
# INFO:     127.0.0.1:45750 - "GET /health HTTP/1.1" 200 OK
curl http://localhost:8000/react
# Should get inside curl terminal:
# {"message":"react workflow"}
# and inside server terminal / logs:
# INFO:     127.0.0.1:45756 - "GET /react HTTP/1.1" 200 OK
```

I.e.:
uv terminal:
```bash
(ml) [agent-base] ❯ uv run uvicorn ml.main:app --host 0.0.0.0 --port 8000
INFO:     Started server process [87930]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:40054 - "GET /ping HTTP/1.1" 200 OK
INFO:     127.0.0.1:40056 - "GET /health HTTP/1.1" 200 OK
^C # Ctrl+C
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process 
```
curl terminal:
```bash
[agent-base] ❯ curl http://localhost:8000/ping
{"message":"pong"}
[agent-base] ❯ curl http://localhost:8000/health
{"status":"healthy"}
```

## Testing
Run tests:
```bash
uv run pytest
```

## CUDA

Create `.env` file and copy `.env.example` contents into it (adjust model's if needed)

### Linux

Install via your package manager
Fedora 42 driver installation example: 
```bash
sudo dnf upgrade -y
sudo dnf install -y \
  https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda
sudo reboot
```

Linux general docker nvidia-container-toolkit:
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo dnf install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Winwows

1) NVIDIA Driver (Windows)
  - Install latest GeForce/Studio driver from NVIDIA → reboot.

2) Enable WSL2
  - Start → “Turn Windows features on or off”
  - Check: “Virtual Machine Platform” and “Windows Subsystem for Linux” → OK → reboot.

3) Linux distro
  - Microsoft Store → install “Ubuntu” (or your choice) → launch once to finish setup.

4) Docker Desktop
  - Install Docker Desktop.
  - Settings → General → ✔ “Use the WSL 2 based engine”
  - Settings → Resources → WSL Integration → ✔ your distro (e.g., Ubuntu) → Apply & Restart.

### ollama Testing

This command should give non-empty json with created models
```bash
curl -s http://localhost:11434/api/tags
```

## Docker image via Dockerfile

from ml directory
```bash
docker build -t agent-base .
docker run --rm -p 8000:8000 agent-base
```

## Compose service

### Linux
Navigate to compose.yaml and click "run all services"

or CLI way:
- upp'ing service
```bash
docker compose up --build
```
- shutting it down after Ctrl+C or in another terminal:
```bash
docker compose down
```

### Windows
Navigate to compose.windows.yaml and click "run all services"

or CLI way:
- upp'ing service
```bash
docker compose -f compose.windows.yml up --build
```
- shutting it down after Ctrl+C or in another terminal:
```bash
docker compose -f compose.windows.yml down
```

## Project policy's

### English-only including:
- instructions
- comments
- tests
- obviously code and deployment

### We are using uv as package installer, dependency manager and build-tool. Here's how you can add a dependency:
- `uv add PACKAGE_NAME` - Add it
- `uv pip install PACKAGE_NAME` - install for everyday usage
- `uv sync` - Update dependency's and make sure current setup is working

### NO DEVEOPMENT IN MASTER BRANCH GOD BLESS. 
    
here is correct way to develop from a local branch:
1. make sure you are on latest master:
```bash
git fetch origin
git checkout master
git pull --ff-only
```
2. create a new local branch and work there
```bash
git checkout -b feature_name
git add .
git commit -m "Job's done"
```
3. Publish branch (can be done anywhere along step 2)
```bash
git push -u origin HEAD
```
4. When you think it's ready, create a PR via Gihub GUI or CLI:
```bash
gh pr create --base master --fill
```
5. Merge via gh with rebase
```bash
gh pr merge --rebase -d # -d -> deletes branch in case it's HOPEFULLY no longer needs attention
```

6. Pull new master
```bash
git switch master
git pull origin master
```

7. (OPTIONAL) If you didn't delete branch, here's how to continue working on it
```bash
git switch api
git fetch origin # just in case
git reset --hard origin/master # Align with newly setted up master
git push origin HEAD --force-with-lease # update origin feature HEAD
```
or you could just merge with origin master instead, but it adds a commit in git history:
```bash
git switch fature_name
git git merge origin/master -m "syncing with master"
```