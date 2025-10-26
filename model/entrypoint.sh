#!/usr/bin/env bash
set -euo pipefail

MODEL="${OLLAMA_MODEL:-qwen3:0.6b}"
WARM_PROMPT="${OLLAMA_WARM_PROMPT:-Hello from ollama warm-up}"
HEALTH_URL="${OLLAMA_HEALTH_URL:-http://127.0.0.1:11434/api/tags}"
MAX_ATTEMPTS="${OLLAMA_HEALTH_ATTEMPTS:-30}"
SLEEP_SECONDS="${OLLAMA_HEALTH_INTERVAL:-2}"

log() {
  printf '[entrypoint] %s\n' "$*" >&2
}

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

warm_model() {
  log "ensuring model ${MODEL} is available"
  if ! /bin/ollama list | awk '{print $1}' | grep -Fx "${MODEL}" >/dev/null 2>&1; then
    log "pulling model ${MODEL}"
    /bin/ollama pull "${MODEL}"
  else
    log "model ${MODEL} already present"
  fi

  log "warming model ${MODEL}"
  # Run a single-token generation to prime the runtime. Ignore failure but log it.
  if ! /bin/ollama run "${MODEL}" -n 1 -p "${WARM_PROMPT}" >/dev/null 2>&1; then
    log "warning: warm-up run failed (continuing)"
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
  warm_model || log "warning: warm-up sequence failed"
fi

log "handing over to ollama (pid ${OLLAMA_PID})"
wait "${OLLAMA_PID}"
