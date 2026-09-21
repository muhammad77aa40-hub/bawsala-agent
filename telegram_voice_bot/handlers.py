from __future__ import annotations

import logging
from io import BytesIO

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from telegram_voice_bot.access import chat_is_allowed, owner_command_access
from telegram_voice_bot.config import Settings
from telegram_voice_bot.errors import AIError, ConfigError, EmptyTranscriptError
from telegram_voice_bot.service import ConversationService, TurnResult
from telegram_voice_bot.textutil import (
    CAPTION_LIMIT,
    clip,
    command_body,
    is_clear_command,
    split_text,
)

logger = logging.getLogger(__name__)

MAX_AUDIO_BYTES = 20 * 1024 * 1024
OWNER_ONLY = "هذا الأمر لصاحب البوت فقط."
VOICE_DOWNLOAD_ERROR = "صار خطأ وأنا أعالج الرسالة الصوتية. جرب مرة ثانية."

HELP_TEXT = """دز رسالة صوتية: أفرغها وأرد عليك برسالة صوتية.
دز نص: أرد عليك بنص.

الأوامر:
/start بداية
/help هذي المساعدة
/whoami يعرض معرفك على تلفرام
/reset يمسح سجل هالمحادثة من ذاكرة البوت"""

OWNER_HELP = """
أوامر صاحب البوت، بالخاص فقط:
/persona يعرض الشخصية الحالية
/persona وبعدها النص يحفظ شخصية جديدة
/persona reset يرجع الشخصية من الملف أو SYSTEM_PROMPT
/task يعرض المهمة الثابتة
/task وبعدها النص يحفظ مهمة يلتزم بيها البوت
/task reset يمسح المهمة"""


def register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("whoami", whoami))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("persona", persona))
    application.add_handler(CommandHandler("task", task))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, on_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_error_handler(on_error)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update, context):
        return
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(
        "هلا.\n"
        "أني مساعد صوتي. دزلي رسالة صوتية وأرد عليك بصوت، أو اكتب وأرد عليك بنص.\n\n"
        "هالبوت يشتغل على الرسائل الصوتية (فويس نوت)، مو على مكالمات تلفرام المباشرة.\n\n"
        "اكتب /help حتى تشوف الأوامر."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update, context):
        return
    message = update.effective_message
    user = update.effective_user
    if message is None:
        return
    settings = _settings(context)
    text = HELP_TEXT
    if user is not None and user.id == settings.owner_telegram_id:
        text += OWNER_HELP
    await message.reply_text(text)


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update, context):
        return
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return
    settings = _settings(context)
    if user.id == settings.owner_telegram_id:
        await message.reply_text(f"معرفك على تلفرام: {user.id}\nهذا الحساب هو صاحب البوت.")
        return
    await message.reply_text(f"معرفك على تلفرام: {user.id}")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update, context):
        return
    message = update.effective_message
    if message is None:
        return
    _service(context).state.clear_history(message.chat_id)
    await message.reply_text("مسحت سجل هالمحادثة من عندي. نقدر نبدي من جديد.")


async def persona(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _owner_only(update, context):
        return
    message = update.effective_message
    if message is None:
        return
    service = _service(context)
    body = command_body(message.text)
    if is_clear_command(body):
        service.state.clear_persona_override()
        try:
            _prompt, source = service.active_persona()
        except ConfigError as exc:
            await message.reply_text(str(exc))
            return
        await message.reply_text(f"رجعت الشخصية الافتراضية.\nالمصدر: {source}")
        return
    if not body:
        try:
            prompt, source = service.active_persona()
        except ConfigError as exc:
            await message.reply_text(str(exc))
            return
        await message.reply_text(f"المصدر: {source}\n\n{clip(prompt)}")
        return
    service.state.set_persona_override(body)
    logger.info("Owner updated persona chars=%s", len(body))
    await message.reply_text("تم تحديث الشخصية. راح أستخدم هذا الوصف بدل الملف والإعداد.")


async def task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _owner_only(update, context):
        return
    message = update.effective_message
    if message is None:
        return
    state = _service(context).state
    body = command_body(message.text)
    if not body:
        current = state.get_standing_task()
        if not current:
            await message.reply_text("ماكو مهمة ثابتة هسه.\nمثال: /task جاوب باختصار وساعد المستخدم يرتب أفكاره")
            return
        await message.reply_text(f"المهمة الثابتة:\n{clip(current)}")
        return
    if is_clear_command(body):
        state.clear_standing_task()
        logger.info("Owner cleared standing task")
        await message.reply_text("مسحت المهمة الثابتة.")
        return
    state.set_standing_task(body)
    logger.info("Owner updated standing task chars=%s", len(body))
    await message.reply_text("تم حفظ المهمة الثابتة. راح ألتزم بيها بالمحادثات.")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update, context):
        return
    message = update.effective_message
    if message is None:
        return
    await message.reply_text("ما أعرف هذا الأمر. اكتب /help")


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update, context):
        return
    message = update.effective_message
    if message is None or not message.text or not message.text.strip():
        return
    settings = _settings(context)
    await message.reply_chat_action(ChatAction.TYPING)
    try:
        result = await _service(context).reply_to_text(
            message.chat_id,
            message.text,
            with_voice=settings.always_voice,
        )
    except ConfigError as exc:
        logger.warning("Persona is not available: %s", exc)
        await message.reply_text(str(exc))
        return
    except AIError as exc:
        await message.reply_text(str(exc))
        return
    await deliver_reply(message, result, voice_primary=False)


async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update, context):
        return
    message = update.effective_message
    if message is None:
        return
    media = message.voice or message.audio
    if media is None:
        return
    if media.file_size and media.file_size > MAX_AUDIO_BYTES:
        await message.reply_text("الملف الصوتي كبير. دز مقطع أقصر.")
        return
    await message.reply_chat_action(ChatAction.RECORD_VOICE)
    filename = _audio_filename(media)
    try:
        tg_file = await context.bot.get_file(media.file_id)
        payload = bytes(await tg_file.download_as_bytearray())
    except Exception:
        logger.exception("Failed to download Telegram audio")
        await message.reply_text(VOICE_DOWNLOAD_ERROR)
        return
    if not payload:
        await message.reply_text("ما وصلتني الرسالة الصوتية. أعد الإرسال.")
        return
    try:
        result = await _service(context).reply_to_voice(
            message.chat_id,
            payload,
            filename,
            caption=message.caption,
        )
    except ConfigError as exc:
        logger.warning("Persona is not available: %s", exc)
        await message.reply_text(str(exc))
        return
    except EmptyTranscriptError as exc:
        await message.reply_text(str(exc))
        return
    except AIError as exc:
        await message.reply_text(str(exc))
        return
    except Exception:
        logger.exception("Voice turn failed")
        await message.reply_text(VOICE_DOWNLOAD_ERROR)
        return
    await deliver_reply(message, result, voice_primary=True)


async def deliver_reply(message, result: TurnResult, *, voice_primary: bool) -> None:
    if voice_primary and result.audio and result.audio_format:
        try:
            await _send_audio(
                message,
                result.audio,
                result.audio_format,
                caption=_caption(result.reply_text),
            )
        except Exception:
            logger.exception("Failed to send voice reply; sending text")
            await _reply_text_chunks(message, result.reply_text)
            return
        if len(result.reply_text) > CAPTION_LIMIT:
            await _reply_text_chunks(message, result.reply_text)
        return

    await _reply_text_chunks(message, result.reply_text)
    if result.audio and result.audio_format:
        try:
            await _send_audio(message, result.audio, result.audio_format, caption=None)
        except Exception:
            logger.exception("Failed to send optional voice reply")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error: %s", context.error)


def _settings(context: ContextTypes.DEFAULT_TYPE) -> Settings:
    return context.bot_data["settings"]


def _service(context: ContextTypes.DEFAULT_TYPE) -> ConversationService:
    return context.bot_data["service"]


def _allowed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    if chat is None:
        return False
    settings = _settings(context)
    if chat_is_allowed(chat.type, settings.allow_groups):
        return True
    logger.debug("Ignoring chat %s type %s", chat.id, chat.type)
    return False


async def _owner_only(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    if chat is None or message is None:
        return False
    settings = _settings(context)
    access = owner_command_access(
        chat.type,
        user.id if user is not None else None,
        settings.owner_telegram_id,
        settings.allow_groups,
    )
    if access == "allow":
        return True
    if access == "deny":
        await message.reply_text(OWNER_ONLY)
    return False


def _audio_filename(media) -> str:
    name = getattr(media, "file_name", None)
    if name:
        return str(name)
    mime = (getattr(media, "mime_type", None) or "").lower()
    if "mpeg" in mime or "mp3" in mime:
        return "note.mp3"
    if "mp4" in mime or "m4a" in mime:
        return "note.m4a"
    if "wav" in mime:
        return "note.wav"
    return "note.ogg"


def _caption(text: str) -> str | None:
    cleaned = text.strip()
    if not cleaned or len(cleaned) > CAPTION_LIMIT:
        return None
    return cleaned


async def _send_audio(message, audio: bytes, audio_format: str, caption: str | None) -> None:
    payload = BytesIO(audio)
    if audio_format == "opus":
        payload.name = "reply.ogg"
        await message.reply_voice(voice=payload, caption=caption, filename="reply.ogg")
        return
    extension = "mp3" if audio_format == "mp3" else audio_format
    payload.name = f"reply.{extension}"
    await message.reply_audio(audio=payload, caption=caption, filename=payload.name)


async def _reply_text_chunks(message, text: str) -> None:
    chunks = split_text(text)
    if not chunks:
        return
    for chunk in chunks:
        await message.reply_text(chunk)
