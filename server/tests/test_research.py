import pytest
from unittest.mock import patch, AsyncMock


@pytest.fixture
def mock_tavily_search_result():
    return {
        "results": [
            {"title": "Test Title", "url": "https://test.com", "content": "Test content about the topic."},
            {"title": "Another", "url": "https://test2.com", "content": "More content here."},
        ]
    }


@pytest.fixture
def mock_tavily_extract_result():
    return {
        "results": [{"url": "https://example.com", "raw_content": "Full page content here."}],
        "failed_results": [],
    }


@pytest.mark.asyncio
async def test_research_short_text_searches():
    from chains.research_chain import research_content

    with patch("chains.research_chain._tavily_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = "Search result content"

        r = await research_content("Harness Engineering", search_enabled=True)

        assert r.search_used is True
        assert "[联网研究参考内容]" in r.content
        assert "[用户输入]" in r.content
        assert "Harness Engineering" in r.content
        mock_search.assert_called_once_with("Harness Engineering")


@pytest.mark.asyncio
async def test_research_url_extracts():
    from chains.research_chain import research_content

    with patch("chains.research_chain._tavily_extract", new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = "Extracted content"

        r = await research_content("https://example.com/article", search_enabled=True)

        assert r.search_used is True
        assert "[联网研究参考内容]" in r.content
        mock_extract.assert_called_once_with("https://example.com/article")


@pytest.mark.asyncio
async def test_research_long_text_skips():
    from chains.research_chain import research_content

    long_text = "这是一段很长的知识内容。" * 500
    r = await research_content(long_text, search_enabled=True)

    assert r.search_used is False
    assert r.content == long_text


@pytest.mark.asyncio
async def test_research_disabled():
    from chains.research_chain import research_content

    r = await research_content("Harness Engineering", search_enabled=False)

    assert r.search_used is False
    assert r.content == "Harness Engineering"


@pytest.mark.asyncio
async def test_research_no_api_key():
    from chains.research_chain import research_content

    with patch("chains.research_chain.settings") as mock_settings:
        mock_settings.tavily_api_key = ""

        r = await research_content("Harness Engineering", search_enabled=True)

        assert r.search_used is False
        assert r.content == "Harness Engineering"


@pytest.mark.asyncio
async def test_research_search_failure_degrades():
    from chains.research_chain import research_content

    with patch("chains.research_chain._tavily_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ""

        r = await research_content("Harness Engineering", search_enabled=True)

        assert r.search_used is False
        assert r.content == "Harness Engineering"


@pytest.mark.asyncio
async def test_research_search_exception_degrades():
    from chains.research_chain import research_content

    with patch("chains.research_chain._tavily_search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = Exception("API error")

        r = await research_content("Harness Engineering", search_enabled=True)

        assert r.search_used is False
        assert r.content == "Harness Engineering"


@pytest.mark.asyncio
async def test_tavily_search_success():
    from chains.research_chain import _tavily_search

    mock_result = {
        "results": [
            {"title": "Test", "url": "https://test.com", "content": "Test content"},
            {"title": "Test2", "url": "https://test2.com", "content": "More content"},
        ]
    }

    with patch("langchain_tavily.TavilySearch") as MockSearch:
        MockSearch.return_value.invoke.return_value = mock_result
        result = await _tavily_search("test query")

        assert "Test content" in result
        assert "More content" in result


@pytest.mark.asyncio
async def test_tavily_search_empty():
    from chains.research_chain import _tavily_search

    with patch("langchain_tavily.TavilySearch") as MockSearch:
        MockSearch.return_value.invoke.return_value = {"results": []}
        result = await _tavily_search("nonexistent")

        assert result == ""


@pytest.mark.asyncio
async def test_tavily_search_exception():
    from chains.research_chain import _tavily_search

    with patch("langchain_tavily.TavilySearch", side_effect=Exception("API error")):
        result = await _tavily_search("test")

        assert result == ""


@pytest.mark.asyncio
async def test_tavily_extract_success():
    from chains.research_chain import _tavily_extract

    mock_result = {"results": [{"url": "https://example.com", "raw_content": "Full content"}]}

    with patch("langchain_tavily.TavilyExtract") as MockExtract:
        MockExtract.return_value.invoke.return_value = mock_result
        result = await _tavily_extract("https://example.com")

        assert "Full content" in result


@pytest.mark.asyncio
async def test_tavily_extract_exception():
    from chains.research_chain import _tavily_extract

    with patch("langchain_tavily.TavilyExtract", side_effect=Exception("API error")):
        result = await _tavily_extract("https://example.com")

        assert result == ""


def test_research_result_defaults():
    from chains.research_chain import ResearchResult

    r = ResearchResult(content="test")
    assert r.search_used is False
    assert r.needs_clarification is False
    assert r.domain_options == []


@pytest.mark.asyncio
async def test_generate_endpoint_search_used(client, mock_generate_result):
    from chains.research_chain import ResearchResult

    with patch("routers.generate.chain_generate") as mock_chain, \
         patch("routers.generate.research_content", new_callable=AsyncMock) as mock_research:
        mock_chain.ainvoke = AsyncMock(return_value=mock_generate_result)
        mock_research.return_value = ResearchResult(content="enriched", search_used=True)

        resp = await client.post("/api/generate", json={"content": "test", "question_count": 5})

    assert resp.status_code == 200
    assert resp.json()["search_used"] is True


@pytest.mark.asyncio
async def test_generate_endpoint_search_false(client, mock_generate_result):
    from chains.research_chain import ResearchResult

    with patch("routers.generate.chain_generate") as mock_chain, \
         patch("routers.generate.research_content", new_callable=AsyncMock) as mock_research:
        mock_chain.ainvoke = AsyncMock(return_value=mock_generate_result)
        mock_research.return_value = ResearchResult(content="original", search_used=False)

        resp = await client.post("/api/generate", json={"content": "test", "question_count": 5})

    assert resp.status_code == 200
    assert resp.json()["search_used"] is False


@pytest.mark.asyncio
async def test_generate_endpoint_clarification(client):
    from chains.research_chain import ResearchResult

    with patch("routers.generate.research_content", new_callable=AsyncMock) as mock_research:
        mock_research.return_value = ResearchResult(
            content="test", needs_clarification=True, domain_options=["Option A", "Option B"]
        )

        resp = await client.post("/api/generate", json={"content": "test", "question_count": 5})

    assert resp.status_code == 200
    data = resp.json()
    assert data["needs_clarification"] is True
    assert data["domain_options"] == ["Option A", "Option B"]
    assert data["questions"] == []
