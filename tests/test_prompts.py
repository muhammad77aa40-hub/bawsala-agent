import tempfile
import unittest
from pathlib import Path

from telegram_voice_bot.config import load_settings
from telegram_voice_bot.prompts import (
    SAFETY_HINT,
    SPEECH_HINT,
    TASK_PREFIX,
    build_messages,
    build_system_prompt,
    resolve_persona,
)
from telegram_voice_bot.textutil import (
    combine_transcript,
    command_body,
    is_clear_command,
    prepare_speech_text,
    split_text,
)


def _settings(**overrides: str):
    env = {
        "TELEGRAM_BOT_TOKEN": "token",
        "OPENAI_API_KEY": "key",
        "OWNER_TELEGRAM_ID": "1",
        "SYSTEM_PROMPT": "from env",
    }
    env.update(overrides)
    return load_settings(env)


class PromptTests(unittest.TestCase):
    def test_persona_precedence_is_override_then_env_then_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "persona.md"
            path.write_text("من الملف", encoding="utf-8")
            env = _settings(SYSTEM_PROMPT="from env", PERSONA_PATH=str(path))
            self.assertEqual(resolve_persona(env, "من الأمر")[0], "من الأمر")
            self.assertEqual(resolve_persona(env, None)[0], "from env")
            bare = load_settings(
                {
                    "TELEGRAM_BOT_TOKEN": "token",
                    "OPENAI_API_KEY": "key",
                    "OWNER_TELEGRAM_ID": "1",
                    "PERSONA_PATH": str(path),
                }
            )
            text, source = resolve_persona(bare, None)
            self.assertEqual(text, "من الملف")
            self.assertIn("persona.md", source)
            self.assertIn("file", source)

    def test_system_prompt_includes_task_and_speech_hint(self) -> None:
        spoken = build_system_prompt("شخصية", "ساعد المستخدم", for_speech=True)
        self.assertIn("شخصية", spoken)
        self.assertIn(SAFETY_HINT, spoken)
        self.assertIn(TASK_PREFIX, spoken)
        self.assertIn("ساعد المستخدم", spoken)
        self.assertIn(SPEECH_HINT, spoken)
        written = build_system_prompt("شخصية", None, for_speech=False)
        self.assertNotIn(SPEECH_HINT, written)
        self.assertNotIn(TASK_PREFIX, written)

    def test_messages_keep_history_and_end_with_the_user(self) -> None:
        messages = build_messages(
            "system",
            [
                {"role": "user", "content": "قبل"},
                {"role": "assistant", "content": "جواب"},
                {"role": "system", "content": "ignore me"},
            ],
            "هسه",
        )
        self.assertEqual(
            [item["role"] for item in messages],
            ["system", "user", "assistant", "user"],
        )
        self.assertEqual(messages[-1]["content"], "هسه")


class TextUtilTests(unittest.TestCase):
    def test_command_body_keeps_newlines(self) -> None:
        self.assertEqual(command_body("/task@MyBot رتب التوصيل"), "رتب التوصيل")
        self.assertEqual(command_body("/persona\nسطر أول\nسطر ثاني"), "سطر أول\nسطر ثاني")
        self.assertEqual(command_body("/task"), "")
        self.assertTrue(is_clear_command("Reset"))
        self.assertTrue(is_clear_command("مسح"))
        self.assertFalse(is_clear_command("reset the persona now"))

    def test_transcript_caption_and_speech_limit(self) -> None:
        self.assertEqual(combine_transcript("شلونك", "بسرعة"), "شلونك\nبسرعة")
        self.assertEqual(combine_transcript("  ", "فقط"), "فقط")
        self.assertEqual(combine_transcript("", None), "")
        long_text = "كلمة " * 2000
        spoken = prepare_speech_text(long_text, limit=100)
        self.assertLessEqual(len(spoken), 100)
        self.assertTrue(spoken)

    def test_split_text_respects_the_limit(self) -> None:
        chunks = split_text("alpha beta gamma", limit=6)
        self.assertTrue(chunks)
        self.assertTrue(all(len(chunk) <= 6 for chunk in chunks))
        self.assertEqual("".join(chunks).replace(" ", ""), "alphabetagamma")


if __name__ == "__main__":
    unittest.main()
