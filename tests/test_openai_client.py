import unittest
from types import SimpleNamespace

from openai import OpenAIError

from telegram_voice_bot.config import load_settings
from telegram_voice_bot.errors import AIError
from telegram_voice_bot.openai_client import AIClient, supports_tts_instructions


def _settings(**overrides: str):
    env = {
        "TELEGRAM_BOT_TOKEN": "token",
        "OPENAI_API_KEY": "key",
        "OWNER_TELEGRAM_ID": "1",
        "SYSTEM_PROMPT": "persona",
    }
    env.update(overrides)
    return load_settings(env)


class StubSpeech:
    def __init__(self, results):
        self.results = list(results)
        self.kwargs = []

    async def create(self, **kwargs):
        self.kwargs.append(kwargs)
        item = self.results.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class StubTranscriptions:
    def __init__(self):
        self.kwargs = None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(text="  يا هلا  ")


class StubCompletions:
    def __init__(self):
        self.kwargs = None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        message = SimpleNamespace(content=" زين ")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class StubResponse:
    def __init__(self, data: bytes):
        self.data = data

    async def aread(self) -> bytes:
        return self.data


def _client(speech, transcriptions=None, completions=None):
    return SimpleNamespace(
        audio=SimpleNamespace(
            speech=speech,
            transcriptions=transcriptions or StubTranscriptions(),
        ),
        chat=SimpleNamespace(completions=completions or StubCompletions()),
    )


class OpenAIClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_transcribe_and_complete_pass_the_configured_models(self) -> None:
        speech = StubSpeech([])
        transcriptions = StubTranscriptions()
        completions = StubCompletions()
        ai = AIClient(
            _settings(STT_LANGUAGE="ar", STT_PROMPT="بغداد"),
            client=_client(speech, transcriptions, completions),
        )
        self.assertEqual(await ai.transcribe(b"ogg", "note.oga"), "يا هلا")
        self.assertEqual(transcriptions.kwargs["model"], "gpt-4o-mini-transcribe")
        self.assertEqual(transcriptions.kwargs["language"], "ar")
        self.assertEqual(transcriptions.kwargs["prompt"], "بغداد")
        self.assertEqual(transcriptions.kwargs["file"][0], "note.oga")
        self.assertEqual(transcriptions.kwargs["file"][2], "audio/ogg")
        self.assertEqual(await ai.complete([{"role": "user", "content": "هلا"}]), "زين")
        self.assertEqual(completions.kwargs["model"], "gpt-4o-mini")
        self.assertEqual(completions.kwargs["max_completion_tokens"], 500)

    async def test_tts_instructions_follow_the_model(self) -> None:
        self.assertTrue(supports_tts_instructions("gpt-4o-mini-tts"))
        self.assertFalse(supports_tts_instructions("tts-1"))
        speech = StubSpeech([StubResponse(b"opus-bytes")])
        ai = AIClient(_settings(TTS_INSTRUCTIONS="احجي عراقي"), client=_client(speech))
        data, fmt = await ai.synthesize("هلا")
        self.assertEqual((data, fmt), (b"opus-bytes", "opus"))
        self.assertEqual(speech.kwargs[0]["instructions"], "احجي عراقي")
        self.assertEqual(speech.kwargs[0]["response_format"], "opus")

        plain = StubSpeech([StubResponse(b"mp3-bytes")])
        classic = AIClient(
            _settings(OPENAI_TTS_MODEL="tts-1", OPENAI_TTS_FORMAT="mp3", TTS_INSTRUCTIONS="ignored"),
            client=_client(plain),
        )
        await classic.synthesize("هلا")
        self.assertNotIn("instructions", plain.kwargs[0])

    async def test_tts_falls_back_to_mp3_and_auth_errors_do_not_retry(self) -> None:
        speech = StubSpeech([OpenAIError("bad format"), StubResponse(b"mp3")])
        ai = AIClient(_settings(), client=_client(speech))
        data, fmt = await ai.synthesize("هلا")
        self.assertEqual(data, b"mp3")
        self.assertEqual(fmt, "mp3")
        self.assertEqual([call["response_format"] for call in speech.kwargs], ["opus", "mp3"])

        class AuthError(OpenAIError):
            status_code = 401

        denied = StubSpeech([AuthError("no")])
        locked = AIClient(_settings(), client=_client(denied))
        with self.assertRaises(AIError):
            await locked.synthesize("هلا")
        self.assertEqual(len(denied.kwargs), 1)


if __name__ == "__main__":
    unittest.main()
