"""Runtime service container models."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


ServiceFactory = Callable[[], Any]


@dataclass
class ServiceDescriptor:
    """Describes a lazily initialized runtime service."""

    name: str
    factory: ServiceFactory
    singleton: bool = True
    instance: Any = None
    initialized: bool = False
