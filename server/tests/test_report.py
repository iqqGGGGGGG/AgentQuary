import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_report_success(client, mock_report_result):
    with patch("routers.report.chain_report") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=mock_report_result)
        resp = await client.post("/api/report", json={
            "topic": "太阳系基础知识",
            "questions": [
                {"question": "最大的行星？", "options": ["地球", "木星"], "answer": 1},
                {"question": "太阳是恒星？", "options": ["正确", "错误"], "answer": 0},
            ],
            "user_answers": [1, 1],
            "duration_seconds": 120,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["accuracy"] == 0.5
    assert data["correct_count"] == 1
    assert data["total_count"] == 2
    assert len(data["mastered"]) == 1
    assert len(data["weak"]) == 1
    assert "summary" in data
    assert "encouragement" in data


@pytest.mark.asyncio
async def test_report_all_correct(client, mock_report_result):
    with patch("routers.report.chain_report") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=mock_report_result)
        resp = await client.post("/api/report", json={
            "topic": "测试主题",
            "questions": [
                {"question": "问题1", "options": ["A", "B"], "answer": 0},
            ],
            "user_answers": [0],
            "duration_seconds": 60,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["accuracy"] == 1.0
    assert data["correct_count"] == 1
    assert len(data["mastered"]) == 1
    assert len(data["weak"]) == 0


@pytest.mark.asyncio
async def test_report_chain_fallback(client):
    with patch("routers.report.chain_report") as mock_chain:
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("AI error"))
        resp = await client.post("/api/report", json={
            "topic": "测试",
            "questions": [
                {"question": "Q1", "options": ["A", "B"], "answer": 0},
            ],
            "user_answers": [0],
            "duration_seconds": 30,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert "测试" in data["summary"]
    assert data["encouragement"] == "继续加油！"


@pytest.mark.asyncio
async def test_report_wrong_answers(client, mock_report_result):
    with patch("routers.report.chain_report") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=mock_report_result)
        resp = await client.post("/api/report", json={
            "topic": "测试",
            "questions": [
                {"question": "Q1", "options": ["A", "B", "C", "D"], "answer": 0},
                {"question": "Q2", "options": ["正确", "错误"], "answer": 1},
            ],
            "user_answers": [2, 0],
            "duration_seconds": 90,
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["accuracy"] == 0.0
    assert data["correct_count"] == 0
    assert len(data["weak"]) == 2


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "知识闯关 API is running"
