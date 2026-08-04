import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from main import app


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


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
