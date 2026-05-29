"""External feed error types for read-only data integrations."""


class ExternalFeedError(Exception):
    """Base error for external data feed operations."""


class FeedConfigurationError(ExternalFeedError):
    """Raised when a feed is configured with invalid research settings."""


class FeedConnectionError(ExternalFeedError):
    """Raised when a read-only feed cannot start or reconnect."""


class FeedValidationError(ExternalFeedError):
    """Raised when incoming feed data cannot be normalized or validated."""


class FeedRegistryError(ExternalFeedError):
    """Raised when feed registration or lookup fails."""
