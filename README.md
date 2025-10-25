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
uv run uvicorn ml.main:app --host 0.0.0.0 --port 8000
```
Ctrl+C to stop server

Test via making calls from another terminal:
```bash
curl http://localhost:8000/ping # Should get {"message":"pong"} and INFO: 127.0.0.1:37270 - "GET /ping HTTP/1.1" 200 OK
curl http://localhost:8000/health # Should get {"status":"healthy"} and INFO: 127.0.0.1:37272 - "GET /health HTTP/1.1" 200 OK
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
^CINFO:     Shutting down
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


## Project policy's

1. English-only including:
    - instructions
    - comments
    - tests
    - obviously code and deployment
2. NO DEVEOPMENT IN MASTER BRANCH GOD BLESS. 
    
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

    5. Rebase on top of origin master:
    ```bash
    git rebase origin/master
    ```

    6. Push after rebase
    ```bash
    git push --force-with-lease
    ```

    7. Merge
    ```bash
    git pr merge --rebase
    ```