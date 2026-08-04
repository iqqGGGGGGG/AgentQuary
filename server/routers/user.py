import json
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth import get_current_user
from models.orm import User, LearningRecord
from models.schemas import (
    UserProfileResponse,
    UserProfileUpdate,
    UserStatsResponse,
    HistorySaveRequest,
    HistoryItemResponse,
    HistoryListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return UserProfileResponse(
        openid=user.openid,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    body: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.nickname is not None:
        user.nickname = body.nickname
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url
    await db.commit()
    await db.refresh(user)
    return UserProfileResponse(
        openid=user.openid,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.get("/stats", response_model=UserStatsResponse)
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            func.count(LearningRecord.id),
            func.coalesce(func.sum(LearningRecord.total_questions), 0),
            func.coalesce(func.avg(LearningRecord.accuracy), 0.0),
        ).where(LearningRecord.user_id == user.id)
    )
    row = result.one()
    total_quizzes = row[0] or 0
    total_questions = row[1] or 0
    avg_accuracy = float(row[2] or 0.0)

    day_result = await db.execute(
        select(func.count(func.distinct(func.date(LearningRecord.created_at)))).where(
            LearningRecord.user_id == user.id
        )
    )
    learning_days = day_result.scalar() or 0

    streak_result = await db.execute(
        select(LearningRecord.correct_count, LearningRecord.total_questions)
        .where(LearningRecord.user_id == user.id)
        .order_by(LearningRecord.accuracy.desc())
        .limit(1)
    )
    streak_row = streak_result.first()
    best_streak = streak_row[0] if streak_row else 0

    return UserStatsResponse(
        total_quizzes=total_quizzes,
        total_questions=int(total_questions),
        avg_accuracy=round(avg_accuracy, 4),
        best_streak=best_streak,
        learning_days=learning_days,
    )


@router.post("/history", response_model=HistoryItemResponse)
async def save_history(
    body: HistorySaveRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(LearningRecord).where(LearningRecord.session_id == body.session_id)
    )
    record = existing.scalar_one_or_none()

    if record:
        record.topic = body.topic
        record.accuracy = body.accuracy
        record.total_questions = body.total_questions
        record.correct_count = body.correct_count
        record.duration_seconds = body.duration_seconds
        record.summary = body.summary
        if body.questions is not None:
            record.questions_json = json.dumps(body.questions, ensure_ascii=False)
        if body.user_answers is not None:
            record.user_answers_json = json.dumps(body.user_answers, ensure_ascii=False)
    else:
        record = LearningRecord(
            user_id=user.id,
            session_id=body.session_id,
            topic=body.topic,
            accuracy=body.accuracy,
            total_questions=body.total_questions,
            correct_count=body.correct_count,
            duration_seconds=body.duration_seconds,
            questions_json=json.dumps(body.questions, ensure_ascii=False) if body.questions else None,
            user_answers_json=json.dumps(body.user_answers, ensure_ascii=False) if body.user_answers else None,
            summary=body.summary,
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)

    return HistoryItemResponse(
        id=record.id,
        session_id=record.session_id,
        topic=record.topic,
        accuracy=record.accuracy,
        total_questions=record.total_questions,
        correct_count=record.correct_count,
        duration_seconds=record.duration_seconds,
        summary=record.summary,
        created_at=record.created_at.isoformat() if record.created_at else "",
    )


@router.get("/history", response_model=HistoryListResponse)
async def list_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LearningRecord)
        .where(LearningRecord.user_id == user.id)
        .order_by(LearningRecord.created_at.desc())
        .limit(50)
    )
    records = result.scalars().all()
    items = [
        HistoryItemResponse(
            id=r.id,
            session_id=r.session_id,
            topic=r.topic,
            accuracy=r.accuracy,
            total_questions=r.total_questions,
            correct_count=r.correct_count,
            duration_seconds=r.duration_seconds,
            summary=r.summary,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in records
    ]
    return HistoryListResponse(items=items, total=len(items))


@router.delete("/history/{record_id}")
async def delete_history(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LearningRecord).where(
            LearningRecord.id == record_id,
            LearningRecord.user_id == user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    await db.delete(record)
    await db.commit()
    return {"detail": "已删除"}
