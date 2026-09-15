import logging
import httpx
from config import settings
from services.cos_upload import upload_image

logger = logging.getLogger(__name__)

BAILIAN_IMAGE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/images/generations"


async def generate_image(prompt: str, session_id: str, question_id: int) -> str | None:
    if not settings.embedding_api_key:
        logger.debug("Image generation skipped: no embedding_api_key (used for Bailian)")
        return None

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                BAILIAN_IMAGE_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.embedding_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "qwen-image-3.0-pro",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                },
            )
            response.raise_for_status()
            data = response.json()

        images = data.get("data", [])
        if not images:
            logger.warning("No images returned from Bailian")
            return None

        image_url = images[0].get("url", "")
        if not image_url:
            logger.warning("No URL in image response")
            return None

        async with httpx.AsyncClient(timeout=30) as dl_client:
            dl_resp = await dl_client.get(image_url)
            dl_resp.raise_for_status()
            image_bytes = dl_resp.content

        cos_key = f"question-images/{session_id}_{question_id}.png"
        cos_url = upload_image(image_bytes, cos_key)

        logger.info("Image generated: session=%s, q=%d, url=%s", session_id, question_id, cos_url)
        return cos_url

    except Exception as e:
        logger.warning("Image generation failed for q%d: %s", question_id, e)
        return None


async def generate_images_batch(questions: list[dict], session_id: str) -> list[str | None]:
    import asyncio

    tasks = []
    for q in questions:
        if q.get("needs_image") and q.get("image_prompt"):
            prompt = q["image_prompt"]
            tasks.append(generate_image(prompt, session_id, q["id"]))
        else:
            tasks.append(_return_none())

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r if isinstance(r, str) else None for r in results]


async def _return_none() -> None:
    return None
