from __future__ import annotations

PRIVATE = "private"
GROUP_TYPES = {"group", "supergroup"}


def chat_is_allowed(chat_type: str, allow_groups: bool) -> bool:
    if chat_type == PRIVATE:
        return True
    return allow_groups and chat_type in GROUP_TYPES


def owner_command_access(
    chat_type: str,
    user_id: int | None,
    owner_id: int,
    allow_groups: bool,
) -> str:
    """Return allow, deny, or ignore for an owner-only command."""
    if not chat_is_allowed(chat_type, allow_groups):
        return "ignore"
    if chat_type != PRIVATE:
        return "ignore"
    if user_id == owner_id:
        return "allow"
    return "deny"
