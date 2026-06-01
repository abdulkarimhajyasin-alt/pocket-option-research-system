"""Models for production system design blueprints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.production_system_design.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    """Small dataclass serialization helper."""

    schema_version: str = SCHEMA_VERSION
    design_only: bool = True
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ProductionDesignItem(SerializableModel):
    item_id: str = ""
    title: str = ""
    description: str = ""
    category: str = ""
    priority: str = "متوسط"
    status: str = "تصميم فقط"
    implementation_allowed_now: bool = False
    future_program_required: bool = True
    safety_notes: list[str] | None = None
    verification_method: str = "design review"


@dataclass(frozen=True)
class ProductionDesignCategory(SerializableModel):
    category_id: str = ""
    title: str = ""
    status: str = "تصميم فقط"
    items: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class ProductionTopology(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class ServiceBoundary(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class RuntimeBlueprint(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class EnvironmentPlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class ConfigurationPlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class SecretsPlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class DatabasePlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class EventQueuePlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class LoggingPlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class MonitoringPlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class AlertingPlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class IncidentResponsePlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class BackupRecoveryPlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class ReleaseRollbackPlan(ProductionDesignCategory):
    pass


@dataclass(frozen=True)
class ProductionReadinessGate(SerializableModel):
    gate_id: str = ""
    title: str = ""
    required: bool = True
    current_status: str = "missing"
    blocks_progress: bool = True
    may_approve_live_trading: bool = False


@dataclass(frozen=True)
class ProductionDesignSummary(SerializableModel):
    design_status: str = "Design Incomplete"
    design_domain_count: int = 0
    service_boundary_count: int = 0
    readiness_state: str = "Not Ready"
    diagnostic_count: int = 0
    recommendation_count: int = 0


@dataclass(frozen=True)
class ProductionDesignDiagnostics(SerializableModel):
    code: str = ""
    severity: str = "متوسط"
    message: str = ""


@dataclass(frozen=True)
class ProductionDesignRecommendation(SerializableModel):
    recommendation_id: str = ""
    text: str = ""
    priority: str = "متوسط"


def design_category(model, category_id: str, title: str, topics: list[str]):
    """Create a design category with standard design-only items."""
    items = [
        ProductionDesignItem(
            item_id=f"{category_id.upper()}-{index:02d}",
            title=topic,
            description=f"Design-only blueprint for {topic.lower()}.",
            category=category_id,
            priority="مرتفع" if index <= 2 else "متوسط",
            safety_notes=[
                "Design artifact only.",
                "No current implementation or external connectivity is allowed.",
            ],
        ).to_dict()
        for index, topic in enumerate(topics, 1)
    ]
    return model(category_id=category_id, title=title, items=items)
