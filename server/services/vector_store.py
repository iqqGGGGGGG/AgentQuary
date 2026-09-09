import logging
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings
from services.embedding import get_embedding_model

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", "。", ".", "！", "!", "？", "?", "；", ";", " "],
)


def _get_collection_name(user_id: int) -> str:
    return f"user_{user_id}"


def _get_vector_store(user_id: int) -> Chroma:
    return Chroma(
        collection_name=_get_collection_name(user_id),
        embedding_function=get_embedding_model(),
        persist_directory=settings.chroma_persist_dir,
    )


class VectorStoreService:
    @staticmethod
    async def add_document(user_id: int, doc_id: int, text: str) -> int:
        try:
            chunks = _text_splitter.split_text(text)
            if not chunks:
                logger.warning("No chunks generated for doc %d", doc_id)
                return 0

            metadatas = [
                {"doc_id": doc_id, "chunk_index": i, "user_id": user_id}
                for i in range(len(chunks))
            ]
            ids = [f"user_{user_id}_doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]

            store = _get_vector_store(user_id)
            store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)

            logger.info("Added %d chunks for user=%d, doc=%d", len(chunks), user_id, doc_id)
            return len(chunks)
        except Exception as e:
            logger.error("Failed to add document to vector store: %s", e)
            return 0

    @staticmethod
    async def search(user_id: int, query: str, k: int = 5) -> list[str]:
        try:
            store = _get_vector_store(user_id)
            results = store.similarity_search(query, k=k)
            texts = [doc.page_content for doc in results]
            logger.debug("Vector search for user=%d, query='%s': found %d results",
                         user_id, query[:50], len(texts))
            return texts
        except Exception as e:
            logger.warning("Vector search failed for user=%d: %s", user_id, e)
            return []

    @staticmethod
    async def delete_document(user_id: int, doc_id: int) -> bool:
        try:
            store = _get_vector_store(user_id)
            collection = store._collection
            collection.delete(where={"doc_id": doc_id})
            logger.info("Deleted vectors for user=%d, doc=%d", user_id, doc_id)
            return True
        except Exception as e:
            logger.error("Failed to delete vectors for user=%d, doc=%d: %s", user_id, doc_id, e)
            return False

    @staticmethod
    async def clear_user(user_id: int) -> bool:
        try:
            store = _get_vector_store(user_id)
            collection = store._collection
            collection.delete(where={"user_id": user_id})
            logger.info("Cleared all vectors for user=%d", user_id)
            return True
        except Exception as e:
            logger.error("Failed to clear vectors for user=%d: %s", user_id, e)
            return False
