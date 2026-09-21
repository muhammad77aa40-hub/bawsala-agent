import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from telegram_voice_bot.bot import main
from telegram_voice_bot.config import REPO_ROOT


class CliTests(unittest.TestCase):
    def test_check_succeeds_without_printing_secrets(self) -> None:
        stdout = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(stdout):
                code = main(
                    ["--check"],
                    environ={
                        "TELEGRAM_BOT_TOKEN": "super-secret-token",
                        "OPENAI_API_KEY": "super-secret-key",
                        "OWNER_TELEGRAM_ID": "42",
                        "DATABASE_PATH": str(Path(tmp) / "bot.db"),
                        "PERSONA_PATH": "config/persona.md",
                    },
                    load_env_file=False,
                )
        report = stdout.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Configuration OK", report)
        self.assertIn("Owner Telegram id: 42", report)
        self.assertIn("persona.md", report)
        self.assertNotIn("super-secret-token", report)
        self.assertNotIn("super-secret-key", report)
        self.assertTrue((REPO_ROOT / "config" / "persona.md").is_file())

    def test_missing_keys_exit_with_a_clear_message(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["--check"], environ={}, load_env_file=False)
        self.assertEqual(code, 1)
        self.assertIn("TELEGRAM_BOT_TOKEN", stderr.getvalue())
        self.assertIn("OPENAI_API_KEY", stderr.getvalue())
        self.assertIn("OWNER_TELEGRAM_ID", stderr.getvalue())


class RepoFileTests(unittest.TestCase):
    def test_env_example_has_empty_secrets_and_required_names(self) -> None:
        text = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
        for name in ("TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "OWNER_TELEGRAM_ID"):
            self.assertIn(f"{name}=", text)
        for line in text.splitlines():
            if line.startswith(("TELEGRAM_BOT_TOKEN=", "OPENAI_API_KEY=", "OWNER_TELEGRAM_ID=")):
                self.assertEqual(line.split("=", 1)[1], "")
        self.assertNotIn("sk-", text)
        ignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", ignore)
        self.assertIn(".venv/", ignore)

    def test_sample_persona_is_iraqi_arabic(self) -> None:
        text = (REPO_ROOT / "config" / "persona.md").read_text(encoding="utf-8")
        for marker in ("شلونك", "هسه", "ماكو", "عراقية"):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
