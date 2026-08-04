from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from routers.auth import _get_openid_from_wechat


@pytest.mark.asyncio
async def test_login_new_user(client):
    resp = await client.post("/api/login", json={"code": "test_code_001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["openid"] == "dev_test_code_001"
    assert data["nickname"] == "知识探索者"
    assert data["is_new"] is True


@pytest.mark.asyncio
async def test_login_existing_user(client):
    resp1 = await client.post("/api/login", json={"code": "test_code_002"})
    assert resp1.status_code == 200
    assert resp1.json()["is_new"] is True

    resp2 = await client.post("/api/login", json={"code": "test_code_002"})
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["openid"] == "dev_test_code_002"
    assert data["is_new"] is False


@pytest.mark.asyncio
async def test_login_empty_code(client):
    resp = await client.post("/api/login", json={"code": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_code(client):
    resp = await client.post("/api/login", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_wechat_login_preserves_provider_error_message():
    response = MagicMock()
    response.json.return_value = {"errcode": 40029, "errmsg": "invalid code"}

    http_client = MagicMock()
    http_client.get = AsyncMock(return_value=response)
    context_manager = MagicMock()
    context_manager.__aenter__ = AsyncMock(return_value=http_client)
    context_manager.__aexit__ = AsyncMock(return_value=None)

    with patch("routers.auth.httpx.AsyncClient", return_value=context_manager):
        with pytest.raises(HTTPException) as exc_info:
            await _get_openid_from_wechat("bad-code")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "微信登录失败: 40029 - invalid code"
