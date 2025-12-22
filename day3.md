
---

## 修改后的 `main.py`

```python
# backend/app/main.py
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from app.model import Base, Article

# 数据库连接配置（和 seed_db.py 保持一致）
DATABASE_URL = "postgresql://demo:demo@localhost:5433/demo"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 初始化数据库表（如果不存在则创建）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Blog Backend",
    version="0.1.0",
)

# CORS：允许前端在不同域名/端口访问后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源；生产建议改成你的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入：获取数据库 session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 健康检查接口：用于快速验证后端是否运行
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# 返回文章列表（从数据库查询）
@app.get("/api/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Article).all()
    return [
        {"id": p.id, "title": p.title, "content": p.content[:200], "tags": p.tags}
        for p in posts
    ]

# 返回单篇文章
@app.get("/api/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Article).filter(Article.id == post_id).first()
    if not post:
        return {"error": "Post not found"}
    return {"id": post.id, "title": post.title, "content": post.content, "tags": post.tags}

# 搜索接口：支持标题和内容模糊匹配
@app.get("/api/search")
def search_posts(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    results = db.query(Article).filter(
        (Article.title.ilike(f"%{q}%")) | (Article.content.ilike(f"%{q}%"))
    ).all()

    return [
        {"id": p.id, "title": p.title, "content": p.content[:200], "tags": p.tags}
        for p in results
    ]
```

---

## 改动说明
1. **数据库连接**：和 `seed_db.py` 保持一致，使用 `postgresql://demo:demo@localhost:5433/demo`。
2. **依赖注入**：增加 `get_db()`，保证每次请求都能获取并关闭数据库连接。
3. **文章接口**：`/api/posts` 和 `/api/posts/{id}` 改为真正从数据库查询，而不是返回模拟数据。
4. **搜索接口**：新增 `/api/search?q=xxx`，支持 `title` 和 `content` 的模糊匹配。
5. **返回内容**：为了避免返回过长的正文，搜索和列表接口只返回前 200 字摘要。

---

## 测试步骤
1. 启动数据库：
   ```bash
   docker-compose up -d
   ```
2. 运行种子脚本：
   ```bash
   python scripts/seed_db.py
   ```
3. 进入数据库检查：
```bash
        docker exec -it demo-postgres psql -U demo -d demo
   ```
4. 启动后端：
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. 测试接口：
   - 健康检查: `http://localhost:8000/api/health`
   - 获取文章列表: `http://localhost:8000/api/posts`
   - 获取单篇文章: `http://localhost:8000/api/posts/1`
   - 搜索文章: `http://localhost:8000/api/search?q=demo` eg: article1

---
