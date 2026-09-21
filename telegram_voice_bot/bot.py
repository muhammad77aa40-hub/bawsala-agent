from __future__ import annotations

import argparse
import logging
import sys
from typing import Mapping

from dotenv import load_dotenv
from telegram import BotCommand, Update
from telegram.ext import Application

from telegram_voice_bot.config import REPO_ROOT, Settings, load_settings
from telegram_voice_bot.errors import ConfigError
from telegram_voice_bot.handlers import register_handlers
from telegram_voice_bot.openai_client import AIClient
from telegram_voice_bot.prompts import resolve_persona
from telegram_voice_bot.service import ConversationService
from telegram_voice_bot.state import State

logger = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def build_application(settings: Settings) -> Application:
    state = State(settings.database_path)
    service = ConversationService(settings, state, AIClient(settings))
    prompt, source = service.active_persona()
    logger.info("Persona source: %s (%s characters)", source, len(prompt))
    logger.info(
        "Voice-note bot ready. owner=%s chat=%s stt=%s tts=%s voice=%s format=%s "
        "groups=%s always_voice=%s",
        settings.owner_telegram_id,
        settings.openai_chat_model,
        settings.openai_stt_model,
        settings.openai_tts_model,
        settings.openai_tts_voice,
        settings.openai_tts_format,
        settings.allow_groups,
        settings.always_voice,
    )
    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(_post_init)
        .build()
    )
    application.bot_data["settings"] = settings
    application.bot_data["service"] = service
    register_handlers(application)
    return application


def run_bot(settings: Settings) -> None:
    application = build_application(settings)
    application.run_polling(
        allowed_updates=[Update.MESSAGE],
        drop_pending_updates=True,
    )


def run_check(settings: Settings) -> int:
    try:
        state = State(settings.database_path)
        prompt, source = resolve_persona(settings, state.get_persona_override())
    except (ConfigError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Configuration OK")
    print(f"Owner Telegram id: {settings.owner_telegram_id}")
    print(f"Persona source: {source} ({len(prompt)} characters)")
    print(f"Database: {settings.database_path}")
    print(f"Chat model: {settings.openai_chat_model}")
    print(f"Speech-to-text: {settings.openai_stt_model}")
    print(
        "Text-to-speech: "
        f"{settings.openai_tts_model} voice={settings.openai_tts_voice} "
        f"format={settings.openai_tts_format}"
    )
    print(f"Private chats only: {not settings.allow_groups}")
    print(f"Always send voice for text messages: {settings.always_voice}")
    return 0


def main(
    argv: list[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    load_env_file: bool = True,
) -> int:
    parser = argparse.ArgumentParser(
        prog="telegram_voice_bot",
        description="Telegram AI bot for voice notes and text messages. Live calls are not supported.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate configuration, persona, and the local database, then exit",
    )
    args = parser.parse_args(argv)
    if load_env_file:
        load_dotenv(REPO_ROOT / ".env")
    try:
        settings = load_settings(environ)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    configure_logging(settings.log_level)
    if args.check:
        return run_check(settings)
    run_bot(settings)
    return 0


async def _post_init(application: Application) -> None:
    try:
        await application.bot.set_my_commands(
            [
                BotCommand("start", "بداية"),
                BotCommand("help", "المساعدة"),
                BotCommand("whoami", "عرض معرفك"),
                BotCommand("reset", "مسح المحادثة"),
                BotCommand("task", "المهمة الثابتة"),
                BotCommand("persona", "تغيير الشخصية"),
            ]
        )
    except Exception:
        logger.exception("Could not register bot commands")
