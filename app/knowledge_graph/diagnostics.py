"""Diagnostics for the research knowledge graph."""

from __future__ import annotations

from app.knowledge_graph.models import KnowledgeDiagnostic, KnowledgeGraphResult


class KnowledgeGraphDiagnostics:
    """Detect isolated entities, weak areas, broken chains, and low confidence."""

    def evaluate(self, graph: KnowledgeGraphResult) -> tuple[KnowledgeDiagnostic, ...]:
        diagnostics: list[KnowledgeDiagnostic] = []
        connected = {edge.source_id for edge in graph.edges} | {
            edge.target_id for edge in graph.edges
        }
        isolated = [node.node_id for node in graph.nodes if node.node_id not in connected]
        weak_edges = [edge for edge in graph.edges if edge.confidence < 50]
        if isolated:
            diagnostics.append(
                self._diag("عقد معزولة", "متوسط", "تقليل العقد المعزولة")
            )
        if graph.relationship_density < 0.08:
            diagnostics.append(
                self._diag("مناطق معرفة ضعيفة", "متوسط", "زيادة الربط")
            )
        if not graph.edges:
            diagnostics.append(
                self._diag("سلاسل مكسورة", "مرتفع", "تقوية سلاسل المعرفة")
            )
        if graph.edge_count < graph.node_count:
            diagnostics.append(
                self._diag("علاقات مفقودة", "منخفض", "تحسين العلاقات")
            )
        if weak_edges:
            diagnostics.append(
                self._diag("علاقات منخفضة الثقة", "منخفض", "تحسين جودة البيانات")
            )
        if not diagnostics:
            diagnostics.append(
                self._diag("مراجعة دورية للعلاقات", "منخفض", "تحسين العلاقات")
            )
        return tuple(diagnostics)

    def _diag(self, name: str, severity: str, detail: str) -> KnowledgeDiagnostic:
        return KnowledgeDiagnostic(name=name, severity=severity, detail=detail)
