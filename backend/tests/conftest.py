import os
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, StaticPool

from app.database import get_db
from app.models import Base

# Defaults to the fast, zero-setup SQLite in-memory DB. Set
# TEST_DATABASE_URL to a real Postgres DSN (e.g.
# postgresql+asyncpg://srs:srs@localhost:5432/srs_test) to run the exact
# same suite against Postgres — this is how the "not Postgres-tested" gap
# noted elsewhere in this project gets closed for good, rather than
# re-verified by hand every time.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
_IS_POSTGRES = TEST_DATABASE_URL.startswith("postgresql")


@pytest_asyncio.fixture
async def db_engine():
    if _IS_POSTGRES:
        # Real network connections, not in-memory — no StaticPool trick
        # needed, but each test gets a clean schema since the database
        # persists across engine disposals (unlike SQLite's :memory:).
        engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
        return

    # A single shared in-memory SQLite connection for the life of each test,
    # so every session sees the same schema and data (StaticPool disables
    # SQLite's default "new connection per session" behavior).
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncSession:
    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_engine):
    from app.main import app

    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)

    async def _override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@example.com"


async def create_project(session: AsyncSession, **overrides):
    """Creates a real Organization + User + Project chain and returns the
    Project. Needed because Postgres enforces the foreign keys that
    Knowledge Graph nodes, Requirements, Security Analyses, Generated
    Documents, and Review Runs all declare against `projects.id` — SQLite
    doesn't enforce these by default, so tests that skip this and just
    make up a project_id via uuid4() pass locally but fail against a real
    Postgres database. Always call this *before* seeding a Knowledge Graph
    or creating anything else that references the returned project's id.
    """
    from app.models.organization import Organization
    from app.models.project import Project
    from app.models.user import User

    # The application has no authentication layer (see public_projects.py) —
    # User/Organization now exist purely as internal FK anchors, not
    # authenticated accounts, so there is no password to hash here.
    unique = uuid.uuid4().hex[:8]
    org = Organization(name=overrides.get("org_name", "Test Org"), slug=f"org-{unique}")
    session.add(org)
    await session.flush()
    user = User(
        email=f"user-{unique}@example.com",
        hashed_password="internal-no-auth",
        full_name="Test User",
    )
    session.add(user)
    await session.flush()
    project = Project(
        name=overrides.get("name", "Test Project"),
        short_name=overrides.get("short_name", "TP"),
        organization_id=org.id,
        owner_id=user.id,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project
