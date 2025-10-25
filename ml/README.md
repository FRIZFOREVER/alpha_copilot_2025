## Setting up for dev:

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

Sync project
```bash
source .venv/bin/activate
uv sync
```

## Running the API

Make sure you are in project folder and venv is activated

```bash
cd ml
source .venv/bin/activate
uv sync
```

uvicorn canonical launch:

```bash
uv run uvicorn ml.main:app --host 0.0.0.0 --port 8000 u
```

## Project policy's

1. English-only including:
    - instructions
    - comments
    - tests
    - obviously code and deployment
2. NO DEVEOPMENT IN MASTER BRANCH GOD BLESS. 
    - Create your feature-branch i.e. `git checkout -b api`
    - do all `git add .` and `git commit -m "comment"` that you need
    - create PR to REBASE on top of master branch
    - Dm me to review and approve