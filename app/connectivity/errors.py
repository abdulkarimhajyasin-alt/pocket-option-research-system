"""Connectivity error hierarchy."""


class ConnectorError(Exception):
    """Base exception for read-only connector failures."""


class ConnectorConnectionError(ConnectorError):
    """Raised when connector lifecycle operations fail."""


class ConnectorValidationError(ConnectorError):
    """Raised when connector configuration or environment is invalid."""


class ConnectorDataError(ConnectorError):
    """Raised when connector data fetch or validation fails."""


class ConnectorTimeoutError(ConnectorError):
    """Raised when connector operations exceed expected timing."""


class ConnectorUnsafeOperationError(ConnectorError):
    """Raised when an execution-capable operation is attempted."""
