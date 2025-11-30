from typing import Final

from ollama import ProgressResponse


def format_bytes(bytes_value: int | None) -> str:
    """Format a byte count into a human-readable string."""
    _UNITS: Final[tuple[str, ...]] = ("B", "KB", "MB", "GB", "TB", "PB")

    if bytes_value is None:
        return "unknown"

    size = float(bytes_value)

    for idx, unit in enumerate(_UNITS):
        is_last_unit = idx == len(_UNITS) - 1
        if size < 1024 or is_last_unit:
            return f"{size:5.1f}{unit}"
        size /= 1024

    # NOTE: Fallback: logically unreachable, but keeps Pyright happy.
    return "unknown"


def format_progress(progress: ProgressResponse, length: int = 20) -> str:
    """Build a single-line human-readable status with a progress bar if possible."""
    status = progress.status or "pulling"
    completed = progress.completed
    total = progress.total

    # If we don't know total, fall back to a simpler format.
    if completed is None or not total:
        if completed is not None:
            return f"{status} {format_bytes(completed)}"
        return status

    # Clamp ratio to [0, 1] and build bar inline (no extra helper).
    ratio = max(0.0, min(1.0, completed / total))
    filled = int(round(ratio * length))
    empty = length - filled
    bar = f"[{'█' * filled}{'-' * empty}]"
    percent = f"{ratio * 100:5.1f}%"

    return f"{status} {bar} {percent} {format_bytes(completed)}/{format_bytes(total)}"
