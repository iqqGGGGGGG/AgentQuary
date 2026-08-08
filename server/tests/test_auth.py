from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from auth import create_access_token, validate_auth_settings
from config import settings
from routers.auth import _get_openid_from_wechat


@pytest.mark.asyncio
async def test_login_new_user(client):
    resp = await client.post("/api/login", json={"code": "test_code_001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["openid"] == "dev_test_code_001"
    assert data["nickname"] == "知识探索者"
    assert data["is_new"] is True
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    assert data["access_token"].startswith("v1.")


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
async def test_forged_openid_header_is_not_authentication(client, test_user):
    resp = await client.get(
        "/api/user/profile",
        headers={"X-User-Openid": test_user.openid},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_token_authenticates_user(client):
    login_resp = await client.post("/api/login", json={"code": "token_user"})
    token = login_resp.json()["access_token"]

    profile_resp = await client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert profile_resp.status_code == 200
    assert profile_resp.json()["openid"] == "dev_token_user"


@pytest.mark.asyncio
async def test_tampered_access_token_is_rejected(client):
    login_resp = await client.post("/api/login", json={"code": "tamper_user"})
    token = login_resp.json()["access_token"]
    replacement = "A" if token[-1] != "A" else "B"

    resp = await client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token[:-1]}{replacement}"},
    )

    assert resp.status_code == 401
    assert resp.headers["www-authenticate"] == "Bearer"


@pytest.mark.asyncio
@pytest.mark.parametrize("signature", ["", "AA"])
async def test_empty_or_short_signature_is_rejected(client, signature):
    login_resp = await client.post("/api/login", json={"code": "short_signature"})
    token = login_resp.json()["access_token"]
    unsigned_token = f"{token.rsplit('.', 1)[0]}.{signature}"

    resp = await client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {unsigned_token}"},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_expired_access_token_is_rejected(client, test_user):
    token = create_access_token(test_user, now=1)

    resp = await client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_token_subject_must_still_match_user(client, test_user, db_session):
    token = create_access_token(test_user)
    test_user.openid = "changed_after_token_was_issued"
    await db_session.commit()

    resp = await client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 401


def test_production_requires_auth_secret(monkeypatch):
    monkeypatch.setattr(settings, "dev_mode", False)
    monkeypatch.setattr(settings, "auth_secret", "")

    with pytest.raises(RuntimeError, match="AUTH_SECRET"):
        validate_auth_settings()


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
