XP_PER_CORRECT = 10
XP_PER_QUIZ = 20

LEVEL_NAMES = [
    "知识新手",      # Lv.1
    "知识探索者",    # Lv.2
    "知识学徒",      # Lv.3
    "知识达人",      # Lv.4
    "知识精英",      # Lv.5
    "知识大师",      # Lv.6
    "知识王者",      # Lv.7
    "百科全书",      # Lv.8
    "智慧先知",      # Lv.9
    "传奇学者",      # Lv.10
]


def xp_for_level(level: int) -> int:
    return 50 * level * (level + 1)


def level_for_xp(xp: int) -> int:
    level = 1
    while xp >= xp_for_level(level):
        level += 1
    return level


def get_level_name(level: int) -> str:
    idx = level - 1
    if 0 <= idx < len(LEVEL_NAMES):
        return LEVEL_NAMES[idx]
    return f"知识大师 Lv.{level}"


def compute_xp_earned(correct_count: int, total_questions: int) -> int:
    return correct_count * XP_PER_CORRECT + total_questions * XP_PER_QUIZ


def compute_level_info(xp: int) -> dict:
    level = level_for_xp(xp)
    current_level_xp = xp_for_level(level - 1) if level > 1 else 0
    next_level_xp = xp_for_level(level)
    progress = (xp - current_level_xp) / (next_level_xp - current_level_xp) if next_level_xp > current_level_xp else 0.0
    return {
        "xp": xp,
        "level": level,
        "level_name": get_level_name(level),
        "current_level_xp": current_level_xp,
        "next_level_xp": next_level_xp,
        "progress": round(min(progress, 1.0), 4),
    }
