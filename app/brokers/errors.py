"""Broker adapter error hierarchy."""


class BrokerError(Exception):
    """Base class for broker adapter failures."""


class BrokerConnectionError(BrokerError):
    """Raised when a broker adapter cannot connect or stay connected."""


class BrokerValidationError(BrokerError):
    """Raised when broker configuration or environment validation fails."""


class BrokerExecutionError(BrokerError):
    """Raised when validated broker execution fails locally."""


class BrokerTimeoutError(BrokerError):
    """Raised when a broker operation exceeds its allowed time."""
