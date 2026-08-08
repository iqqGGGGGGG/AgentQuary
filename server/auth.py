import base64
import hashlib
import hmac
import json
import logging
import time

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.orm import User

logger = logging.getLogger(__name__)
TOKEN_VERSION = "v1"
DEV_AUTH_SECRET = "agentquary-development-secret-do-not-use-in-production"


def validate_auth_settings() -> None:
    if settings.auth_token_ttl_seconds <= 0:
        raise RuntimeError("AUTH_TOKEN_TTL_SECONDS 必须大于 0")
    if not settings.auth_secret and not settings.dev_mode:
        raise RuntimeError("生产模式必须配置 AUTH_SECRET")
    if settings.auth_secret and len(settings.auth_secret.encode("utf-8")) < 32:
        message = "AUTH_SECRET 必须至少包含 32 字节"
        if not settings.dev_mode:
            raise RuntimeError(message)
        logger.warning("%s；当前仅允许开发模式使用", message)
    if not settings.auth_secret and settings.dev_mode:
        logger.warning("AUTH_SECRET 未配置，正在使用仅限开发环境的固定密钥")


def _token_secret() -> bytes:
    if settings.auth_secret:
        return settings.auth_secret.encode("utf-8")
    if settings.dev_mode:
        return DEV_AUTH_SECRET.encode("utf-8")
    raise RuntimeError("生产模式必须配置 AUTH_SECRET")


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    decoded = base64.b64decode(value + padding, altchars=b"-_", validate=True)
    if _base64url_encode(decoded) != value:
        raise ValueError("non-canonical base64url encoding")
    return decoded


def create_access_token(user: User, *, now: int | None = None) -> str:
    issued_at = int(time.time()) if now is None else now
    payload = {
        "uid": user.id,
        "sub": user.openid,
        "iat": issued_at,
        "exp": issued_at + settings.auth_token_ttl_seconds,
    }
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signed_value = f"{TOKEN_VERSION}.{encoded_payload}"
    signature = hmac.new(
        _token_secret(), signed_value.encode("ascii"), hashlib.sha256
    ).digest()
    return f"{signed_value}.{_base64url_encode(signature)}"


def decode_access_token(token: str, *, now: int | None = None) -> dict[str, int | str]:
    try:
        version, encoded_payload, encoded_signature = token.split(".")
        if version != TOKEN_VERSION:
            raise ValueError

        signed_value = f"{version}.{encoded_payload}"
        expected_signature = hmac.new(
            _token_secret(), signed_value.encode("ascii"), hashlib.sha256
        ).digest()
        supplied_signature = _base64url_decode(encoded_signature)
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise ValueError

        payload = json.loads(_base64url_decode(encoded_payload))
        uid = payload["uid"]
        subject = payload["sub"]
        issued_at = payload["iat"]
        expires_at = payload["exp"]
        if (
            not isinstance(uid, int)
            or isinstance(uid, bool)
            or not isinstance(subject, str)
            or not subject
            or not isinstance(issued_at, int)
            or isinstance(issued_at, bool)
            or not isinstance(expires_at, int)
            or isinstance(expires_at, bool)
            or expires_at <= issued_at
            or expires_at <= (int(time.time()) if now is None else now)
        ):
            raise ValueError
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("invalid access token") from None

    return payload


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="登录凭证无效或已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization:
        raise _unauthorized()

    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token or " " in token:
        raise _unauthorized()

    try:
        claims = decode_access_token(token)
    except ValueError:
        raise _unauthorized() from None

    result = await db.execute(select(User).where(User.id == claims["uid"]))
    user = result.scalar_one_or_none()
    if not user or user.openid != claims["sub"]:
        raise _unauthorized()
    return user
