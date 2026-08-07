import uuid

from sqlalchemy import select

from app.models.knowledge_graph import KnowledgeGraphEdge, KnowledgeGraphNode
from app.repositories.base import BaseRepository


class KnowledgeGraphNodeRepository(BaseRepository[KnowledgeGraphNode]):
    model = KnowledgeGraphNode

    async def list_for_project(self, project_id: uuid.UUID) -> list[KnowledgeGraphNode]:
        result = await self.session.execute(
            select(KnowledgeGraphNode).where(KnowledgeGraphNode.project_id == project_id)
        )
        return list(result.scalars().all())

    async def get_by_concept_key(
        self, project_id: uuid.UUID, concept_key: str
    ) -> KnowledgeGraphNode | None:
        result = await self.session.execute(
            select(KnowledgeGraphNode).where(
                KnowledgeGraphNode.project_id == project_id,
                KnowledgeGraphNode.concept_key == concept_key,
            )
        )
        return result.scalar_one_or_none()


class KnowledgeGraphEdgeRepository(BaseRepository[KnowledgeGraphEdge]):
    model = KnowledgeGraphEdge

    async def list_for_nodes(self, node_ids: list[uuid.UUID]) -> list[KnowledgeGraphEdge]:
        if not node_ids:
            return []
        result = await self.session.execute(
            select(KnowledgeGraphEdge).where(KnowledgeGraphEdge.node_id.in_(node_ids))
        )
        return list(result.scalars().all())
