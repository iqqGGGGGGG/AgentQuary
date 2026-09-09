import logging
from langchain_openai import OpenAIEmbeddings
from config import settings

logger = logging.getLogger(__name__)

_embeddings_instance: OpenAIEmbeddings | None = None


def get_embedding_model() -> OpenAIEmbeddings:
    global _embeddings_instance
    if _embeddings_instance is None:
        logger.info("Initializing embedding model: %s via %s",
                     settings.embedding_model, settings.embedding_base_url)
        _embeddings_instance = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_base=settings.embedding_base_url,
            openai_api_key=settings.embedding_api_key,
        )
    return _embeddings_instance
