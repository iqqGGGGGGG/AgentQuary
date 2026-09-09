import pytest
from unittest.mock import AsyncMock, patch
from chains.research_chain import ResearchResult


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
    from chains.research_chain import ResearchResult
    with patch("routers.generate.chain_generate") as mock_chain, \
         patch("routers.generate.research_content", new_callable=AsyncMock) as mock_research:
        mock_chain.ainvoke = AsyncMock(return_value=mock_generate_result)
        mock_research.return_value = ResearchResult(content="太阳系基础知识", search_used=False)
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
    assert data["search_used"] is False


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
    from chains.research_chain import ResearchResult
    with patch("routers.generate.chain_generate") as mock_chain, \
         patch("routers.generate.research_content", new_callable=AsyncMock) as mock_research:
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API timeout"))
        mock_research.return_value = ResearchResult(content="测试内容", search_used=False)
        resp = await client.post("/api/generate", json={
            "content": "测试内容",
            "question_count": 5,
        })
    assert resp.status_code == 500
    assert "题目生成失败" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_generate_quiz_excludes_previous_questions(client, mock_generate_result):
    old_question = mock_generate_result["questions"][0]
    new_question = {
        "id": 99,
        "type": "true_false",
        "question": "木星拥有太阳系中最明显的行星环。",
        "options": ["正确", "错误"],
        "answer": 1,
        "explanation": "太阳系中最明显的行星环属于土星。",
    }
    duplicate_batch = {"topic": "太阳系", "questions": [old_question]}
    fresh_batch = {"topic": "太阳系", "questions": [new_question]}

    with patch("routers.generate.chain_generate") as mock_chain, \
         patch("routers.generate.research_content", new_callable=AsyncMock) as mock_research:
        mock_chain.ainvoke = AsyncMock(side_effect=[duplicate_batch, fresh_batch, fresh_batch])
        from chains.research_chain import ResearchResult
        mock_research.return_value = ResearchResult(content="太阳系基础知识", search_used=False)
        resp = await client.post("/api/generate", json={
            "content": "太阳系基础知识",
            "question_count": 5,
            "excluded_questions": [old_question["question"]],
        })

    assert resp.status_code == 200
    questions = resp.json()["questions"]
    assert [item["question"] for item in questions] == [new_question["question"]]
    assert questions[0]["id"] == 1
    assert mock_chain.ainvoke.await_count == 3
    first_call = mock_chain.ainvoke.await_args_list[0].args[0]
    assert old_question["question"] in first_call["excluded_questions"]


@pytest.mark.asyncio
async def test_generate_quiz_fails_when_all_questions_are_excluded(client, mock_generate_result):
    duplicate = {"topic": "太阳系", "questions": [mock_generate_result["questions"][0]]}
    from chains.research_chain import ResearchResult
    with patch("routers.generate.chain_generate") as mock_chain, \
         patch("routers.generate.research_content", new_callable=AsyncMock) as mock_research:
        mock_chain.ainvoke = AsyncMock(return_value=duplicate)
        mock_research.return_value = ResearchResult(content="太阳系基础知识", search_used=False)
        resp = await client.post("/api/generate", json={
            "content": "太阳系基础知识",
            "question_count": 5,
            "excluded_questions": [mock_generate_result["questions"][0]["question"]],
        })

    assert resp.status_code == 502
    assert "不同的新题" in resp.json()["detail"]
