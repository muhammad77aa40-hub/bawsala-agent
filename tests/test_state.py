import tempfile
import unittest
from pathlib import Path

from telegram_voice_bot import state as state_module
from telegram_voice_bot.state import State


class StateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.state = State(Path(self.tmp.name) / "nested" / "bot.db")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_task_and_persona_round_trip(self) -> None:
        self.assertIsNone(self.state.get_standing_task())
        self.assertIsNone(self.state.get_persona_override())
        self.state.set_standing_task("  رتب الأفكار  ")
        self.state.set_persona_override("  احجي عراقي  ")
        self.assertEqual(self.state.get_standing_task(), "رتب الأفكار")
        self.assertEqual(self.state.get_persona_override(), "احجي عراقي")
        self.state.clear_standing_task()
        self.state.clear_persona_override()
        self.assertIsNone(self.state.get_standing_task())
        self.assertIsNone(self.state.get_persona_override())

    def test_history_is_oldest_first_and_scoped_to_the_chat(self) -> None:
        self.state.add_message(1, "user", "أول")
        self.state.add_message(1, "assistant", "ثاني")
        self.state.add_message(2, "user", "غير")
        self.assertEqual(
            self.state.recent_messages(1, 10),
            [
                {"role": "user", "content": "أول"},
                {"role": "assistant", "content": "ثاني"},
            ],
        )
        self.state.clear_history(1)
        self.assertEqual(self.state.recent_messages(1, 10), [])
        self.assertEqual(self.state.recent_messages(2, 10), [{"role": "user", "content": "غير"}])

    def test_old_messages_are_pruned(self) -> None:
        original = state_module.STORED_MESSAGES_PER_CHAT
        state_module.STORED_MESSAGES_PER_CHAT = 2
        try:
            self.state.add_message(5, "user", "واحد")
            self.state.add_message(5, "assistant", "اثنين")
            self.state.add_message(5, "user", "ثلاثة")
        finally:
            state_module.STORED_MESSAGES_PER_CHAT = original
        self.assertEqual(
            self.state.recent_messages(5, 10),
            [
                {"role": "assistant", "content": "اثنين"},
                {"role": "user", "content": "ثلاثة"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
