import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from auth import get_current_user
from database import get_db
from models.orm import User
from models.schemas import GenerateRequest, GenerateResponse
from chains.generate_chain import chain_generate, parser
from chains.research_chain import research_content
from services.content import ContentInputError, normalize_content
from services.image_gen import generate_images_batch

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["generate"])


def _question_key(value: str) -> str:
    return "".join(value.casefold().split())


@router.post("/generate", response_model=GenerateResponse)
async def generate_quiz(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user_id = None
        content = await normalize_content(req.content)
        research = await research_content(content, user_id=user_id)
        logger.debug("After research: content_length=%d, search_used=%s, needs_clarification=%s",
                      len(research.content), research.search_used, research.needs_clarification)

        if research.needs_clarification:
            return GenerateResponse(
                session_id=str(uuid.uuid4()),
                topic=req.content[:20],
                questions=[],
                needs_clarification=True,
                domain_options=research.domain_options,
            )

        content = research.content
        search_used = research.search_used
        excluded = [item.strip() for item in req.excluded_questions if item.strip()]
        seen = {_question_key(item) for item in excluded}
        questions = []
        topic = ""
        max_attempts = 3 if excluded else 1

        feedback_section = ""
        if req.feedback:
            feedback_section = f"用户反馈：{req.feedback}"
        if req.previous_questions:
            feedback_section += f"\n上一轮题目（不得重复）：\n" + "\n".join(f"- {q}" for q in req.previous_questions)

        for _ in range(max_attempts):
            remaining = max(1, req.question_count - len(questions))
            result = await chain_generate.ainvoke({
                "content": content,
                "count": remaining,
                "excluded_questions": "\n".join(f"- {item}" for item in excluded) or "无",
                "feedback_section": feedback_section,
                "format_instructions": parser.get_format_instructions(),
            })
            topic = topic or result.get("topic", "")
            for question in result.get("questions", []):
                key = _question_key(question.get("question", ""))
                if not key or key in seen:
                    continue
                seen.add(key)
                questions.append(question)
                excluded.append(question["question"])
                if len(questions) >= req.question_count:
                    break
            if len(questions) >= req.question_count:
                break

        if not questions:
            raise HTTPException(status_code=502, detail="未能生成与上一关不同的新题，请稍后重试")

        session_id = str(uuid.uuid4())
        for i, q in enumerate(questions):
            q["id"] = i + 1

        questions_with_image = [q for q in questions if q.get("needs_image")]
        if questions_with_image:
            logger.debug("Generating images for %d questions (out of %d total)", len(questions_with_image), len(questions))
            image_urls = await generate_images_batch(questions, session_id)
            for q, url in zip(questions, image_urls):
                if url:
                    q["image_url"] = url

        return GenerateResponse(
            session_id=session_id,
            topic=topic or req.content[:20],
            questions=questions,
            search_used=search_used,
        )
    except ContentInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Generate chain failed")
        raise HTTPException(status_code=500, detail=f"题目生成失败：{str(e)}")
