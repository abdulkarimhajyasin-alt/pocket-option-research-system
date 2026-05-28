"""UTC-aware market session filtering."""

from dataclasses import dataclass
from datetime import UTC, datetime, time

from loguru import logger


@dataclass(frozen=True)
class SessionWindow:
    """Defines a UTC trading session window."""

    name: str
    start: time
    end: time

    def contains(self, timestamp: datetime) -> bool:
        """Return True when timestamp is inside the session window."""
        if timestamp.tzinfo is None:
            raise ValueError("Session filtering requires timezone-aware timestamps")

        current = timestamp.astimezone(UTC).time()
        if self.start <= self.end:
            return self.start <= current < self.end
        return current >= self.start or current < self.end


class SessionFilter:
    """Filters timestamps by configured market sessions."""

    DEFAULT_SESSIONS = {
        "asian": SessionWindow("asian", time(0, 0), time(8, 0)),
        "london": SessionWindow("london", time(7, 0), time(16, 0)),
        "new_york": SessionWindow("new_york", time(12, 0), time(21, 0)),
    }

    def __init__(self, sessions: dict[str, SessionWindow] | None = None) -> None:
        self.sessions = sessions or self.DEFAULT_SESSIONS

    def is_allowed(self, timestamp: datetime, allowed_sessions: tuple[str, ...]) -> bool:
        """Return True if timestamp falls inside any allowed session."""
        if not allowed_sessions:
            return True

        for session_name in allowed_sessions:
            window = self.get_session(session_name)
            if window.contains(timestamp):
                logger.info("Timestamp {} accepted by {} session", timestamp, session_name)
                return True

        logger.info("Timestamp {} rejected by session filters {}", timestamp, allowed_sessions)
        return False

    def get_session(self, name: str) -> SessionWindow:
        """Return a configured session by name."""
        normalized_name = name.strip().lower()
        if normalized_name not in self.sessions:
            raise KeyError(f"Unknown trading session: {name}")
        return self.sessions[normalized_name]

    def validate_sessions(self, sessions: tuple[str, ...]) -> bool:
        """Validate that session names exist."""
        for session in sessions:
            self.get_session(session)
        return True
