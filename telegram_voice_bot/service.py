from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from telegram_voice_bot.config import Settings
from telegram_voice_bot.errors import AIError, EmptyTranscriptError
from telegram_voice_bot.prompts import build_messages, build_system_prompt, resolve_persona
from telegram_voice_bot.state import State
from telegram_voice_bot.textutil import combine_transcript

logger = logging.getLogger(__name__)


class LanguageModel(Protocol):
    async def complete(self, messages: list[dict[str, str]]) -> str: ...

    async def transcribe(self, audio: bytes, filename: str) -> str: ...

    async def synthesize(self, text: str) -> tuple[bytes, str]: ...


@dataclass(frozen=True)
class TurnResult:
    user_text: str
    reply_text: str
    audio: bytes | None = None
    audio_format: str | None = None


class ConversationService:
    def __init__(self, settings: Settings, state: State, ai: LanguageModel):
        self.settings = settings
        self.state = state
        self.ai = ai

    def active_persona(self) -> tuple[str, str]:
        return resolve_persona(self.settings, self.state.get_persona_override())

    async def reply_to_text(self, chat_id: int, text: str, *, with_voice: bool) -> TurnResult:
        user_text = text.strip()
        if not user_text:
            raise ValueError("empty text")
        persona, _source = self.active_persona()
        system = build_system_prompt(
            persona,
            self.state.get_standing_task(),
            for_speech=with_voice,
        )
        history = self.state.recent_messages(chat_id, self.settings.history_limit)
        reply = await self.ai.complete(build_messages(system, history, user_text))
        self.state.add_message(chat_id, "user", user_text)
        self.state.add_message(chat_id, "assistant", reply)
        audio: bytes | None = None
        audio_format: str | None = None
        if with_voice:
            try:
                audio, audio_format = await self.ai.synthesize(reply)
            except AIError:
                logger.exception("Text-to-speech failed; text reply is still available")
        return TurnResult(
            user_text=user_text,
            reply_text=reply,
            audio=audio,
            audio_format=audio_format,
        )

    async def reply_to_voice(
        self,
        chat_id: int,
        audio: bytes,
        filename: str,
        caption: str | None = None,
    ) -> TurnResult:
        transcript = (await self.ai.transcribe(audio, filename)).strip()
        combined = combine_transcript(transcript, caption)
        if not combined:
            raise EmptyTranscriptError("ما سمعت كلام واضح بالمقطع. أعد التسجيل لو سمحت.")
        logger.info("Transcribed voice chat=%s chars=%s", chat_id, len(combined))
        logger.debug("Transcript chat=%s text=%s", chat_id, combined)
        return await self.reply_to_text(chat_id, combined, with_voice=True)
