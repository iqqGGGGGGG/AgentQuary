import pytest

from services.content import ContentInputError, normalize_content


@pytest.mark.asyncio
async def test_plain_text_is_trimmed():
    assert await normalize_content("  太阳系基础知识  ") == "太阳系基础知识"


@pytest.mark.asyncio
async def test_blank_text_is_rejected():
    with pytest.raises(ContentInputError):
        await normalize_content("   ")


@pytest.mark.asyncio
async def test_private_url_is_rejected():
    with pytest.raises(ContentInputError, match="内网"):
        await normalize_content("http://127.0.0.1/private")
