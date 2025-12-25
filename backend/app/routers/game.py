"""
游戏相关 API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import random

from app.database import get_db
from app.models.models import User, Fish, Coupon, FeedingRecord, FishType, FishStatus

router = APIRouter()

# 鱼类配置
FISH_CONFIG = {
    FishType.QINGJIANG: {"name": "清江鱼", "growth_time": 3, "value": 50},
    FishType.LINGBO: {"name": "凌波鱼", "growth_time": 4, "value": 80},
    FishType.BASHA: {"name": "巴沙鱼", "growth_time": 5, "value": 100},
    FishType.JINMU: {"name": "金目鲈", "growth_time": 7, "value": 150},
}

# 每日饲料限制
DAILY_FEED_LIMIT = 10


# Pydantic 模型
class FishResponse(BaseModel):
    id: int
    fish_type: str
    status: str
    hunger: float
    health: float
    growth: float
    pos_x: float
    pos_y: float
    created_at: datetime

    class Config:
        from_attributes = True


class CouponResponse(BaseModel):
    id: int
    code: str
    fish_type: str
    value: int
    used: bool
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AddFishRequest(BaseModel):
    fish_type: str


class FeedResult(BaseModel):
    success: bool
    message: str
    fish: Optional[FishResponse] = None
    remaining_feed: int


class HarvestResult(BaseModel):
    success: bool
    message: str
    coupon: Optional[CouponResponse] = None


class GameState(BaseModel):
    fishes: List[FishResponse]
    coupons: List[CouponResponse]
    daily_feed_count: int


@router.get("/state/{user_id}", response_model=GameState)
async def get_game_state(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取用户游戏状态"""
    # 检查并重置每日饲料
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if user.last_feed_date != today:
        user.daily_feed_count = DAILY_FEED_LIMIT
        user.last_feed_date = today
        await db.commit()
    
    # 获取鱼列表
    result = await db.execute(
        select(Fish).where(Fish.user_id == user_id)
    )
    fishes = result.scalars().all()
    
    # 获取优惠券列表
    result = await db.execute(
        select(Coupon).where(Coupon.user_id == user_id, Coupon.used == False)
    )
    coupons = result.scalars().all()
    
    return GameState(
        fishes=[FishResponse.model_validate(f) for f in fishes],
        coupons=[CouponResponse.model_validate(c) for c in coupons],
        daily_feed_count=user.daily_feed_count
    )


@router.post("/fish/add/{user_id}", response_model=FishResponse)
async def add_fish(
    user_id: int,
    request: AddFishRequest,
    db: AsyncSession = Depends(get_db)
):
    """添加一条新鱼"""
    try:
        fish_type = FishType(request.fish_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的鱼类型")
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    fish = Fish(
        user_id=user_id,
        fish_type=fish_type,
        status=FishStatus.BABY,
        pos_x=random.uniform(10, 90),
        pos_y=random.uniform(20, 80),
    )
    
    db.add(fish)
    await db.commit()
    await db.refresh(fish)
    
    return FishResponse.model_validate(fish)


@router.post("/fish/feed/{fish_id}", response_model=FeedResult)
async def feed_fish(
    fish_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """喂食一条鱼"""
    fish = await db.get(Fish, fish_id)
    if not fish:
        raise HTTPException(status_code=404, detail="鱼不存在")
    
    if fish.status == FishStatus.DEAD:
        return FeedResult(
            success=False,
            message="这条鱼已经死了",
            remaining_feed=0
        )
    
    user = await db.get(User, fish.user_id)
    
    # 检查每日饲料限制
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if user.last_feed_date != today:
        user.daily_feed_count = DAILY_FEED_LIMIT
        user.last_feed_date = today
    
    if user.daily_feed_count <= 0:
        return FeedResult(
            success=False,
            message="今日饲料已用完，明天再来吧！",
            remaining_feed=0
        )
    
    # 喂食
    fish.hunger = min(100, fish.hunger + 30)
    fish.growth += 10
    user.daily_feed_count -= 1
    
    # 检查成长
    config = FISH_CONFIG[fish.fish_type]
    if fish.growth >= config["growth_time"] * 10 and fish.status == FishStatus.BABY:
        fish.status = FishStatus.ADULT
    
    # 恢复饥饿状态
    if fish.status == FishStatus.HUNGRY and fish.hunger > 30:
        fish.status = FishStatus.ADULT if fish.growth >= config["growth_time"] * 10 else FishStatus.BABY
    
    # 记录喂食
    record = FeedingRecord(
        user_id=fish.user_id,
        fish_id=fish_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(record)
    
    await db.commit()
    await db.refresh(fish)
    
    return FeedResult(
        success=True,
        message="喂食成功！",
        fish=FishResponse.model_validate(fish),
        remaining_feed=user.daily_feed_count
    )


@router.post("/fish/harvest/{fish_id}", response_model=HarvestResult)
async def harvest_fish(
    fish_id: int,
    db: AsyncSession = Depends(get_db)
):
    """收获成年鱼，获得优惠券"""
    fish = await db.get(Fish, fish_id)
    if not fish:
        raise HTTPException(status_code=404, detail="鱼不存在")
    
    if fish.status != FishStatus.ADULT:
        return HarvestResult(
            success=False,
            message="只能收获成年鱼"
        )
    
    config = FISH_CONFIG[fish.fish_type]
    
    # 生成优惠券
    coupon = Coupon(
        user_id=fish.user_id,
        code=f"OF{secrets.token_hex(4).upper()}",
        fish_type=fish.fish_type,
        value=config["value"],
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    
    db.add(coupon)
    
    # 更新用户统计
    user = await db.get(User, fish.user_id)
    user.total_coupons_earned += 1
    
    # 删除鱼
    await db.delete(fish)
    await db.commit()
    await db.refresh(coupon)
    
    return HarvestResult(
        success=True,
        message=f"获得 ¥{config['value']} 优惠券！",
        coupon=CouponResponse.model_validate(coupon)
    )


@router.get("/coupons/{user_id}", response_model=List[CouponResponse])
async def get_user_coupons(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取用户优惠券列表"""
    result = await db.execute(
        select(Coupon).where(Coupon.user_id == user_id).order_by(Coupon.created_at.desc())
    )
    coupons = result.scalars().all()
    
    return [CouponResponse.model_validate(c) for c in coupons]
