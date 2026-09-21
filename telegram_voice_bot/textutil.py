from __future__ import annotations

import re

SPEECH_CHAR_LIMIT = 4000
TELEGRAM_TEXT_LIMIT = 4096
CAPTION_LIMIT = 1024
CLEAR_WORDS = {"clear", "reset", "default", "مسح", "حذف"}


def command_body(text: str | None) -> str:
    """Return the text after a Telegram /command token, keeping later newlines."""
    if not text:
        return ""
    stripped = text.strip()
    parts = stripped.split(maxsplit=1)
    if not parts:
        return ""
    if parts[0].startswith("/") and len(parts[0]) > 1:
        return parts[1].strip() if len(parts) > 1 else ""
    return stripped


def is_clear_command(body: str) -> bool:
    return body.casefold() in CLEAR_WORDS


def combine_transcript(transcript: str, caption: str | None) -> str:
    spoken = transcript.strip()
    note = (caption or "").strip()
    if spoken and note:
        return f"{spoken}\n{note}"
    return spoken or note


def prepare_speech_text(text: str, limit: int = SPEECH_CHAR_LIMIT) -> str:
    cleaned = text.replace("**", "").replace("__", "").replace("`", "")
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if len(cleaned) <= limit:
        return cleaned
    cut = cleaned[:limit]
    for separator in ("\n", ".", "،", "؟", "!", " "):
        index = cut.rfind(separator)
        if index > int(limit * 0.6):
            return cut[:index].strip()
    return cut.strip()


def split_text(text: str, limit: int = TELEGRAM_TEXT_LIMIT) -> list[str]:
    remaining = text.strip()
    if not remaining:
        return []
    if len(remaining) <= limit:
        return [remaining]
    chunks: list[str] = []
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = remaining.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        piece = remaining[:cut].strip()
        if piece:
            chunks.append(piece)
        remaining = remaining[cut:].strip()
    return chunks


def clip(text: str, limit: int = 3500) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n…"
