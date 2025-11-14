"""Построитель подсказки для этапа рассуждений исследовательского агента."""

from typing import Optional, Sequence

from ml.agent.graph.state import ResearchTurn
from ml.configs.message import ChatHistory, Role


def _format_turn_history(turn_history: Sequence[ResearchTurn]) -> str:
    lines: list[str] = []
    for index, turn in enumerate(turn_history, start=1):

        lines.append(
            f"Ход {index} — рассуждение: {turn.reasoning_summary}"
        )

        request = turn.request
        lines.append(
            f"Ход {index} — запрос к инструменту: {request.tool_name} -> {request.input_text}"
        )

        observation = turn.observation
        lines.append(
            f"Ход {index} — наблюдение: {observation.content}"
        )
    return "\n".join(lines)


def get_research_reason_prompt(
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    latest_reasoning: Optional[str] = None,
) -> ChatHistory:
    """Создать подсказку для рассуждений с учётом предыдущих ходов и черновика."""

    prompt = ChatHistory()
    prompt.add_or_change_system(
        (
            "Вы — эксперт по исследовательским стратегиям, координирующий многошаговое расследование.\n"
            "Изучите диалог, обратитесь к завершённым исследовательским шагам и определите следующий этап рассуждений.\n"
            "Поясните ход мыслей и укажите, какой предыдущий ход повлиял на каждое решение."
        )
    )

    conversation_block = conversation.model_dump_string()
    history_block = _format_turn_history(turn_history)

    user_sections: list[str] = []
    if conversation_block:
        user_sections.append("Контекст беседы:\n" + conversation_block)
    else:
        user_sections.append("Контекст беседы:\nПредыдущий диалог отсутствует.")

    if history_block:
        user_sections.append("Завершённые исследовательские ходы:\n" + history_block)
    else:
        user_sections.append("Завершённые исследовательские ходы:\nНет. Это будет первый этап рассуждений.")

    if latest_reasoning:
        user_sections.append("Последние заметки из черновика:\n" + latest_reasoning)

    user_sections.append(
        (
            "Сформулируйте следующую сводку рассуждений.\n"
            "Сосредоточьтесь на ключевом вопросе, сослитесь на полезные прошлые данные и предложите, стоит ли вызвать инструмент или перейти к синтезу выводов."
        )
    )

    prompt.add_user("\n\n".join(user_sections))
    return prompt
