import logging
from fastapi import APIRouter
from models.schemas import ReportRequest, ReportResponse
from chains.report_chain import chain_report, parser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["report"])


def compute_stats(questions: list[dict], user_answers: list[int]):
    total = len(questions)
    correct = 0
    mastered = []
    weak = []
    correct_list = []
    wrong_list = []

    for i, q in enumerate(questions):
        user_ans = user_answers[i] if i < len(user_answers) else -1
        correct_ans = q.get("answer", 0)
        is_correct = user_ans == correct_ans

        if is_correct:
            correct += 1
            mastered.append(q.get("question", ""))
            correct_list.append(q.get("question", ""))
        else:
            weak.append(q.get("question", ""))
            user_opt = q.get("options", [])[user_ans] if 0 <= user_ans < len(q.get("options", [])) else "跳过"
            correct_opt = q.get("options", [])[correct_ans] if 0 <= correct_ans < len(q.get("options", [])) else "未知"
            wrong_list.append(f"题目：{q.get('question', '')}，用户选：{user_opt}，正确答案：{correct_opt}")

    accuracy = correct / total if total > 0 else 0
    return accuracy, correct, total, mastered, weak, correct_list, wrong_list


@router.post("/report", response_model=ReportResponse)
async def generate_report(req: ReportRequest):
    accuracy, correct, total, mastered, weak, correct_list, wrong_list = compute_stats(
        req.questions, req.user_answers
    )

    default_summary = f"本次学习「{req.topic}」，共 {total} 题答对 {correct} 题，正确率 {int(accuracy * 100)}%。"
    default_encouragement = "继续加油！"

    try:
        ai_result = await chain_report.ainvoke({
            "topic": req.topic,
            "accuracy": int(accuracy * 100),
            "total": total,
            "correct": correct,
            "correct_list": "\n".join(correct_list) if correct_list else "无",
            "wrong_list": "\n".join(wrong_list) if wrong_list else "无",
            "format_instructions": parser.get_format_instructions(),
        })
        summary = ai_result.get("summary", default_summary)
        encouragement = ai_result.get("encouragement", default_encouragement)
    except Exception as e:
        logger.warning("Report chain failed, using defaults: %s", e)
        summary = default_summary
        encouragement = default_encouragement

    return ReportResponse(
        accuracy=accuracy,
        correct_count=correct,
        total_count=total,
        mastered=mastered,
        weak=weak,
        summary=summary,
        encouragement=encouragement,
    )
