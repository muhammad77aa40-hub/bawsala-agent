# Telegram voice-note agent

A private Telegram bot you run on your Mac. People send it a **voice note** or a text message. The bot answers with OpenAI.

A voice note is transcribed, answered, then spoken back as another Telegram voice message. A text message gets a text reply. Live Telegram voice calls are out of scope: this bot only handles voice messages (the round microphone notes) and ordinary text.

Persona, dialect, and the owner’s standing task are configuration. You do not edit the Python code to change how it speaks.

## What you need

- A Mac with Python 3.11 or newer (`python3 --version`)
- A Telegram account
- An OpenAI API key with billing enabled

The bot uses long polling. Leave the Terminal window open while you want it online. The Mac has to stay awake.

## 1. Create the bot with BotFather

1. In Telegram, open `@BotFather`.
2. Send `/newbot`.
3. Choose a display name and a username that ends in `bot`.
4. Copy the HTTP API token. That value is `TELEGRAM_BOT_TOKEN`.
5. Optional: `/setdescription` and tell people to send a voice note. The bot cannot join a live call.

## 2. Create an OpenAI API key

1. Open [OpenAI API keys](https://platform.openai.com/api-keys).
2. Create a key. That value is `OPENAI_API_KEY`.
3. Confirm the account has billing. Transcription, chat, and speech each spend credit.

## 3. Get your Telegram user id

1. In Telegram, open `@userinfobot` and press Start.
2. Copy the numeric `Id`. That value is `OWNER_TELEGRAM_ID`.
3. After the bot is running, send it `/whoami`. The reply should show the same number and say this account is the owner.

Only this user can change the persona or the standing task. Anyone can still send a private message.

## 4. Configure and run

From the repository root:

```bash
cp .env.example .env
```

Edit `.env` and set the three required values. Leave the other lines as they are until you want a different model or voice.

```bash
make install
make check
make run
```

`make check` confirms the keys, the persona file, and the local database without connecting to Telegram. `make run` starts polling. Stop it with Control-C.

If the Mac sleeps and drops the bot, run:

```bash
caffeinate -i make run
```

On a new Mac, install Python 3.11+ from [python.org](https://www.python.org/downloads/) or Homebrew (`brew install python@3.12`). The installer includes `venv`, which `make install` uses.

## Talk to the bot

Open a private chat with the bot and press Start.

| You send | The bot does |
| --- | --- |
| Voice note | Transcribes it, writes a reply, speaks the reply back as a voice note |
| Text | Replies with text |
| Text while `ALWAYS_VOICE=true` | Replies with text and a voice note |

Audio files (not only voice notes) are transcribed the same way. Replies that do not fit in a voice caption are also sent as text. If speech synthesis fails, you still get the text.

### Owner commands

Send these in a private chat from the owner account:

- `/persona` shows the active personality.
- `/persona` followed by new text replaces it until you reset.
- `/persona reset` goes back to `config/persona.md`, or to `SYSTEM_PROMPT` if that variable is set.
- `/task` shows the standing task.
- `/task` followed by text saves a task the bot follows in later chats. Example: `/task جاوب باختصار، وإذا السؤال عن سعر قول ماكو سعر ثابت واطلب التفاصيل.`
- `/task reset` clears that task.
- `/reset` clears the conversation history for this chat only. Any user can do that for their own chat.

The sample persona speaks Iraqi Arabic: شلونك، هسه، ماكو، and the rest of everyday speech. Edit `config/persona.md` in any text editor and save it as UTF-8. The next reply picks up the file, unless a `/persona` override or `SYSTEM_PROMPT` is active.

`/persona` wins over `SYSTEM_PROMPT`, and `SYSTEM_PROMPT` wins over the file. Changing `SYSTEM_PROMPT` needs a restart. The file and `/persona` are read on each reply.

## Useful settings

All of these live in `.env`. See `.env.example` for the full list.

| Variable | Default | What it does |
| --- | --- | --- |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat Completions model for every reply |
| `OPENAI_STT_MODEL` | `gpt-4o-mini-transcribe` | Speech-to-text. `whisper-1` and `gpt-4o-transcribe` also work |
| `STT_LANGUAGE` | `ar` | Language hint. Empty lets OpenAI detect the language |
| `OPENAI_TTS_MODEL` | `gpt-4o-mini-tts` | Text-to-speech |
| `OPENAI_TTS_VOICE` | `alloy` | `alloy`, `ash`, `coral`, `nova`, `shimmer`, and the other OpenAI voices |
| `OPENAI_TTS_FORMAT` | `opus` | `opus` is sent as a Telegram voice note. `mp3` is sent as an audio file |
| `TTS_INSTRUCTIONS` | Iraqi Arabic delivery | Style hint for `gpt-4o` TTS models |
| `ALLOW_GROUPS` | `false` | Group and supergroup messages are ignored until this is `true` |
| `ALWAYS_VOICE` | `false` | Also speak replies to text messages |
| `HISTORY_LIMIT` | `20` | How many past messages are sent back to the model |

Owner commands stay in the private owner chat even when groups are enabled. In BotFather, disable privacy mode only if the bot should see every group message rather than commands and mentions.

## Architecture

```
Telegram private chat
        |
        v
python-telegram-bot  (long polling on your Mac)
        |
        |-- voice note --> OpenAI transcription
        v
Chat Completions
  system prompt: persona + standing task
  history: recent turns in SQLite
        |
        v
reply text
        |
        +-- voice note in, or ALWAYS_VOICE=true
        |       --> OpenAI text-to-speech (opus)
        |       --> Telegram voice message
        +-- ordinary text
                --> Telegram text message
```

`config/persona.md` is the default personality. `data/bot.db` (SQLite, created on first run) stores the owner’s `/persona` override, the `/task` text, and recent chat text. Nothing in that database is committed. Messages are sent to OpenAI to produce the reply and, on the voice path, the audio.

Missing `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, or `OWNER_TELEGRAM_ID` stops startup with a short message instead of a stack trace. The process logs model names and chat ids, not your keys. Transcripts are logged only when `LOG_LEVEL=DEBUG`.

## If something goes wrong

- `Missing required environment variables` — `.env` is missing a required line, or you started the bot outside the repository root. `make run` loads `.env` from this folder.
- The bot is silent in a group — that is the default. Set `ALLOW_GROUPS=true` and restart.
- Telegram says the bot is already running — only one `make run` can poll at a time.
- OpenAI returns 401 — the API key is wrong, or billing is not enabled.
- A voice note comes back as text only — speech synthesis failed. The terminal has the reason, and the text is still the answer.
- `make install` cannot create a virtualenv — install Python 3.11+ from python.org so `python3 -m venv` works.

Run the tests with `make test`.

## الإعداد بالعربي

هذا بوت رسائل صوتية (فويس نوت) على تلفرام، مو مكالمات مباشرة. يشتغل على ماك ويحتاج يبقى التيرمنل مفتوح.

1. من `@BotFather` سوّي بوت جديد بـ `/newbot` وانسخ التوكن.
2. من حساب OpenAI سوّي مفتاح API وحطه بملف `.env`.
3. من `@userinfobot` انسخ رقمك وحطه بـ `OWNER_TELEGRAM_ID`.
4. من مجلد المشروع:

```bash
cp .env.example .env
make install
make check
make run
```

افتح البوت بالخاص ودز فويس نوت. البوت يفرغ الصوت، يجاوب، ويرجع لك الجواب بصوت. إذا تكتب نص، يرجعلك نص. الشخصية الافتراضية تحجي عراقي، وتعدلها من `config/persona.md` أو من الأمر `/persona`. المهمة الثابتة تنحط بأمر `/task` وتنحفظ على جهازك.

## Other files in this repository

`index.js`, `package.json`, `railway.json`, and `env.example` are a separate WhatsApp agent. This Telegram bot does not start them, and `make run` does not change them. Use `.env.example` (with the dot) for the Telegram bot. Do not put real keys in either example file.
