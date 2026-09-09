import json
import base64
import binascii
import logging
import uuid
from datetime import datetime, timedelta, timezone, date as date_type
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth import get_current_user
from models.orm import User, LearningRecord, Achievement, UserAchievement
from models.schemas import (
    Question,
    GenerateResponse,
    UserProfileResponse,
    UserProfileUpdate,
    AvatarUploadRequest,
    UserStatsResponse,
    HistorySaveRequest,
    HistoryItemResponse,
    HistoryListResponse,
    LevelInfoResponse,
    LearningCalendarResponse,
    CalendarDay,
    AchievementResponse,
    AchievementListResponse,
    WrongQuestionItem,
    WrongQuestionListResponse,
    TrendsResponse,
    TrendDay,
    DomainsResponse,
    DomainStat,
    PreferencesUpdate,
    PreferencesResponse,
    GoalUpdate,
    GoalResponse,
    HistorySaveResponse,
)
from services.level import compute_xp_earned, compute_level_info
from services.achievements import check_achievements
from services.domains import compute_domains

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["user"])
AVATAR_DIR = Path(__file__).resolve().parents[1] / "uploads" / "avatars"
MAX_AVATAR_BYTES = 2 * 1024 * 1024


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


def _detect_avatar_extension(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


@router.post("/profile/avatar", response_model=UserProfileResponse)
async def upload_avatar(
    body: AvatarUploadRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        image_data = base64.b64decode(body.data, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="头像数据格式无效") from None

    if len(image_data) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=413, detail="头像不能超过 2MB")
    extension = _detect_avatar_extension(image_data)
    if extension is None:
        raise HTTPException(status_code=400, detail="仅支持 PNG、JPEG 或 WebP 头像")

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{user.id}-{uuid.uuid4().hex}.{extension}"
    (AVATAR_DIR / filename).write_bytes(image_data)
    user.avatar_url = str(request.url_for("uploads", path=f"avatars/{filename}"))
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


@router.post("/history", response_model=HistorySaveResponse)
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

    xp_earned = compute_xp_earned(body.correct_count, body.total_questions)
    old_level = user.level
    user.xp = (user.xp or 0) + xp_earned
    level_info = compute_level_info(user.xp)
    user.level = level_info["level"]
    new_level = user.level if user.level != old_level else None
    await db.commit()

    new_achievements = []
    try:
        new_achievements = await check_achievements(db, user, record)
    except Exception:
        logger.exception("成就检测失败")

    return HistorySaveResponse(
        id=record.id,
        session_id=record.session_id,
        topic=record.topic,
        accuracy=record.accuracy,
        total_questions=record.total_questions,
        correct_count=record.correct_count,
        duration_seconds=record.duration_seconds,
        summary=record.summary,
        created_at=record.created_at.isoformat() if record.created_at else "",
        xp_earned=xp_earned,
        new_level=new_level,
        new_achievements=[
            AchievementResponse(
                id=a.id, key=a.key, name=a.name, description=a.description,
                icon=a.icon, condition_type=a.condition_type,
                condition_value=a.condition_value, sort_order=a.sort_order,
                unlocked=True, unlocked_at="",
            )
            for a in new_achievements
        ],
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


# ── Level ──

@router.get("/level", response_model=LevelInfoResponse)
async def get_level(user: User = Depends(get_current_user)):
    return LevelInfoResponse(**compute_level_info(user.xp or 0))


# ── Learning Calendar ──

@router.get("/learning-calendar", response_model=LearningCalendarResponse)
async def get_learning_calendar(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = date_type(year, month, 1)
    if month == 12:
        end = date_type(year + 1, 1, 1)
    else:
        end = date_type(year, month + 1, 1)

    result = await db.execute(
        select(
            func.date(LearningRecord.created_at).label("day"),
            func.count(LearningRecord.id).label("cnt"),
        )
        .where(
            LearningRecord.user_id == user.id,
            LearningRecord.created_at >= datetime.combine(start, datetime.min.time()),
            LearningRecord.created_at < datetime.combine(end, datetime.min.time()),
        )
        .group_by(func.date(LearningRecord.created_at))
    )
    day_counts = {str(row.day): row.cnt for row in result.all()}

    all_records = await db.execute(
        select(func.date(LearningRecord.created_at))
        .where(LearningRecord.user_id == user.id)
        .distinct()
        .order_by(func.date(LearningRecord.created_at).desc())
    )
    all_dates = [str(row[0]) for row in all_records.all()]

    streak = 0
    today = date_type.today()
    check = today
    date_set = set(all_dates)
    while check.isoformat() in date_set:
        streak += 1
        check -= timedelta(days=1)

    days = []
    current = start
    while current < end:
        ds = current.isoformat()
        count = day_counts.get(ds, 0)
        days.append(CalendarDay(date=ds, count=count, high=count >= 3))
        current += timedelta(days=1)

    return LearningCalendarResponse(year=year, month=month, days=days, current_streak=streak)


# ── Achievements ──

@router.get("/achievements", response_model=AchievementListResponse)
async def get_achievements(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Achievement).order_by(Achievement.sort_order))
    all_achievements = result.scalars().all()

    ua_result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user.id)
    )
    ua_map = {ua.achievement_id: ua for ua in ua_result.scalars().all()}

    items = []
    for ach in all_achievements:
        ua = ua_map.get(ach.id)
        items.append(AchievementResponse(
            id=ach.id, key=ach.key, name=ach.name, description=ach.description,
            icon=ach.icon, condition_type=ach.condition_type,
            condition_value=ach.condition_value, sort_order=ach.sort_order,
            unlocked=ua is not None,
            unlocked_at=ua.unlocked_at.isoformat() if ua and ua.unlocked_at else None,
        ))

    return AchievementListResponse(
        items=items,
        unlocked_count=len(ua_map),
        total_count=len(all_achievements),
    )


# ── Wrong Questions ──

@router.get("/wrong-questions", response_model=WrongQuestionListResponse)
async def get_wrong_questions(
    limit: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LearningRecord)
        .where(LearningRecord.user_id == user.id)
        .order_by(LearningRecord.created_at.desc())
        .limit(100)
    )
    records = result.scalars().all()

    items: list[WrongQuestionItem] = []
    topics: set[str] = set()

    for rec in records:
        if not rec.questions_json or not rec.user_answers_json:
            continue
        try:
            questions = json.loads(rec.questions_json)
            answers = json.loads(rec.user_answers_json)
        except json.JSONDecodeError:
            continue

        answer_map = {}
        for ans in answers:
            qid = ans.get("question_id") if isinstance(ans, dict) else None
            sel = ans.get("selected") if isinstance(ans, dict) else None
            if qid is not None:
                answer_map[qid] = sel

        for q in questions:
            qid = q.get("id")
            correct = q.get("answer")
            selected = answer_map.get(qid)
            if selected is None or selected == correct:
                continue

            options = q.get("options", [])
            your_ans = options[selected] if 0 <= selected < len(options) else str(selected)
            correct_ans = options[correct] if 0 <= correct < len(options) else str(correct)

            topics.add(rec.topic)
            items.append(WrongQuestionItem(
                record_id=rec.id,
                question_id=qid,
                topic=rec.topic,
                question=q.get("question", ""),
                your_answer=your_ans,
                correct_answer=correct_ans,
                explanation=q.get("explanation", ""),
                created_at=rec.created_at.isoformat() if rec.created_at else "",
            ))

            if len(items) >= limit:
                break
        if len(items) >= limit:
            break

    return WrongQuestionListResponse(items=items, total=len(items), topic_count=len(topics))


@router.get("/wrong-questions/quiz", response_model=GenerateResponse)
async def get_wrong_questions_quiz(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    question_id: int | None = Query(default=None),
):
    result = await db.execute(
        select(LearningRecord)
        .where(LearningRecord.user_id == user.id)
        .order_by(LearningRecord.created_at.desc())
        .limit(100)
    )
    records = result.scalars().all()

    questions: list[dict] = []
    seen_ids: set[int] = set()

    for rec in records:
        if not rec.questions_json or not rec.user_answers_json:
            continue
        try:
            qs = json.loads(rec.questions_json)
            answers = json.loads(rec.user_answers_json)
        except json.JSONDecodeError:
            continue

        answer_map: dict[int, int] = {}
        for ans in answers:
            qid = ans.get("question_id") if isinstance(ans, dict) else None
            sel = ans.get("selected") if isinstance(ans, dict) else None
            if qid is not None and sel is not None:
                answer_map[qid] = sel

        for q in qs:
            qid = q.get("id")
            correct = q.get("answer")
            selected = answer_map.get(qid)
            if selected is None or selected == correct:
                continue
            if question_id is not None and qid != question_id:
                continue
            if qid in seen_ids:
                continue
            seen_ids.add(qid)
            questions.append({
                "id": qid,
                "type": q.get("type", "single_choice"),
                "question": q.get("question", ""),
                "options": q.get("options", []),
                "answer": correct,
                "explanation": q.get("explanation", ""),
            })
            if question_id is not None or len(questions) >= 20:
                break
        if question_id is not None and questions:
            break
        if len(questions) >= 20:
            break

    return GenerateResponse(
        session_id=f"wrong-{uuid.uuid4().hex[:12]}",
        topic="错题练习",
        questions=[Question(**q) for q in questions],
    )


@router.delete("/wrong-questions/{record_id}/{question_id}")
async def remove_wrong_question(
    record_id: int,
    question_id: int,
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

    if record.user_answers_json:
        try:
            answers = json.loads(record.user_answers_json)
            for ans in answers:
                if isinstance(ans, dict) and ans.get("question_id") == question_id:
                    ans["removed"] = True
            record.user_answers_json = json.dumps(answers, ensure_ascii=False)
            await db.commit()
        except json.JSONDecodeError:
            pass

    return {"detail": "已移除"}


# ── Trends ──

@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    days: int = Query(default=7, ge=1, le=90),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date_type.today()
    start = today - timedelta(days=days - 1)

    result = await db.execute(
        select(
            func.date(LearningRecord.created_at).label("day"),
            func.count(LearningRecord.id).label("cnt"),
            func.coalesce(func.avg(LearningRecord.accuracy), 0.0).label("acc"),
        )
        .where(
            LearningRecord.user_id == user.id,
            LearningRecord.created_at >= datetime.combine(start, datetime.min.time()),
        )
        .group_by(func.date(LearningRecord.created_at))
    )
    day_data = {str(row.day): (row.cnt, float(row.acc)) for row in result.all()}

    trend_days = []
    current = start
    while current <= today:
        ds = current.isoformat()
        count, acc = day_data.get(ds, (0, 0.0))
        trend_days.append(TrendDay(date=ds, count=count, accuracy=round(acc, 4)))
        current += timedelta(days=1)

    return TrendsResponse(days=trend_days)


# ── Domains ──

@router.get("/domains", response_model=DomainsResponse)
async def get_domains(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    domains = await compute_domains(db, user.id)
    return DomainsResponse(domains=[DomainStat(**d) for d in domains])


# ── Preferences ──

@router.get("/preferences", response_model=PreferencesResponse)
async def get_preferences(user: User = Depends(get_current_user)):
    prefs = []
    if user.preferences_json:
        try:
            prefs = json.loads(user.preferences_json)
        except json.JSONDecodeError:
            pass
    return PreferencesResponse(preferences=prefs)


@router.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(
    body: PreferencesUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user.preferences_json = json.dumps(body.preferences, ensure_ascii=False)
    await db.commit()
    return PreferencesResponse(preferences=body.preferences)


# ── Goal ──

@router.get("/goal", response_model=GoalResponse)
async def get_goal(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date_type.today()
    result = await db.execute(
        select(func.count(LearningRecord.id)).where(
            LearningRecord.user_id == user.id,
            LearningRecord.created_at >= datetime.combine(today, datetime.min.time()),
        )
    )
    today_count = result.scalar() or 0
    return GoalResponse(daily_goal=user.daily_goal or 3, today_count=today_count)


@router.put("/goal", response_model=GoalResponse)
async def update_goal(
    body: GoalUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user.daily_goal = body.daily_goal
    await db.commit()

    today = date_type.today()
    result = await db.execute(
        select(func.count(LearningRecord.id)).where(
            LearningRecord.user_id == user.id,
            LearningRecord.created_at >= datetime.combine(today, datetime.min.time()),
        )
    )
    today_count = result.scalar() or 0
    return GoalResponse(daily_goal=user.daily_goal, today_count=today_count)
