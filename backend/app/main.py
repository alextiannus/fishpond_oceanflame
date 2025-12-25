"""
海鲜养殖乐园 - FastAPI 后端
Ocean Flame Fish Game Backend
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.routers import auth, game, admin
from app.database import init_db

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    print("🐟 海鲜养殖乐园后端启动成功!")
    yield
    # 关闭时清理资源
    print("👋 后端服务关闭")

# 创建 FastAPI 应用
app = FastAPI(
    title="海鲜养殖乐园 API",
    description="养鱼赢优惠券 - 商业级 H5/PWA 游戏后端",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(game.router, prefix="/api/game", tags=["游戏"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理"])

# 根路由
@app.get("/")
async def root():
    return {
        "message": "🐟 欢迎来到海鲜养殖乐园 API",
        "docs": "/docs",
        "version": "1.0.0"
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ocean-flame-fish"}

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.status_code}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
