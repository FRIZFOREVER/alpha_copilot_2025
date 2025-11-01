## Настройка окружения для разработки

### Установка проекта

Склонируй репозиторий любым удобным способом

Для Windows: убедись, что ты используешь git bash терминал внутри VS Code, а не PowerShell

Обнови pip и установи uv:
```bash
pip install --upgrade pip
pip install uv
```

Создай виртуальное окружение (venv) с помощью uv внутри папки ml:
```bash
cd ml
uv venv
```
### Настройка .gitignore !

Создай файл .gitignore в следующих директориях:
- agent-base/
- agent-base/ml/

Через командную строку::

```bash
( curl -fsSL https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
  echo
  echo ".gitignore"                                                                                   
  echo ".vscode/*"
) > .gitignore
```

### Синхронизация проекта

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

## Настройка VS Code

### Исключение временных файлов

Настройка исключения кэша и временных файлов в VS Code:
Откройте File -> Preferences -> Settings -> Search: exclude
Inside "files: exclude" -> add patterns: 
1. `**/__pycache__` - кэш Python
2. `**/*.pyc` - временные файлы Python
3. `**/.pytest_cache` - кэш pytest
4. (OPTIONAL) `/.venv` - локальное окружение
5. (OPTIONAL) `/.git` - папка Git (можно исключить через другие настройки)

### Настройка среды .venv в VS Code
Чтобы Pylance не ругался, выбери локальное окружение:
ctrl+shift+P -> Python: Select Interpreter -> Enter Interpreter path -> дальше вставьте в зависимости от OS:
- linux    - `agent-base/ml/.venv/bin/activate`
- windows  - `agent-base/ml/.venv/scripts/python.exe`

## Запуск API

Убедись, что ты находишься в папке проекта и виртуальное окружение активировано:

```bash
cd ml
source .venv/bin/activate
uv sync
```

Стандартный запуск сервера Uvicorn:
```bash
uv run uvicorn ml.main:app --host 0.0.0.0 --port 8000
```
Дополнительное логирование:
```bash
uv run uvicorn ml.main:app --host 0.0.0.0 --port 8000 --log-config ./src/ml/configs/logging.yaml --access-log
```
Остановить сервер: Ctrl+C

Проверь работу API из другой консоли (например, через docker compose)::
```bash
curl http://localhost:8000/ping 
# Ожидаемый ответ в curl терминале:
# {"message":"pong"} 
# Ответ внутри серверного териминала / logs: 
# INFO:     127.0.0.1:45744 - "GET /ping HTTP/1.1" 200 OK
curl http://localhost:8000/health 
# Ожидаемый ответ в curl терминале:
# {"status":"healthy"} 
# Ответ внутри серверного териминала / logs:
# INFO:     127.0.0.1:45750 - "GET /health HTTP/1.1" 200 OK
curl http://localhost:8000/react
# Ожидаемый ответ в curl терминале:
# {"message":"react workflow"}
# Ответ внутри серверного териминала / logs:
# INFO:     127.0.0.1:45756 - "GET /react HTTP/1.1" 200 OK
```

Пример:
uv терминал:
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
curl терминал:
```bash
[agent-base] ❯ curl http://localhost:8000/ping
{"message":"pong"}
[agent-base] ❯ curl http://localhost:8000/health
{"status":"healthy"}
```

## Тестирование API
Запуск тестов:
```bash
uv run pytest
```

## CUDA

Отредактируй модели в .env, если нужно.

### Linux

Установка драйверов через менеджер пакетов (пример для Fedora 42):
```bash
sudo dnf upgrade -y
sudo dnf install -y \
  https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda
sudo reboot
```

Docker + NVIDIA Toolkit:
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo dnf install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Winwows

1) NVIDIA драйвер (Windows)
  - Установи последнюю версию GeForce/Studio driver с сайта NVIDIA → перезагрузи компьютер.

2) Включи WSL2
  - Старт → “Turn Windows features on or off”
  - Проверьте: “Virtual Machine Platform” and “Windows Subsystem for Linux” → OK → перезагрузи компьютер.

3) Установка дистрибутива Linux
  - Через Microsoft Store установи Ubuntu (или другой) → запусти один раз для инициализации.

4) Docker Desktop
  - Установи Docker Desktop
  - Settings → General → ✔ “Use the WSL 2 based engine”
  - Settings → Resources → WSL Integration → ✔ выбери свой дистрибутив → Apply & Restart

### Тестирование Ollama

Эта команда должна вернуть непустой JSON с моделями:
```bash
curl -s http://localhost:11434/api/tags
```

## Docker образ через Dockerfile

Из папки ml
```bash
docker build -t agent-base .
docker run --rm -p 8000:8000 agent-base
```

## Compose сервис

### Linux

Перейди к compose.yaml и запусти все сервисы

или через CLI:
- запуск сервера
```bash
docker compose up --build
```
- Остановить после Ctrl+C или из другого терминала:
```bash
docker compose down
```

### Windows
Перейди к compose.windows.yaml и запусти все сервисы

или через CLI:
- запуск сервера
```bash
docker compose -f compose.windows.yml up --build
```
- Остановить после Ctrl+C или из другого терминала:
```bash
docker compose -f compose.windows.yml down
```

## Политика проекта

### English-only including:
- instructions
- comments
- tests
- obviously code and deployment

### Мы используем uv как инструмент для установки пакетов, управления зависимостями и сборки.

Основные команды:
- `uv add PACKAGE_NAME` - добавить
- `uv pip install PACKAGE_NAME` - установить для использования
- `uv sync` - обновить зависимости и убедиться, что всё работает

### Ради бога никаких коммитов в мастер делать не нужно
    
Правильный рабочий процесс из локальной ветки:
1. Обнови master::
```bash
git fetch origin
git checkout master
git pull --ff-only
```
2. Создай новую локальную ветку, внеси изменения и закоммить:
```bash
git checkout -b feature_name
git add .
git commit -m "Job's done"
```
3. Опубликуй ветку: (Можно сделать в любой момент выполнения шага 2)
```bash
git push -u origin HEAD
```
4. Когда всё готово — создай Pull Request через GitHub (GUI или CLI)::
```bash
gh pr create --base master --fill # Свяжись с FRIZ для ревью перед слиянием.
```
5. Слияние с помощью rebase (и удаление ветки):
```bash
gh pr merge --rebase -d # -d -> удаляет ветку
```

6. Обнови master:
```bash
git switch master
git pull origin master
```

7. (Необязательно) Если ветку не удалил и хочешь продолжить:
- Синхронизируйте ветку с master (фактически это то же самое, что создать её заново от origin/master)
```bash
git switch api
git fetch origin # just in case
git reset --hard origin/master # Align with newly setted up master
git push origin HEAD --force-with-lease # update origin feature HEAD
```
- Или вы можете просто сделать merge с origin/master, но это добавит некрасивый коммит в историю Git.:
```bash
git switch fature_name
git git merge origin/master -m "syncing with master"
```