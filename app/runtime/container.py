"""Lightweight dependency injection container for runtime services."""

from typing import Any

from loguru import logger

from app.runtime.services import ServiceDescriptor, ServiceFactory


class ServiceContainer:
    """Registers and resolves runtime services with lazy singleton support."""

    def __init__(self) -> None:
        self._services: dict[str, ServiceDescriptor] = {}

    def register(self, name: str, factory: ServiceFactory, singleton: bool = True) -> None:
        """Register a service factory."""
        key = self._normalize(name)
        if key in self._services:
            raise KeyError(f"Service already registered: {name}")
        self._services[key] = ServiceDescriptor(name=key, factory=factory, singleton=singleton)
        logger.bind(component="orchestrator").info("Registered service {}", key)

    def register_instance(self, name: str, instance: Any) -> None:
        """Register an already-created service instance."""
        key = self._normalize(name)
        self._services[key] = ServiceDescriptor(
            name=key,
            factory=lambda: instance,
            singleton=True,
            instance=instance,
            initialized=True,
        )
        logger.bind(component="orchestrator").info("Registered service instance {}", key)

    def get(self, name: str) -> Any:
        """Resolve a service by name."""
        key = self._normalize(name)
        if key not in self._services:
            raise KeyError(f"Unknown service: {name}")
        descriptor = self._services[key]
        if descriptor.singleton:
            if not descriptor.initialized:
                descriptor.instance = descriptor.factory()
                descriptor.initialized = True
                logger.bind(component="orchestrator").info("Initialized service {}", key)
            return descriptor.instance
        return descriptor.factory()

    def dependency_graph(self) -> dict[str, dict[str, object]]:
        """Return service registration diagnostics."""
        return {
            name: {"singleton": desc.singleton, "initialized": desc.initialized}
            for name, desc in sorted(self._services.items())
        }

    def names(self) -> list[str]:
        """Return registered service names."""
        return sorted(self._services)

    def _normalize(self, name: str) -> str:
        return name.strip().lower()
