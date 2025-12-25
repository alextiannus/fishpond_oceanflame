"""
管理后台 API（店员核销等）
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import hashlib

from app.database import get_db
from app.models.models import Coupon, User, AdminUser

router = APIRouter()


# Pydantic 模型
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    success: bool
    message: str
    admin_id: Optional[int] = None
    role: Optional[str] = None


class VerifyCouponRequest(BaseModel):
    code: str
    admin_id: int


class VerifyCouponResponse(BaseModel):
    success: bool
    message: str
    coupon_value: Optional[int] = None
    fish_type: Optional[str] = None


class CouponStats(BaseModel):
    total_issued: int
    total_used: int
    total_value_issued: int
    total_value_used: int


class DashboardStats(BaseModel):
    total_users: int
    total_fishes: int
    coupon_stats: CouponStats


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """管理员登录"""
    # 密码哈希
    password_hash = hashlib.sha256(request.password.encode()).hexdigest()
    
    result = await db.execute(
        select(AdminUser).where(
            AdminUser.username == request.username,
            AdminUser.password_hash == password_hash,
            AdminUser.is_active == True
        )
    )
    admin = result.scalar_one_or_none()
    
    if not admin:
        return AdminLoginResponse(
            success=False,
            message="用户名或密码错误"
        )
    
    return AdminLoginResponse(
        success=True,
        message="登录成功",
        admin_id=admin.id,
        role=admin.role
    )


@router.post("/coupon/verify", response_model=VerifyCouponResponse)
async def verify_coupon(
    request: VerifyCouponRequest,
    db: AsyncSession = Depends(get_db)
):
    """核销优惠券"""
    # 验证管理员
    admin = await db.get(AdminUser, request.admin_id)
    if not admin or not admin.is_active:
        raise HTTPException(status_code=403, detail="无权限")
    
    # 查找优惠券
    result = await db.execute(
        select(Coupon).where(Coupon.code == request.code.upper())
    )
    coupon = result.scalar_one_or_none()
    
    if not coupon:
        return VerifyCouponResponse(
            success=False,
            message="优惠券不存在"
        )
    
    if coupon.used:
        return VerifyCouponResponse(
            success=False,
            message=f"优惠券已于 {coupon.used_at.strftime('%Y-%m-%d %H:%M')} 被核销"
        )
    
    if coupon.expires_at < datetime.utcnow():
        return VerifyCouponResponse(
            success=False,
            message="优惠券已过期"
        )
    
    # 核销优惠券
    coupon.used = True
    coupon.used_at = datetime.utcnow()
    coupon.used_by = admin.username
    
    await db.commit()
    
    return VerifyCouponResponse(
        success=True,
        message=f"核销成功！优惠 ¥{coupon.value}",
        coupon_value=coupon.value,
        fish_type=coupon.fish_type.value
    )


@router.get("/coupon/check/{code}", response_model=VerifyCouponResponse)
async def check_coupon(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """查询优惠券状态（不核销）"""
    result = await db.execute(
        select(Coupon).where(Coupon.code == code.upper())
    )
    coupon = result.scalar_one_or_none()
    
    if not coupon:
        return VerifyCouponResponse(
            success=False,
            message="优惠券不存在"
        )
    
    if coupon.used:
        return VerifyCouponResponse(
            success=False,
            message=f"优惠券已核销",
            coupon_value=coupon.value,
            fish_type=coupon.fish_type.value
        )
    
    if coupon.expires_at < datetime.utcnow():
        return VerifyCouponResponse(
            success=False,
            message="优惠券已过期",
            coupon_value=coupon.value,
            fish_type=coupon.fish_type.value
        )
    
    return VerifyCouponResponse(
        success=True,
        message="优惠券有效",
        coupon_value=coupon.value,
        fish_type=coupon.fish_type.value
    )


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """获取仪表盘统计数据"""
    # 用户总数
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0
    
    # 鱼总数 (这里需要导入 Fish 模型)
    from app.models.models import Fish
    result = await db.execute(select(func.count(Fish.id)))
    total_fishes = result.scalar() or 0
    
    # 优惠券统计
    result = await db.execute(select(func.count(Coupon.id)))
    total_issued = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(Coupon.id)).where(Coupon.used == True)
    )
    total_used = result.scalar() or 0
    
    result = await db.execute(select(func.sum(Coupon.value)))
    total_value_issued = result.scalar() or 0
    
    result = await db.execute(
        select(func.sum(Coupon.value)).where(Coupon.used == True)
    )
    total_value_used = result.scalar() or 0
    
    return DashboardStats(
        total_users=total_users,
        total_fishes=total_fishes,
        coupon_stats=CouponStats(
            total_issued=total_issued,
            total_used=total_used,
            total_value_issued=total_value_issued,
            total_value_used=total_value_used,
        )
    )
