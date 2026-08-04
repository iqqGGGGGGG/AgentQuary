import logging
from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.orm import User

logger = logging.getLogger(__name__)


async def get_current_user(
    x_user_openid: str | None = Header(default=None, alias="X-User-Openid"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not x_user_openid:
        raise HTTPException(status_code=401, detail="缺少用户身份信息")

    result = await db.execute(select(User).where(User.openid == x_user_openid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在，请先登录")
    return user
