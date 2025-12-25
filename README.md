# 🐟 海鲜养殖乐园 (Ocean Flame Fish Game)

商业级 H5/PWA 养鱼游戏 - 养鱼赢优惠券！

## 🎮 功能特点

- **四种鱼类**：清江鱼、凌波鱼、巴沙鱼、金目鲈
- **养成系统**：喂食 → 成长 → 收获优惠券
- **PWA 支持**：可安装到手机桌面
- **日夜循环**：白天/黑夜场景自动切换
- **店员系统**：二维码核销管理后台

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + PWA |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | PostgreSQL + Redis |
| 管理后台 | Python Streamlit |
| 部署 | Docker + Nginx |

## 🚀 快速开始

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### 后端开发

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API 文档: http://localhost:8000/docs

### 管理后台

```bash
cd admin
pip install -r requirements.txt
streamlit run app.py
```

访问 http://localhost:8501

### Docker 部署

```bash
# 开发环境
docker-compose up -d db redis backend admin

# 生产环境（含 Nginx）
docker-compose --profile production up -d
```

## 📁 项目结构

```
ocean-flame-fish/
├── frontend/          # Vue 3 + Vite PWA
├── backend/           # Python FastAPI
├── admin/             # Streamlit 管理后台
├── nginx/             # Nginx 配置
└── docker-compose.yml # Docker 编排
```

## 🐟 鱼类配置

| 鱼类 | 成长天数 | 优惠券价值 |
|------|---------|-----------|
| 清江鱼 | 3 天 | ¥50 |
| 凌波鱼 | 4 天 | ¥80 |
| 巴沙鱼 | 5 天 | ¥100 |
| 金目鲈 | 7 天 | ¥150 |

## 📄 License

MIT
