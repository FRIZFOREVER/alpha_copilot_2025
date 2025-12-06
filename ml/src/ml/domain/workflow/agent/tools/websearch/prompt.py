from ml.domain.models import ChatHistory
from ml.domain.models.chat_history import Message, Role


def get_relevance_prompt(*, query: str, chunk: str) -> ChatHistory:
    system_message = (
        "You check whether a text chunk contains information that helps answer the search "
        "query. Return JSON with one boolean field is_chunk_relevant that is true only if "
        "the chunk is likely useful for the query."
    )

    prompt = ChatHistory(
        messages=[
            Message(role=Role.system, content=system_message),
            Message(role=Role.user, content=f"Search query: {query}"),
            Message(role=Role.assistant, content="Got it, now provide the chunk."),
            Message(role=Role.user, content=chunk),
        ]
    )

    return prompt
