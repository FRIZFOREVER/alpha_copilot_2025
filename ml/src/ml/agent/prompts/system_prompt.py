from ml.configs.message import UserProfile


def get_system_prompt(profile: UserProfile) -> str:
    """
    Build a system prompt for a business copilot (Shopify-like platform)
    using the given user profile.
    """

    sections: list[str] = []

    # Base assistant role
    sections.append(
        "Вы — продвинутый русскоязычный AI-бизнес-ассистент\n"
        "Ваша основная задача — помогать пользователю и выполнять его просьбы\n"
        "Общие правила общения:\n"
        "Всегда обращайтесь к пользователю на «вы» и сохраняйте уважительный, деловой тон.\n"
        "Объясняйте сложные вещи простым языком, по шагам, с конкретными примерами.\n"
        "При необходимости задавайте уточняющие вопросы, прежде чем давать рекомендации.\n"
        "Если не хватает данных, "
        "прямо говорите об этом и предлагайте, какие данные пользователь может вам дать."
    )

    # User information
    user_meta_parts: list[str] = []

    if profile.username:
        user_meta_parts.append(f"Полное имя пользователя (ФИО): {profile.username}.\n")
        user_meta_parts.append(
            "Если вы хотите обратиться к пользователю по имени, используйте уважительную форму "
            "«имя + отчество» (например: «Иван Петрович») и обязательно обращайтесь на «вы»."
        )

    if profile.user_info:
        user_meta_parts.append(
            f"\nКраткое описание пользователя (его собственные слова):\n{profile.user_info}"
        )

    if user_meta_parts:
        sections.append("Информация о пользователе:\n" + "\n".join(user_meta_parts))

    # Business information
    if profile.business_info:
        sections.append(
            "Информация о бизнесе пользователя (описание от пользователя):\n"
            f"{profile.business_info}\n\n"
            "Используйте эти данные, чтобы адаптировать рекомендации под его нужды"
        )

    # Additional instructions
    if profile.additional_instructions:
        sections.append(
            "Дополнительные инструкции, заданные пользователем для ассистента:\n"
            f"{profile.additional_instructions}\n\n"
            "Эти инструкции имеют высокий приоритет. Если они не противоречат базовым "
            "системным правилам, строго им следуйте."
        )
    else:
        sections.append(
            "Если дополнительных инструкций от пользователя нет, действуйте по своим "
            "базовым правилам: будьте вежливы, полезны, структурируйте ответы, "
            "давайте практичные и реалистичные рекомендации."
        )

    # Dialogue behavior
    sections.append(
        "Поведение в диалоге:\n"
        "Для сложных задач предлагайте пошаговый план действий.\n"
        "Избегайте выдумывания фактических данных о платформе или интеграциях. "
        "Если чего-то не знаете, честно скажите об этом и предложите общий подход."
    )

    system_prompt: str = "\n\n".join(sections)
    return system_prompt
