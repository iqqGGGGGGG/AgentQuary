import uuid
import logging
from fastapi import APIRouter, HTTPException
from models.schemas import GenerateRequest, GenerateResponse
from chains.generate_chain import chain_generate, parser
from services.content import ContentInputError, normalize_content

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_quiz(req: GenerateRequest):
    try:
        content = await normalize_content(req.content)
        result = await chain_generate.ainvoke({
            "content": content,
            "count": req.question_count,
            "format_instructions": parser.get_format_instructions(),
        })

        questions = result.get("questions", [])
        for i, q in enumerate(questions):
            q["id"] = i + 1

        return GenerateResponse(
            session_id=str(uuid.uuid4()),
            topic=result.get("topic", req.content[:20]),
            questions=questions,
        )
    except ContentInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Generate chain failed")
        raise HTTPException(status_code=500, detail=f"题目生成失败：{str(e)}")
