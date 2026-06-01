"""Event and queue strategy design blueprint."""

from app.production_system_design.models import EventQueuePlan, design_category


class EventQueueStrategyBuilder:
    """Build event and queue strategy design only."""

    def build(self) -> EventQueuePlan:
        return design_category(
            EventQueuePlan,
            "event_queue_strategy",
            "Event / Queue Strategy",
            [
                "Command queue concept",
                "Event bus concept",
                "Audit event flow",
                "Risk event flow",
                "Monitoring event flow",
                "Dead letter concept",
                "Retry policy concept",
            ],
        )
