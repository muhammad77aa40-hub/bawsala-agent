import tempfile
import unittest
from pathlib import Path

from telegram_voice_bot.config import load_settings
from telegram_voice_bot.errors import AIError, EmptyTranscriptError
from telegram_voice_bot.prompts import SPEECH_HINT
from telegram_voice_bot.service import ConversationService
from telegram_voice_bot.state import State


class FakeAI:
    def __init__(self, reply: str = "هلا بيك", transcript: str = "شلونك") -> None:
        self.reply = reply
        self.transcript = transcript
        self.calls: list[tuple] = []

    async def transcribe(self, audio: bytes, filename: str) -> str:
        self.calls.append(("transcribe", audio, filename))
        return self.transcript

    async def complete(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(("complete", messages))
        return self.reply

    async def synthesize(self, text: str) -> tuple[bytes, str]:
        self.calls.append(("synthesize", text))
        return b"OggS-fake", "opus"


class FailingSpeech(FakeAI):
    async def synthesize(self, text: str) -> tuple[bytes, str]:
        self.calls.append(("synthesize", text))
        raise AIError("tts down")


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = load_settings(
            {
                "TELEGRAM_BOT_TOKEN": "token",
                "OPENAI_API_KEY": "key",
                "OWNER_TELEGRAM_ID": "5",
                "SYSTEM_PROMPT": "شخصية الاختبار",
                "DATABASE_PATH": str(Path(self.tmp.name) / "bot.db"),
                "HISTORY_LIMIT": "4",
            }
        )
        self.state = State(self.settings.database_path)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    async def test_voice_note_is_transcribed_answered_and_spoken(self) -> None:
        ai = FakeAI()
        service = ConversationService(self.settings, self.state, ai)
        self.state.set_standing_task("جاوب باختصار")
        result = await service.reply_to_voice(7, b"audio-bytes", "note.ogg", caption="اليوم")
        self.assertEqual(result.user_text, "شلونك\nاليوم")
        self.assertEqual(result.reply_text, "هلا بيك")
        self.assertEqual(result.audio, b"OggS-fake")
        self.assertEqual(result.audio_format, "opus")
        self.assertEqual([call[0] for call in ai.calls], ["transcribe", "complete", "synthesize"])
        system = ai.calls[1][1][0]["content"]
        self.assertIn("شخصية الاختبار", system)
        self.assertIn("جاوب باختصار", system)
        self.assertIn(SPEECH_HINT, system)
        self.assertEqual(
            self.state.recent_messages(7, 10),
            [
                {"role": "user", "content": "شلونك\nاليوم"},
                {"role": "assistant", "content": "هلا بيك"},
            ],
        )

    async def test_text_stays_text_unless_voice_is_requested(self) -> None:
        ai = FakeAI(reply="جواب نصي")
        service = ConversationService(self.settings, self.state, ai)
        quiet = await service.reply_to_text(7, "مرحبا", with_voice=False)
        self.assertIsNone(quiet.audio)
        self.assertNotIn(SPEECH_HINT, ai.calls[0][1][0]["content"])
        spoken = await service.reply_to_text(7, "رد بصوت", with_voice=True)
        self.assertEqual(spoken.audio_format, "opus")
        self.assertEqual([call[0] for call in ai.calls], ["complete", "complete", "synthesize"])
        history = ai.calls[1][1]
        self.assertEqual(history[1]["content"], "مرحبا")
        self.assertEqual(history[2]["content"], "جواب نصي")

    async def test_empty_transcript_does_not_call_the_model(self) -> None:
        ai = FakeAI(transcript="  ")
        service = ConversationService(self.settings, self.state, ai)
        with self.assertRaises(EmptyTranscriptError):
            await service.reply_to_voice(7, b"audio", "note.ogg")
        self.assertEqual([call[0] for call in ai.calls], ["transcribe"])
        self.assertEqual(self.state.recent_messages(7, 10), [])

    async def test_tts_failure_still_returns_the_text_reply(self) -> None:
        ai = FailingSpeech(reply="النص موجود")
        service = ConversationService(self.settings, self.state, ai)
        result = await service.reply_to_text(3, "احجي", with_voice=True)
        self.assertEqual(result.reply_text, "النص موجود")
        self.assertIsNone(result.audio)
        self.assertEqual(self.state.recent_messages(3, 10)[-1]["content"], "النص موجود")


if __name__ == "__main__":
    unittest.main()
