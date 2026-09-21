import tempfile
import unittest
from pathlib import Path

from telegram_voice_bot.config import REPO_ROOT, load_settings
from telegram_voice_bot.errors import ConfigError


def _env(**overrides: str) -> dict[str, str]:
    env = {
        "TELEGRAM_BOT_TOKEN": "token-secret",
        "OPENAI_API_KEY": "key-secret",
        "OWNER_TELEGRAM_ID": "99",
        "SYSTEM_PROMPT": "persona from env",
    }
    env.update(overrides)
    return env


class ConfigTests(unittest.TestCase):
    def test_missing_keys_are_listed_together(self) -> None:
        with self.assertRaises(ConfigError) as caught:
            load_settings({})
        message = str(caught.exception)
        self.assertIn("TELEGRAM_BOT_TOKEN", message)
        self.assertIn("OPENAI_API_KEY", message)
        self.assertIn("OWNER_TELEGRAM_ID", message)
        self.assertIn(".env.example", message)

    def test_owner_id_must_be_a_positive_integer(self) -> None:
        with self.assertRaises(ConfigError):
            load_settings(_env(OWNER_TELEGRAM_ID="nope"))
        with self.assertRaises(ConfigError):
            load_settings(_env(OWNER_TELEGRAM_ID="0"))

    def test_rejects_bad_boolean_and_voice_format(self) -> None:
        with self.assertRaises(ConfigError):
            load_settings(_env(ALLOW_GROUPS="maybe"))
        with self.assertRaises(ConfigError):
            load_settings(_env(OPENAI_TTS_FORMAT="midi"))

    def test_defaults_and_secret_repr(self) -> None:
        settings = load_settings(_env())
        self.assertEqual(settings.owner_telegram_id, 99)
        self.assertFalse(settings.allow_groups)
        self.assertFalse(settings.always_voice)
        self.assertEqual(settings.stt_language, "ar")
        self.assertEqual(settings.openai_tts_format, "opus")
        self.assertEqual(settings.history_limit, 20)
        rendered = repr(settings)
        self.assertNotIn("token-secret", rendered)
        self.assertNotIn("key-secret", rendered)

    def test_empty_language_disables_the_hint(self) -> None:
        settings = load_settings(_env(STT_LANGUAGE="", TTS_INSTRUCTIONS=""))
        self.assertIsNone(settings.stt_language)
        self.assertIsNone(settings.tts_instructions)

    def test_relative_paths_resolve_from_the_repo_root(self) -> None:
        settings = load_settings(_env(DATABASE_PATH="data/bot.db", PERSONA_PATH="config/persona.md"))
        self.assertEqual(settings.database_path, REPO_ROOT / "data" / "bot.db")
        self.assertEqual(settings.persona_path, REPO_ROOT / "config" / "persona.md")

    def test_system_prompt_does_not_require_the_persona_file(self) -> None:
        missing = Path(tempfile.gettempdir()) / "missing-persona-does-not-exist.md"
        settings = load_settings(_env(PERSONA_PATH=str(missing), SYSTEM_PROMPT="from env"))
        self.assertEqual(settings.system_prompt, "from env")

    def test_missing_persona_file_is_an_error_without_system_prompt(self) -> None:
        missing = Path(tempfile.gettempdir()) / "missing-persona-does-not-exist.md"
        env = _env(PERSONA_PATH=str(missing))
        del env["SYSTEM_PROMPT"]
        with self.assertRaises(ConfigError) as caught:
            load_settings(env)
        self.assertIn("Persona file not found", str(caught.exception))

    def test_flags_parse_true_values(self) -> None:
        settings = load_settings(_env(ALLOW_GROUPS="true", ALWAYS_VOICE="yes"))
        self.assertTrue(settings.allow_groups)
        self.assertTrue(settings.always_voice)


if __name__ == "__main__":
    unittest.main()
