"""
数据模型定义
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class FishType(str, enum.Enum):
    QINGJIANG = "qingjiang"  # 清江鱼
    LINGBO = "lingbo"        # 凌波鱼
    BASHA = "basha"          # 巴沙鱼
    JINMU = "jinmu"          # 金目鲈


class FishStatus(str, enum.Enum):
    BABY = "baby"
    ADULT = "adult"
    HUNGRY = "hungry"
    SICK = "sick"
    DEAD = "dead"


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(128), unique=True, index=True, nullable=True)  # 微信 openid
    phone = Column(String(20), unique=True, index=True, nullable=True)
    username = Column(String(50), default="访客")
    avatar = Column(String(255), nullable=True)
    
    # 游戏数据
    daily_feed_count = Column(Integer, default=10)
    last_feed_date = Column(String(10), nullable=True)
    total_coupons_earned = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    fishes = relationship("Fish", back_populates="owner")
    coupons = relationship("Coupon", back_populates="owner")


class Fish(Base):
    """鱼模型"""
    __tablename__ = "fishes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    fish_type = Column(SQLEnum(FishType), nullable=False)
    status = Column(SQLEnum(FishStatus), default=FishStatus.BABY)
    hunger = Column(Float, default=100.0)
    health = Column(Float, default=100.0)
    growth = Column(Float, default=0.0)
    
    # 位置信息 (用于前端渲染)
    pos_x = Column(Float, default=50.0)
    pos_y = Column(Float, default=50.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    owner = relationship("User", back_populates="fishes")


class Coupon(Base):
    """优惠券模型"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    code = Column(String(20), unique=True, index=True, nullable=False)
    fish_type = Column(SQLEnum(FishType), nullable=False)
    value = Column(Integer, nullable=False)  # 优惠金额（分）
    
    used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    used_by = Column(String(50), nullable=True)  # 核销员工 ID
    
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    owner = relationship("User", back_populates="coupons")


class FeedingRecord(Base):
    """喂食记录（用于防作弊）"""
    __tablename__ = "feeding_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fish_id = Column(Integer, ForeignKey("fishes.id"), nullable=False)
    
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AdminUser(Base):
    """管理员/店员用户"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="staff")  # admin, staff
    store_id = Column(String(50), nullable=True)  # 所属门店
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
