import logging
import os
import re
import time
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models.orm import User, Document
from models.schemas import DocumentResponse, DocumentListResponse
from services.document_parser import parse_document, DocumentParseError
from services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def _sanitize_filename(filename: str) -> str:
    name = re.sub(r"[^\w\u4e00-\u9fff.\-]", "_", filename)
    return name[:200]


def _get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="请选择要上传的文件")

    ext = _get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}，支持: PDF、Word、TXT、MD")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过10MB")

    user_dir = UPLOAD_DIR / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    sanitized = _sanitize_filename(file.filename)
    stored_name = f"{int(time.time())}_{sanitized}"
    file_path = user_dir / stored_name

    file_path.write_bytes(content)

    try:
        text_content = parse_document(str(file_path), ext)
    except DocumentParseError as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        file_path.unlink(missing_ok=True)
        logger.exception("Document parse failed")
        raise HTTPException(status_code=500, detail="文档解析失败")

    doc = Document(
        user_id=user.id,
        filename=stored_name,
        original_filename=file.filename,
        file_type=ext,
        file_size=len(content),
        text_content=text_content,
        text_length=len(text_content),
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    logger.info("Document uploaded: user=%d, doc=%d, file=%s, chars=%d",
                user.id, doc.id, file.filename, doc.text_length)

    chunk_count = await VectorStoreService.add_document(user.id, doc.id, text_content)
    logger.info("Vectorized: user=%d, doc=%d, chunks=%d", user.id, doc.id, chunk_count)

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        text_length=doc.text_length,
        created_at=str(doc.created_at),
        text_preview=text_content[:200] if text_content else None,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document)
        .where(Document.user_id == user.id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    items = [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            original_filename=d.original_filename,
            file_type=d.file_type,
            file_size=d.file_size,
            text_length=d.text_length,
            created_at=str(d.created_at),
        )
        for d in docs
    ]

    return DocumentListResponse(items=items, total=len(items))


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        text_length=doc.text_length,
        created_at=str(doc.created_at),
        text_preview=doc.text_content[:500] if doc.text_content else None,
    )


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    file_path = UPLOAD_DIR / str(user.id) / doc.filename
    if file_path.exists():
        file_path.unlink()

    await VectorStoreService.delete_document(user.id, doc_id)
    await db.delete(doc)
    await db.commit()

    logger.info("Document deleted: user=%d, doc=%d", user.id, doc_id)

    return {"detail": "文档已删除"}


@router.get("/{doc_id}/text")
async def get_document_text(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    return {
        "id": doc.id,
        "original_filename": doc.original_filename,
        "text_content": doc.text_content or "",
        "text_length": doc.text_length,
    }


@router.delete("")
async def clear_documents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.user_id == user.id)
    )
    docs = result.scalars().all()

    for doc in docs:
        file_path = UPLOAD_DIR / str(user.id) / doc.filename
        if file_path.exists():
            file_path.unlink()
        await db.delete(doc)

    await VectorStoreService.clear_user(user.id)
    await db.commit()

    logger.info("All documents cleared: user=%d, count=%d", user.id, len(docs))

    return {"detail": f"已清空 {len(docs)} 个文档"}
