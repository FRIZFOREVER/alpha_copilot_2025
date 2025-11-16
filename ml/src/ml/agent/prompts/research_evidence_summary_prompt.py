"""Prompt helper for summarizing research evidence snippets."""

from collections.abc import Sequence

from ml.agent.prompts.system_prompt import get_system_prompt
from ml.configs.message import ChatHistory, UserProfile


def _format_evidence(evidence_snippets: Sequence[str]) -> str:
    lines: list[str] = []
    for index, snippet in enumerate(evidence_snippets, start=1):
        lines.append(f"[{index}] {snippet}")
    return "\n".join(lines)


def get_research_evidence_summary_prompt(
    *, profile: UserProfile, evidence_snippets: Sequence[str]
) -> ChatHistory:
    """Compose a summarization prompt for condensing gathered evidence."""

    prompt = ChatHistory()
    persona = get_system_prompt(profile)
    system_sections: list[str] = [persona]
    system_sections.append(
        "Ты аналитик, который готовит короткий отчёт по найденным источникам."
        " Сохраняй номера источников в квадратных скобках и перечисляй главные факты без"
        " повторов. Результат использует другой агент как основу финального ответа."
        " Не добавляй новых фактов."
    )
    prompt.add_or_change_system("\n\n".join(system_sections))

    if evidence_snippets:
        formatted_evidence = _format_evidence(evidence_snippets)
        prompt.add_user(
            "Сожми выдержки в единый связный отчёт и выдели ключевые выводы,"
            " используя ссылки вида [1], [2] и так далее.\n\n" + formatted_evidence,
        )
    else:
        prompt.add_user(
            "Источники не переданы. Ответь одной фразой, что нет данных для отчёта."
        )

    return prompt
