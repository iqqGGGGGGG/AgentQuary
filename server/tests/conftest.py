import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

import database
from database import Base, get_db
from main import app


test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        from services.achievements import seed_achievements
        await seed_achievements(session)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session):
    from models.orm import User
    user = User(openid="test_openid_001", nickname="测试用户")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_client(test_user):
    from auth import create_access_token

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {create_access_token(test_user)}"},
    ) as ac:
        yield ac


@pytest.fixture
def mock_generate_result():
    return {
        "topic": "太阳系基础知识",
        "questions": [
            {
                "id": 1,
                "type": "single_choice",
                "question": "太阳系中最大的行星是？",
                "options": ["地球", "木星", "土星", "火星"],
                "answer": 1,
                "explanation": "木星是太阳系中体积和质量最大的行星。",
            },
            {
                "id": 2,
                "type": "true_false",
                "question": "太阳是一颗恒星。",
                "options": ["正确", "错误"],
                "answer": 0,
                "explanation": "太阳是一颗典型的黄矮星，属于恒星。",
            },
        ],
    }


@pytest.fixture
def mock_report_result():
    return {
        "summary": "你对太阳系基础知识掌握不错，行星大小排序记得很准，但恒星的定义还需要再巩固一下。",
        "encouragement": "继续加油！",
    }
