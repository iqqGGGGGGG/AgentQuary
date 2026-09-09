import logging
import re
from dataclasses import dataclass, field

from config import settings

logger = logging.getLogger(__name__)

MAX_CONTENT_CHARS = 12_000
SEARCH_THRESHOLD = 2000
URL_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)


@dataclass
class ResearchResult:
    content: str
    search_used: bool = False
    needs_clarification: bool = False
    domain_options: list[str] = field(default_factory=list)


async def _tavily_search(query: str) -> str:
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

        logger.debug("TavilySearch returned %d results, total_chars=%d",
                      len(parts), sum(len(p) for p in parts))
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning("TavilySearch failed: %s", e)
        return ""


async def _tavily_extract(url: str) -> str:
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

        logger.debug("TavilyExtract returned %d results, total_chars=%d",
                      len(parts), sum(len(p) for p in parts))
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning("TavilyExtract failed: %s", e)
        return ""


async def research_content(content: str, search_enabled: bool = True) -> ResearchResult:
    if not search_enabled or not settings.tavily_api_key:
        logger.debug("Research skipped: search_enabled=%s, tavily_api_key_set=%s",
                      search_enabled, bool(settings.tavily_api_key))
        return ResearchResult(content=content)

    clean = content.strip()

    if URL_PATTERN.fullmatch(clean):
        logger.debug("URL input detected, extracting: %s", clean[:80])
        gathered = await _tavily_extract(clean)
        if gathered:
            enriched = f"[联网研究参考内容]\n{gathered}"[:MAX_CONTENT_CHARS]
            enriched += f"\n\n[用户输入]\n{clean}"
            logger.debug("Research complete (URL): enriched_length=%d", len(enriched))
            return ResearchResult(content=enriched, search_used=True)
        logger.debug("TavilyExtract returned empty, falling back")
        return ResearchResult(content=content)

    if len(clean) > SEARCH_THRESHOLD:
        logger.debug("Research skipped: content_length=%d > %d", len(clean), SEARCH_THRESHOLD)
        return ResearchResult(content=content)

    try:
        logger.debug("Searching for: '%s'", clean[:80])
        gathered = await _tavily_search(clean)

        if not gathered:
            logger.debug("TavilySearch returned empty, falling back to original content")
            return ResearchResult(content=content)

        enriched = f"[联网研究参考内容]\n{gathered}"[:MAX_CONTENT_CHARS]
        enriched += f"\n\n[用户输入]\n{clean}"

        logger.debug("Research complete: enriched_length=%d", len(enriched))
        return ResearchResult(content=enriched, search_used=True)

    except Exception as e:
        logger.warning("Research phase failed, falling back to original content: %s", e)
        return ResearchResult(content=content)
