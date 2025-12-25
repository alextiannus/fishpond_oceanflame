"""
认证相关 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets
import hashlib

from app.database import get_db
from app.models.models import User

router = APIRouter()


# Pydantic 模型
class UserCreate(BaseModel):
    phone: Optional[str] = None
    username: Optional[str] = "访客"


class UserResponse(BaseModel):
    id: int
    username: str
    phone: Optional[str]
    daily_feed_count: int
    total_coupons_earned: int

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# 简单的 Token 存储 (生产环境应使用 Redis)
active_tokens = {}


def generate_token(user_id: int) -> str:
    """生成访问令牌"""
    token = secrets.token_urlsafe(32)
    active_tokens[token] = {
        "user_id": user_id,
        "expires": datetime.utcnow() + timedelta(days=30)
    }
    return token


def verify_token(token: str) -> Optional[int]:
    """验证令牌并返回用户 ID"""
    if token not in active_tokens:
        return None
    token_data = active_tokens[token]
    if datetime.utcnow() > token_data["expires"]:
        del active_tokens[token]
        return None
    return token_data["user_id"]


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册（游客自动注册）"""
    # 创建新用户
    user = User(
        username=user_data.username or "访客",
        phone=user_data.phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # 生成令牌
    token = generate_token(user.id)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login/guest", response_model=TokenResponse)
async def guest_login(db: AsyncSession = Depends(get_db)):
    """游客登录（自动创建账号）"""
    user = User(username="访客")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = generate_token(user.id)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户信息"""
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse.model_validate(user)
