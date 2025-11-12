# ML Service Notes

## Pipeline instrumentation

Pipeline execution no longer relies on a dedicated logger. Instead, nodes
append structured dictionaries to `GraphState.event_log` via the
`GraphState.record_event` helper. Inspect the `event_log` field on the final
state returned by LangGraph to review routing decisions, tool invocations, and
prompt construction without scraping log output.
