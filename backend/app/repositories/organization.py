from sqlalchemy import select

from app.models.organization import Membership, Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    model = Organization

    async def get_by_slug(self, slug: str) -> Organization | None:
        result = await self.session.execute(select(Organization).where(Organization.slug == slug))
        return result.scalar_one_or_none()


class MembershipRepository(BaseRepository[Membership]):
    model = Membership

    async def list_for_user(self, user_id) -> list[Membership]:
        result = await self.session.execute(
            select(Membership).where(Membership.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_membership(self, user_id, organization_id) -> Membership | None:
        result = await self.session.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_organization(self, organization_id) -> list[Membership]:
        from sqlalchemy.orm import selectinload

        result = await self.session.execute(
            select(Membership)
            .where(Membership.organization_id == organization_id)
            .options(selectinload(Membership.user))
        )
        return list(result.scalars().all())
