from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm import User, Achievement, UserAchievement, LearningRecord

logger = logging.getLogger(__name__)

ACHIEVEMENT_SEEDS = [
    {"key": "first_quiz", "name": "初试牛刀", "description": "完成第一次闯关", "icon": "🎯", "condition_type": "total_quizzes", "condition_value": 1, "sort_order": 1},
    {"key": "streak_3", "name": "连续三天", "description": "连续学习3天", "icon": "🔥", "condition_type": "learning_streak", "condition_value": 3, "sort_order": 2},
    {"key": "topics_5", "name": "博学多才", "description": "学习5个不同主题", "icon": "📚", "condition_type": "unique_topics", "condition_value": 5, "sort_order": 3},
    {"key": "perfect_score", "name": "满分达人", "description": "单次闯关正确率100%", "icon": "🏆", "condition_type": "perfect_score", "condition_value": 1, "sort_order": 4},
    {"key": "correct_100", "name": "知识大师", "description": "累计答对100题", "icon": "⭐", "condition_type": "total_correct", "condition_value": 100, "sort_order": 5},
    {"key": "streak_7", "name": "七日坚持", "description": "连续学习7天", "icon": "💎", "condition_type": "learning_streak", "condition_value": 7, "sort_order": 6},
    {"key": "speed_demon", "name": "速度之王", "description": "2分钟内完成10题", "icon": "🌟", "condition_type": "speed_run", "condition_value": 120, "sort_order": 7},
    {"key": "all_domains", "name": "全面发展", "description": "所有领域正确率超60%", "icon": "🎓", "condition_type": "all_domains_60", "condition_value": 1, "sort_order": 8},
    {"key": "level_10", "name": "知识王者", "description": "达到Lv.10", "icon": "👑", "condition_type": "level", "condition_value": 10, "sort_order": 9},
    {"key": "quizzes_50", "name": "闯关达人", "description": "完成50次闯关", "icon": "🏅", "condition_type": "total_quizzes", "condition_value": 50, "sort_order": 10},
]


async def seed_achievements(db: AsyncSession) -> None:
    for seed in ACHIEVEMENT_SEEDS:
        result = await db.execute(select(Achievement).where(Achievement.key == seed["key"]))
        if result.scalar_one_or_none() is None:
            db.add(Achievement(**seed))
    await db.commit()


async def check_achievements(db: AsyncSession, user: User, record: LearningRecord) -> list[Achievement]:
    result = await db.execute(select(Achievement))
    all_achievements = result.scalars().all()

    ua_result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    )
    unlocked_ids = {row[0] for row in ua_result.all()}

    newly_unlocked: list[Achievement] = []

    for ach in all_achievements:
        if ach.id in unlocked_ids:
            continue
        if await _check_condition(db, user, record, ach):
            ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
            db.add(ua)
            newly_unlocked.append(ach)

    if newly_unlocked:
        await db.commit()
        for ach in newly_unlocked:
            await db.refresh(ach)

    return newly_unlocked


async def _check_condition(db: AsyncSession, user: User, record: LearningRecord, ach: Achievement) -> bool:
    ct = ach.condition_type
    cv = ach.condition_value

    if ct == "total_quizzes":
        count_result = await db.execute(
            select(func.count(LearningRecord.id)).where(LearningRecord.user_id == user.id)
        )
        return (count_result.scalar() or 0) >= cv

    if ct == "total_correct":
        sum_result = await db.execute(
            select(func.coalesce(func.sum(LearningRecord.correct_count), 0)).where(LearningRecord.user_id == user.id)
        )
        return int(sum_result.scalar() or 0) >= cv

    if ct == "unique_topics":
        topic_result = await db.execute(
            select(func.count(func.distinct(LearningRecord.topic))).where(LearningRecord.user_id == user.id)
        )
        return (topic_result.scalar() or 0) >= cv

    if ct == "perfect_score":
        return record.accuracy >= 1.0

    if ct == "learning_streak":
        return await _compute_learning_streak(db, user.id) >= cv

    if ct == "speed_run":
        return record.duration_seconds <= cv and record.total_questions >= 10

    if ct == "level":
        return user.level >= cv

    if ct == "all_domains_60":
        from services.domains import compute_domains
        domains = await compute_domains(db, user.id)
        real_domains = [d for d in domains if d["domain"] != "其他"]
        if len(real_domains) < 3:
            return False
        return all(d["accuracy"] >= 0.6 for d in real_domains)

    return False


async def _compute_learning_streak(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.date(LearningRecord.created_at))
        .where(LearningRecord.user_id == user_id)
        .distinct()
        .order_by(func.date(LearningRecord.created_at).desc())
    )
    dates = [row[0] for row in result.all()]
    if not dates:
        return 0

    streak = 1
    for i in range(len(dates) - 1):
        d1 = dates[i] if isinstance(dates[i], datetime) else datetime.strptime(str(dates[i]), "%Y-%m-%d")
        d2 = dates[i + 1] if isinstance(dates[i + 1], datetime) else datetime.strptime(str(dates[i + 1]), "%Y-%m-%d")
        if (d1 - d2).days == 1:
            streak += 1
        else:
            break
    return streak
