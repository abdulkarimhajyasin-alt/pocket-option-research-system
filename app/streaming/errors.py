"""Streaming-specific exceptions."""


class StreamError(Exception):
    """Base exception for read-only market stream failures."""


class StreamValidationError(StreamError):
    """Raised when stream data fails strict validation."""


class StreamConfigurationError(StreamError):
    """Raised when stream configuration is invalid."""


class StreamUnsafeOperationError(StreamError):
    """Raised when an execution-like operation is attempted on a stream."""


class StreamEnvironmentError(StreamError):
    """Raised when a stream cannot run in the local environment."""
