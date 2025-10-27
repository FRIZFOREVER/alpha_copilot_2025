#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[entrypoint] %s\n' "$*" >&2
}

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "${SCRIPT_PATH}")"

REASONING_MODEL="${OLLAMA_REASONING_MODEL:-}"
if [ -z "${REASONING_MODEL}" ]; then
  log "error: OLLAMA_REASONING_MODEL must be provided in the environment"
  exit 1
fi

RERANK_MODEL="${OLLAMA_RERANK_MODEL:-}"
if [ -z "${RERANK_MODEL}" ]; then
  log "error: OLLAMA_RERANK_MODEL must be provided in the environment"
  exit 1
fi

EMBEDDING_MODEL="${OLLAMA_EMBEDDING_MODEL:-}"
if [ -z "${EMBEDDING_MODEL}" ]; then
  log "error: OLLAMA_EMBEDDING_MODEL must be provided in the environment"
  exit 1
fi
HEALTH_URL="${OLLAMA_HEALTH_URL:-http://127.0.0.1:11434/api/tags}"
MAX_ATTEMPTS="${OLLAMA_HEALTH_ATTEMPTS:-30}"
SLEEP_SECONDS="${OLLAMA_HEALTH_INTERVAL:-2}"

start_ollama() {
  log "starting ollama: /bin/ollama $*"
  /bin/ollama "$@" &
  OLLAMA_PID=$!
  log "ollama pid: ${OLLAMA_PID}"
}

stop_ollama() {
  local signal=${1:-TERM}
  if kill -0 "${OLLAMA_PID}" 2>/dev/null; then
    log "forwarding ${signal} to ollama (pid ${OLLAMA_PID})"
    kill "-${signal}" "${OLLAMA_PID}" 2>/dev/null || true
  fi
}

await_health() {
  log "waiting for ollama health at ${HEALTH_URL}"
  local attempt=1
  until curl --fail --silent --show-error "${HEALTH_URL}" >/dev/null; do
    if (( attempt >= MAX_ATTEMPTS )); then
      log "ollama failed health check after ${MAX_ATTEMPTS} attempts"
      return 1
    fi
    attempt=$(( attempt + 1 ))
    sleep "${SLEEP_SECONDS}"
  done
  log "ollama is healthy"
}

ensure_model_present() {
  local model=$1
  log "ensuring model ${model} is available"
  if ! /bin/ollama list | awk '{print $1}' | grep -Fx "${model}" >/dev/null 2>&1; then
    log "pulling model ${model}"
    /bin/ollama pull "${model}"
  else
    log "model ${model} already present"
  fi
}

cleanup() {
  local exit_code=$?
  stop_ollama TERM
  wait "${OLLAMA_PID}" 2>/dev/null || true
  exit "${exit_code}"
}

trap 'stop_ollama TERM' TERM INT
trap 'stop_ollama HUP' HUP
trap cleanup EXIT

start_ollama "$@"

if await_health; then
  ensure_model_present "${REASONING_MODEL}"
  ensure_model_present "${RERANK_MODEL}"
  ensure_model_present "${EMBEDDING_MODEL}"
fi

log "handing over to ollama (pid ${OLLAMA_PID})"
wait "${OLLAMA_PID}"
