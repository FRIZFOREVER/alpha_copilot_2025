from ml.configs.message import Tag


def get_tag_define_prompt() -> str:
    tags_str: str = ", ".join(tag.value for tag in Tag)
    prompt: str = (
        "You are a helpful assistant, that defines tags\n"
        "Your job is to assign exactly ONE tag\n"
        f"There can be next different tags: {tags_str}\n"
        "There can only be one tag for user's message\n"
        "Here is brief descriptions for every tag and when to assign it:\n"
        f"`{Tag.Finance.value}`: user is asking for any finance advice, "
        "potentially asking to research something in that field.\n"
        f"`{Tag.Law.value}`: user is asking for any law advice, "
        "potentially asking to research something in that field.\n"
        "For legal aspects of Finance also use Law as tag.\n"
        f"`{Tag.Marketing.value}`: user asking for Marketing, Promoting or "
        "Advertisement advice, possible research needed.\n"
        f"`{Tag.Management.value}`: user want to schedule a meeting or "
        "send a message via mail service.\n"
        f"`{Tag.General.value}`: Used for everything else. "
        "This might include file editing or requests defined as 'other'\n"
        f"You must respond with EXACTLY ONE OF: {tags_str} and NOTHING else"
    )
    return prompt
