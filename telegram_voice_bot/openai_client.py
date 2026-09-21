from __future__ import annotations

import logging
from pathlib import Path

from openai import AsyncOpenAI, OpenAIError

from telegram_voice_bot.config import Settings
from telegram_voice_bot.errors import AIError, USER_FACING_AI_ERROR
from telegram_voice_bot.textutil import prepare_speech_text

logger = logging.getLogger(__name__)

MIME_TYPES = {
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".opus": "audio/ogg",
    ".mp3": "audio/mpeg",
    ".mpeg": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".mp4": "audio/mp4",
    ".wav": "audio/wav",
    ".webm": "audio/webm",
    ".flac": "audio/flac",
}


def supports_tts_instructions(model: str) -> bool:
    name = model.lower()
    return "tts" in name and name.startswith("gpt-4o")


def audio_mime(filename: str) -> str:
    return MIME_TYPES.get(Path(filename).suffix.lower(), "application/octet-stream")


class AIClient:
    def __init__(self, settings: Settings, client: AsyncOpenAI | None = None):
        self.settings = settings
        self._client = client or AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout,
        )

    async def transcribe(self, audio: bytes, filename: str) -> str:
        kwargs: dict = {
            "model": self.settings.openai_stt_model,
            "file": (filename, audio, audio_mime(filename)),
        }
        if self.settings.stt_language:
            kwargs["language"] = self.settings.stt_language
        if self.settings.stt_prompt:
            kwargs["prompt"] = self.settings.stt_prompt
        try:
            result = await self._client.audio.transcriptions.create(**kwargs)
        except OpenAIError as exc:
            logger.exception("Speech-to-text failed")
            raise AIError(USER_FACING_AI_ERROR) from exc
        text = result if isinstance(result, str) else getattr(result, "text", "")
        return (text or "").strip()

    async def complete(self, messages: list[dict[str, str]]) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self.settings.openai_chat_model,
                messages=messages,
                max_completion_tokens=self.settings.openai_max_output_tokens,
            )
        except OpenAIError as exc:
            logger.exception("Chat completion failed")
            raise AIError(USER_FACING_AI_ERROR) from exc
        if not response.choices:
            logger.error("Chat completion returned no choices")
            raise AIError(USER_FACING_AI_ERROR)
        content = (response.choices[0].message.content or "").strip()
        if not content:
            logger.error("Chat completion returned empty content")
            raise AIError(USER_FACING_AI_ERROR)
        return content

    async def synthesize(self, text: str) -> tuple[bytes, str]:
        spoken = prepare_speech_text(text)
        if not spoken:
            raise AIError(USER_FACING_AI_ERROR)
        requested = self.settings.openai_tts_format
        try:
            return await self._synthesize(spoken, requested), requested
        except OpenAIError as exc:
            status = getattr(exc, "status_code", None)
            if status in {401, 403} or requested == "mp3":
                logger.exception("Text-to-speech failed")
                raise AIError(USER_FACING_AI_ERROR) from exc
            logger.warning("Text-to-speech format %s failed; retrying mp3", requested)
            try:
                return await self._synthesize(spoken, "mp3"), "mp3"
            except OpenAIError as retry_exc:
                logger.exception("Text-to-speech mp3 fallback failed")
                raise AIError(USER_FACING_AI_ERROR) from retry_exc

    async def _synthesize(self, text: str, audio_format: str) -> bytes:
        kwargs: dict = {
            "model": self.settings.openai_tts_model,
            "voice": self.settings.openai_tts_voice,
            "input": text,
            "response_format": audio_format,
        }
        if self.settings.tts_instructions and supports_tts_instructions(self.settings.openai_tts_model):
            kwargs["instructions"] = self.settings.tts_instructions
        response = await self._client.audio.speech.create(**kwargs)
        data = await response.aread()
        if not data:
            raise AIError(USER_FACING_AI_ERROR)
        return data
