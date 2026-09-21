from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from telegram_voice_bot.errors import ConfigError

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CHAT_MODEL = "gpt-4o-mini"
DEFAULT_STT_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_TTS_VOICE = "alloy"
DEFAULT_TTS_FORMAT = "opus"
DEFAULT_STT_LANGUAGE = "ar"
DEFAULT_TTS_INSTRUCTIONS = (
    "Speak in a warm, natural Iraqi Arabic conversational tone. "
    "Sound like a friendly person from Baghdad: clear, unhurried, and informal. "
    "Do not sound like you are reading a formal essay."
)
TTS_FORMATS = {"mp3", "opus", "aac", "flac", "wav", "pcm"}
TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str = field(repr=False)
    openai_api_key: str = field(repr=False)
    owner_telegram_id: int
    openai_chat_model: str = DEFAULT_CHAT_MODEL
    openai_max_output_tokens: int = 500
    openai_timeout: float = 60.0
    openai_stt_model: str = DEFAULT_STT_MODEL
    stt_language: str | None = DEFAULT_STT_LANGUAGE
    stt_prompt: str | None = None
    openai_tts_model: str = DEFAULT_TTS_MODEL
    openai_tts_voice: str = DEFAULT_TTS_VOICE
    openai_tts_format: str = DEFAULT_TTS_FORMAT
    tts_instructions: str | None = DEFAULT_TTS_INSTRUCTIONS
    system_prompt: str | None = None
    persona_path: Path = field(default_factory=lambda: REPO_ROOT / "config" / "persona.md")
    database_path: Path = field(default_factory=lambda: REPO_ROOT / "data" / "bot.db")
    allow_groups: bool = False
    always_voice: bool = False
    history_limit: int = 20
    log_level: str = "INFO"


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if environ is None else environ
    missing = [
        name
        for name in ("TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "OWNER_TELEGRAM_ID")
        if not _raw(env, name)
    ]
    if missing:
        lines = "\n".join(f"  - {name}" for name in missing)
        raise ConfigError(
            "Missing required environment variables:\n"
            f"{lines}\n\n"
            "Copy .env.example to .env, fill in the values, and run make run "
            "from the repository root."
        )

    owner_raw = _raw(env, "OWNER_TELEGRAM_ID")
    try:
        owner_id = int(owner_raw)
    except ValueError as exc:
        raise ConfigError("OWNER_TELEGRAM_ID must be an integer Telegram user id.") from exc
    if owner_id <= 0:
        raise ConfigError("OWNER_TELEGRAM_ID must be a positive integer.")

    tts_format = (_raw(env, "OPENAI_TTS_FORMAT") or DEFAULT_TTS_FORMAT).lower()
    if tts_format not in TTS_FORMATS:
        allowed = ", ".join(sorted(TTS_FORMATS))
        raise ConfigError(f"OPENAI_TTS_FORMAT must be one of: {allowed}.")

    log_level = (_raw(env, "LOG_LEVEL") or "INFO").upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ConfigError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL.")

    system_prompt = _optional(env, "SYSTEM_PROMPT", default=None)
    persona_path = _path(env, "PERSONA_PATH", REPO_ROOT / "config" / "persona.md")
    if not system_prompt:
        if not persona_path.is_file():
            raise ConfigError(
                f"Persona file not found: {persona_path}\n"
                "Create it or set SYSTEM_PROMPT in the environment."
            )
        if not persona_path.read_text(encoding="utf-8-sig").strip():
            raise ConfigError(f"Persona file is empty: {persona_path}")

    return Settings(
        telegram_bot_token=_raw(env, "TELEGRAM_BOT_TOKEN"),
        openai_api_key=_raw(env, "OPENAI_API_KEY"),
        owner_telegram_id=owner_id,
        openai_chat_model=_raw(env, "OPENAI_CHAT_MODEL") or DEFAULT_CHAT_MODEL,
        openai_max_output_tokens=_parse_int(
            _raw(env, "OPENAI_MAX_OUTPUT_TOKENS"),
            default=500,
            name="OPENAI_MAX_OUTPUT_TOKENS",
            minimum=1,
            maximum=4096,
        ),
        openai_timeout=_parse_float(
            _raw(env, "OPENAI_TIMEOUT"),
            default=60.0,
            name="OPENAI_TIMEOUT",
        ),
        openai_stt_model=_raw(env, "OPENAI_STT_MODEL") or DEFAULT_STT_MODEL,
        stt_language=_optional(env, "STT_LANGUAGE", default=DEFAULT_STT_LANGUAGE),
        stt_prompt=_optional(env, "STT_PROMPT", default=None),
        openai_tts_model=_raw(env, "OPENAI_TTS_MODEL") or DEFAULT_TTS_MODEL,
        openai_tts_voice=_raw(env, "OPENAI_TTS_VOICE") or DEFAULT_TTS_VOICE,
        openai_tts_format=tts_format,
        tts_instructions=_optional(env, "TTS_INSTRUCTIONS", default=DEFAULT_TTS_INSTRUCTIONS),
        system_prompt=system_prompt,
        persona_path=persona_path,
        database_path=_path(env, "DATABASE_PATH", REPO_ROOT / "data" / "bot.db"),
        allow_groups=_parse_bool(_raw(env, "ALLOW_GROUPS"), default=False, name="ALLOW_GROUPS"),
        always_voice=_parse_bool(_raw(env, "ALWAYS_VOICE"), default=False, name="ALWAYS_VOICE"),
        history_limit=_parse_int(
            _raw(env, "HISTORY_LIMIT"),
            default=20,
            name="HISTORY_LIMIT",
            minimum=1,
            maximum=200,
        ),
        log_level=log_level,
    )


def _raw(env: Mapping[str, str], name: str) -> str:
    return env.get(name, "").strip()


def _optional(env: Mapping[str, str], name: str, default: str | None) -> str | None:
    if name not in env:
        return default
    value = env.get(name, "").strip()
    return value or None


def _path(env: Mapping[str, str], name: str, default: Path) -> Path:
    raw = _raw(env, name)
    path = Path(raw) if raw else default
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _parse_bool(value: str, *, default: bool, name: str) -> bool:
    if not value:
        return default
    lowered = value.lower()
    if lowered in TRUE_VALUES:
        return True
    if lowered in FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be true or false.")


def _parse_int(
    value: str,
    *,
    default: int,
    name: str,
    minimum: int,
    maximum: int | None = None,
) -> int:
    if not value:
        result = default
    else:
        try:
            result = int(value)
        except ValueError as exc:
            raise ConfigError(f"{name} must be an integer.") from exc
    if result < minimum or (maximum is not None and result > maximum):
        if maximum is None:
            raise ConfigError(f"{name} must be at least {minimum}.")
        raise ConfigError(f"{name} must be between {minimum} and {maximum}.")
    return result


def _parse_float(value: str, *, default: float, name: str) -> float:
    if not value:
        result = default
    else:
        try:
            result = float(value)
        except ValueError as exc:
            raise ConfigError(f"{name} must be a number.") from exc
    if result <= 0:
        raise ConfigError(f"{name} must be greater than 0.")
    return result
