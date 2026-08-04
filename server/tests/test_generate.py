import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_get_examples(client):
    resp = await client.get("/api/examples")
    assert resp.status_code == 200
    data = resp.json()
    assert "examples" in data
    assert len(data["examples"]) == 10
    first = data["examples"][0]
    assert "id" in first
    assert "title" in first
    assert "category" in first
    assert "description" in first


@pytest.mark.asyncio
async def test_generate_quiz_success(client, mock_generate_result):
    with patch("routers.generate.chain_generate") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=mock_generate_result)
        resp = await client.post("/api/generate", json={
            "content": "太阳系基础知识",
            "question_count": 5,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["topic"] == "太阳系基础知识"
    assert len(data["questions"]) == 2
    assert data["questions"][0]["type"] == "single_choice"
    assert data["questions"][1]["type"] == "true_false"


@pytest.mark.asyncio
async def test_generate_quiz_empty_content(client):
    resp = await client.post("/api/generate", json={
        "content": "",
        "question_count": 10,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_generate_quiz_count_out_of_range(client):
    resp = await client.post("/api/generate", json={
        "content": "测试内容",
        "question_count": 3,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_generate_quiz_chain_error(client):
    with patch("routers.generate.chain_generate") as mock_chain:
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API timeout"))
        resp = await client.post("/api/generate", json={
            "content": "测试内容",
            "question_count": 5,
        })
    assert resp.status_code == 500
    assert "题目生成失败" in resp.json()["detail"]
