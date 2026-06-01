"""Models for the Trading System Architecture Program foundation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.trading_architecture_program.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    """Small dataclass serialization helper."""

    schema_version: str = SCHEMA_VERSION
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ArchitectureDomain(SerializableModel):
    domain_id: str = ""
    name: str = ""
    purpose: str = ""
    status: str = "Architecture only"
    prohibited_capabilities: list[str] | None = None


@dataclass(frozen=True)
class DecisionGate(SerializableModel):
    gate_id: str = ""
    name: str = ""
    approval_scope: str = ""
    required_evidence: list[str] | None = None
    may_approve_live_trading: bool = False


@dataclass(frozen=True)
class ProgramWorkstream(SerializableModel):
    workstream_id: str = ""
    name: str = ""
    purpose: str = ""
    deliverables: list[str] | None = None
    forbidden_outputs: list[str] | None = None


@dataclass(frozen=True)
class ProgramRegistry(SerializableModel):
    program_name: str = ""
    program_status: str = ""
    architecture_domains: list[dict[str, Any]] | None = None
    workstreams: list[dict[str, Any]] | None = None
    decision_gates: list[dict[str, Any]] | None = None
    prerequisites: list[str] | None = None
    blocked_items: list[str] | None = None
    forbidden_items: list[str] | None = None
