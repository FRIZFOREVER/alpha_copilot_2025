def _rstrip_slash(url: str) -> str:
    """Small hygiene: OpenAI client prefers base_url without trailing slash."""
    return url[:-1] if url.endswith("/") else url