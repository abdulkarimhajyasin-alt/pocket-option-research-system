"""Future architecture-program workstreams."""

from __future__ import annotations

from app.trading_architecture_program.models import ProgramWorkstream


class ProgramWorkstreamBuilder:
    """Build future workstreams as planning containers only."""

    def build(self) -> list[ProgramWorkstream]:
        names = [
            "Execution Architecture",
            "Broker Architecture",
            "Risk Governance",
            "Monitoring & Observability",
            "Infrastructure",
            "Compliance & Legal",
            "Operations",
            "Audit & Controls",
        ]
        return [
            ProgramWorkstream(
                workstream_id=name.lower().replace(" & ", "-").replace(" ", "-"),
                name=name,
                purpose=f"Define {name} documents, controls, and review gates.",
                deliverables=[
                    "architecture brief",
                    "risk and safety notes",
                    "review checklist",
                ],
                forbidden_outputs=[
                    "executable broker code",
                    "order placement logic",
                    "credential handling",
                    "external connectivity",
                ],
            )
            for name in names
        ]
