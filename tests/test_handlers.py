import unittest
from types import SimpleNamespace

from telegram_voice_bot.access import chat_is_allowed, owner_command_access
from telegram_voice_bot.handlers import _audio_filename, deliver_reply
from telegram_voice_bot.service import TurnResult


class AccessTests(unittest.TestCase):
    def test_private_chats_are_allowed_and_groups_are_opt_in(self) -> None:
        self.assertTrue(chat_is_allowed("private", allow_groups=False))
        self.assertFalse(chat_is_allowed("group", allow_groups=False))
        self.assertFalse(chat_is_allowed("supergroup", allow_groups=False))
        self.assertFalse(chat_is_allowed("channel", allow_groups=True))
        self.assertTrue(chat_is_allowed("group", allow_groups=True))
        self.assertTrue(chat_is_allowed("supergroup", allow_groups=True))

    def test_owner_commands_stay_in_a_private_chat_with_the_owner(self) -> None:
        self.assertEqual(owner_command_access("private", 7, 7, False), "allow")
        self.assertEqual(owner_command_access("private", 8, 7, False), "deny")
        self.assertEqual(owner_command_access("group", 7, 7, True), "ignore")
        self.assertEqual(owner_command_access("group", 7, 7, False), "ignore")
        self.assertEqual(owner_command_access("channel", 7, 7, True), "ignore")


class FilenameTests(unittest.TestCase):
    def test_voice_notes_default_to_ogg(self) -> None:
        media = SimpleNamespace(file_name=None, mime_type="audio/ogg")
        self.assertEqual(_audio_filename(media), "note.ogg")
        named = SimpleNamespace(file_name="clip.mp3", mime_type="audio/mpeg")
        self.assertEqual(_audio_filename(named), "clip.mp3")


class FakeMessage:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    async def reply_text(self, text, **kwargs) -> None:
        self.calls.append(("text", text))

    async def reply_voice(self, voice, **kwargs) -> None:
        voice.seek(0)
        self.calls.append(("voice", voice.read(), kwargs.get("caption"), kwargs.get("filename")))

    async def reply_audio(self, audio, **kwargs) -> None:
        audio.seek(0)
        self.calls.append(("audio", audio.read(), kwargs.get("caption"), kwargs.get("filename")))


class BoomVoice(FakeMessage):
    async def reply_voice(self, voice, **kwargs) -> None:
        raise RuntimeError("telegram rejected the voice note")


class DeliverTests(unittest.IsolatedAsyncioTestCase):
    async def test_voice_primary_sends_an_ogg_voice_note_with_caption(self) -> None:
        message = FakeMessage()
        await deliver_reply(
            message,
            TurnResult("in", "هلا", b"OggS", "opus"),
            voice_primary=True,
        )
        self.assertEqual(message.calls, [("voice", b"OggS", "هلا", "reply.ogg")])

    async def test_long_voice_reply_also_sends_the_full_text(self) -> None:
        message = FakeMessage()
        reply = "ا" * 1100
        await deliver_reply(
            message,
            TurnResult("in", reply, b"OggS", "opus"),
            voice_primary=True,
        )
        self.assertEqual(message.calls[0][0], "voice")
        self.assertIsNone(message.calls[0][2])
        self.assertEqual(message.calls[1], ("text", reply))

    async def test_text_primary_sends_text_then_optional_voice_without_caption(self) -> None:
        message = FakeMessage()
        await deliver_reply(
            message,
            TurnResult("in", "جواب", b"mp3", "mp3"),
            voice_primary=False,
        )
        self.assertEqual(message.calls[0], ("text", "جواب"))
        self.assertEqual(message.calls[1][0], "audio")
        self.assertIsNone(message.calls[1][2])
        self.assertEqual(message.calls[1][3], "reply.mp3")

    async def test_text_only_when_tts_is_missing(self) -> None:
        message = FakeMessage()
        await deliver_reply(
            message,
            TurnResult("in", "بس نص", None, None),
            voice_primary=True,
        )
        self.assertEqual(message.calls, [("text", "بس نص")])

    async def test_voice_send_failure_falls_back_to_text(self) -> None:
        message = BoomVoice()
        await deliver_reply(
            message,
            TurnResult("in", "النص البديل", b"OggS", "opus"),
            voice_primary=True,
        )
        self.assertEqual(message.calls, [("text", "النص البديل")])


if __name__ == "__main__":
    unittest.main()
