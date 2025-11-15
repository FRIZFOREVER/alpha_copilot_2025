from ml.configs.message import ChatHistory


def get_fast_answer_prompt(chat: ChatHistory) -> ChatHistory:
    # TODO: include evidance list found in state to system prompt
    return chat
