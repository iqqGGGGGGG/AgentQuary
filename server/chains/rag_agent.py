import logging
import re
from dataclasses import dataclass, field

from config import settings
from services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

MAX_CONTENT_CHARS = 12_000
SEARCH_THRESHOLD = 2000
URL_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)


@dataclass
class RAGResult:
    content: str
    vector_used: bool = False
    web_used: bool = False
    needs_clarification: bool = False
    domain_options: list[str] = field(default_factory=list)


async def _web_search(query: str) -> str:
    try:
        from langchain_tavily import TavilySearch

        tool = TavilySearch(max_results=10, include_raw_content=False, include_answer=False, tavily_api_key=settings.tavily_api_key)
        logger.debug("TavilySearch query='%s'", query)
        result = tool.invoke({"query": query, "search_depth": "advanced"})

        parts: list[str] = []
        for item in result.get("results", []):
            title = item.get("title", "")
            content = item.get("content", "")
            url = item.get("url", "")
            if content:
                parts.append(f"【{title}】({url})\n{content}")

        logger.debug("TavilySearch returned %d results", len(parts))
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning("TavilySearch failed: %s", e)
        return ""


async def _web_extract(url: str) -> str:
    try:
        from langchain_tavily import TavilyExtract

        tool = TavilyExtract(tavily_api_key=settings.tavily_api_key)
        logger.debug("TavilyExtract url='%s'", url)
        result = tool.invoke({"urls": [url]})

        parts: list[str] = []
        for item in result.get("results", []):
            raw = item.get("raw_content", "")
            if raw:
                parts.append(raw)

        logger.debug("TavilyExtract returned %d results", len(parts))
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning("TavilyExtract failed: %s", e)
        return ""


async def rag_research(content: str, user_id: int | None = None, search_enabled: bool = True) -> RAGResult:
    clean = content.strip()

    if URL_PATTERN.fullmatch(clean):
        logger.debug("URL input detected, extracting: %s", clean[:80])
        gathered = await _web_extract(clean)
        if gathered:
            enriched = f"[联网研究参考内容]\n{gathered}"[:MAX_CONTENT_CHARS]
            enriched += f"\n\n[用户输入]\n{clean}"
            return RAGResult(content=enriched, web_used=True)
        return RAGResult(content=content)

    vector_results: list[str] = []
    if user_id and settings.embedding_api_key:
        try:
            vector_results = await VectorStoreService.search(user_id, clean, k=5)
            logger.debug("Vector search returned %d results", len(vector_results))
        except Exception as e:
            logger.warning("Vector search failed: %s", e)

    web_results = ""
    if search_enabled and settings.tavily_api_key and len(clean) <= SEARCH_THRESHOLD:
        try:
            web_results = await _web_search(clean)
        except Exception as e:
            logger.warning("Web search failed: %s", e)

    parts: list[str] = []

    if vector_results:
        vector_text = "\n\n---\n\n".join(vector_results)
        parts.append(f"[本地知识库参考内容]\n{vector_text}")

    if web_results:
        parts.append(f"[联网研究参考内容]\n{web_results}")

    if not parts:
        logger.debug("No research results, returning original content")
        return RAGResult(content=content)

    enriched = "\n\n".join(parts)
    enriched = enriched[:MAX_CONTENT_CHARS]
    enriched += f"\n\n[用户输入]\n{clean}"

    return RAGResult(
        content=enriched,
        vector_used=bool(vector_results),
        web_used=bool(web_results),
    )
