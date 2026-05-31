"""Research knowledge graph package.

This package builds relationship intelligence from local research reports only.
It does not connect to brokers, automate browsers, authenticate, execute trades,
place orders, handle money, or provide trading automation.
"""

from app.knowledge_graph.service import KnowledgeGraphService

__all__ = ["KnowledgeGraphService"]
