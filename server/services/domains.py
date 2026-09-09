from __future__ import annotations

import json
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm import LearningRecord

logger = logging.getLogger(__name__)

DOMAIN_KEYWORDS = {
    "历史": {"icon": "📖", "keywords": ["历史", "朝代", "皇帝", "战争", "三国", "秦", "汉", "唐", "宋", "明", "清", "古代", "王朝", "战役"]},
    "科学": {"icon": "🔬", "keywords": ["科学", "物理", "化学", "生物", "天文", "行星", "太阳", "宇宙", "原子", "分子", "细胞", "基因"]},
    "心理": {"icon": "🧠", "keywords": ["心理", "效应", "认知", "情绪", "行为", "思维", "偏见", "潜意识", "动机"]},
    "数学": {"icon": "📐", "keywords": ["数学", "几何", "代数", "概率", "统计", "方程", "函数", "微积分"]},
    "地理": {"icon": "🌍", "keywords": ["地理", "国家", "城市", "河流", "山脉", "气候", "大陆", "海洋"]},
    "文学": {"icon": "📖", "keywords": ["文学", "小说", "诗歌", "散文", "作家", "诗人", "名著", "红楼梦", "西游记"]},
    "科技": {"icon": "💻", "keywords": ["科技", "计算机", "互联网", "人工智能", "编程", "软件", "算法", "数据"]},
    "生活": {"icon": "☕", "keywords": ["生活", "美食", "健康", "运动", "旅行", "咖啡", "茶", "养生", "睡眠"]},
    "艺术": {"icon": "🎨", "keywords": ["艺术", "绘画", "音乐", "雕塑", "建筑", "摄影", "设计", "美学"]},
}


def classify_topic(topic: str) -> str:
    topic_lower = topic.lower()
    for domain, info in DOMAIN_KEYWORDS.items():
        for kw in info["keywords"]:
            if kw in topic_lower:
                return domain
    return "其他"


async def compute_domains(db: AsyncSession, user_id: int) -> list[dict]:
    result = await db.execute(
        select(LearningRecord.topic, LearningRecord.accuracy, LearningRecord.correct_count, LearningRecord.total_questions)
        .where(LearningRecord.user_id == user_id)
    )
    rows = result.all()

    domain_data: dict[str, dict] = {}
    for topic, accuracy, correct, total in rows:
        domain = classify_topic(topic)
        if domain not in domain_data:
            domain_data[domain] = {"correct": 0, "total": 0}
        domain_data[domain]["correct"] += correct or 0
        domain_data[domain]["total"] += total or 0

    domains = []
    for domain, data in domain_data.items():
        acc = data["correct"] / data["total"] if data["total"] > 0 else 0.0
        icon = DOMAIN_KEYWORDS.get(domain, {}).get("icon", "📌")
        domains.append({"domain": domain, "icon": icon, "accuracy": round(acc, 4), "count": data["total"]})

    domains.sort(key=lambda d: d["accuracy"], reverse=True)
    return domains
