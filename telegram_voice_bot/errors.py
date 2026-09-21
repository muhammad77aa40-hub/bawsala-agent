class ConfigError(Exception):
    """Configuration is missing or invalid. The message is safe to print."""


class AIError(Exception):
    """An OpenAI call failed. The message is safe to send to the user."""


class EmptyTranscriptError(AIError):
    """Speech-to-text returned no usable words."""


USER_FACING_AI_ERROR = "ما كدرت أكمل الطلب هسه. جرب مرة ثانية بعد شوي."
