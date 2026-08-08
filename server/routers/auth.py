import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.orm import User
from models.schemas import LoginRequest, LoginResponse
from config import settings
from auth import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["auth"])


async def _get_openid_from_wechat(code: str) -> str:
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.wx_appid,
        "secret": settings.wx_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()
    openid = data.get("openid")
    if not openid:
        errcode = data.get("errcode", "unknown")
        errmsg = data.get("errmsg", "")
        raise HTTPException(status_code=400, detail=f"微信登录失败: {errcode} - {errmsg}")
    return openid


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    if settings.dev_mode:
        openid = f"dev_{req.code}"
    else:
        if not settings.wx_appid or not settings.wx_secret:
            raise HTTPException(status_code=500, detail="微信 AppID/Secret 未配置")
        openid = await _get_openid_from_wechat(req.code)

    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()
    is_new = False

    if not user:
        user = User(openid=openid, nickname="知识探索者")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        is_new = True
        logger.info("New user created: openid=%s", openid)

    return LoginResponse(
        openid=user.openid,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        is_new=is_new,
        access_token=create_access_token(user),
        expires_in=settings.auth_token_ttl_seconds,
    )
