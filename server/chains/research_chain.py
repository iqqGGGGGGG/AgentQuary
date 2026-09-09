import logging
from dataclasses import dataclass, field

from chains.rag_agent import rag_research, RAGResult

logger = logging.getLogger(__name__)


@dataclass
class ResearchResult:
    content: str
    search_used: bool = False
    needs_clarification: bool = False
    domain_options: list[str] = field(default_factory=list)


async def research_content(content: str, user_id: int | None = None, search_enabled: bool = True) -> ResearchResult:
    try:
        rag = await rag_research(content, user_id=user_id, search_enabled=search_enabled)
        return ResearchResult(
            content=rag.content,
            search_used=rag.vector_used or rag.web_used,
            needs_clarification=rag.needs_clarification,
            domain_options=rag.domain_options,
        )
    except Exception as e:
        logger.warning("Research failed, falling back to original content: %s", e)
        return ResearchResult(content=content)
