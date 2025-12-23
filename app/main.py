# backend/app/main.py
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from app.model import Base, Article
from datetime import datetime
import os
# import httpx  # Day 11: 启用 n8n webhook 时需要
import logging
from pydantic import BaseModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# 数据库连接配置（和 seed_db.py 保持一致）
DATABASE_URL =  os.getenv("DATABASE_URL", "postgresql://demo:demo@localhost:5433/demo")

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


# 文章URL前缀（与前端配置保持一致）
POST_URL_PREFIX = "article"

class PostCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None
    slug: Optional[str] = None
# 健康检查接口：用于快速验证后端是否运行
@app.get("/api/health")
async def health():
    return {"status": "ok"}


# 返回文章列表（从数据库查询）
# @app.get("/api/posts")
# def get_posts(db: Session = Depends(get_db)):
#     posts = db.query(Article).all()
#     return [
#         {
#             "id": p.id,
#             "title": p.title,
#             "content": p.content[:200] if p.content else "",
#             "tags": [t.strip() for t in p.tags.split(",")] if p.tags else [],
#             "slug": p.slug or str(p.id),
#             "href": f"/{POST_URL_PREFIX}/{p.slug or p.id}"  # 使用 article 前缀
#         }
#         for p in posts
#     ]
@app.post("/api/posts")
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """
    创建新文章
    - 将文章保存到数据库
    - Day 5: 先不触发 n8n webhook，等 Day 11 再启用
    """
    # 将 tags 列表转为字符串存储
    tags_str = ",".join(post.tags) if post.tags else None
    article = Article(
        title=post.title,
        content=post.content,
        tags=tags_str,
        slug=post.slug
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    
    # 格式化响应
    response = format_post_response(article)
    
    # TODO: Day 11 - 启用 n8n webhook 触发
    # 触发 n8n webhook（如果配置了）
    # n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
    # if n8n_webhook_url:
    #     try:
    #         # 异步调用 n8n webhook，不阻塞响应
    #         webhook_payload = {
    #             "post_id": article.id,
    #             "title": article.title,
    #             "slug": article.slug,
    #             "action": "save",
    #             "triggered_by": "backend",
    #             "created_at": article.created_at.isoformat() if article.created_at else None
    #         }
    #         
    #         # 使用 httpx 异步发送请求（非阻塞）
    #         # 注意：这里使用同步 httpx 是为了简化，生产环境建议使用异步
    #         try:
    #             httpx.post(
    #                 n8n_webhook_url,
    #                 json=webhook_payload,
    #                 timeout=5.0  # 5秒超时，避免阻塞太久
    #             )
    #             logger.info(f"Successfully triggered n8n webhook for post {article.id}")
    #         except Exception as e:
    #             # 记录错误但不影响主流程
    #             logger.warning(f"Failed to trigger n8n webhook: {e}")
    #     except Exception as e:
    #         logger.error(f"Error preparing n8n webhook: {e}")
    
    logger.info(f"Post created successfully: id={article.id}, title={article.title}, slug={article.slug}")
    return response

# 通过 ID 获取单篇文章
@app.get("/api/posts/{post_id}")
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Article).filter(Article.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return format_post_response(post)


# 通过 slug 获取单篇文章（新增）
@app.get("/api/post/slug/{slug}")
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    # 首先尝试通过 slug 字段查找
    post = db.query(Article).filter(Article.slug == slug).first()

    # 如果找不到，尝试将 slug 作为 id 查找（兼容性处理）
    if not post:
        try:
            post_id = int(slug)
            post = db.query(Article).filter(Article.id == post_id).first()
        except ValueError:
            pass

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return format_post_response(post)


# 格式化文章响应数据（统一格式）
def format_post_response(post: Article) -> dict:
    """
    将数据库文章对象格式化为前端需要的格式
    返回的 href 格式为: /article/{slug}
    """
    # 获取 slug，如果没有则使用 id
    slug = post.slug or str(post.id)

    # 处理 tags
    tags = []
    if post.tags:
        if isinstance(post.tags, str):
            tags = [t.strip() for t in post.tags.split(",") if t.strip()]
        elif isinstance(post.tags, list):
            tags = post.tags

    # 处理日期
    created_at = None
    if post.created_at:
        if isinstance(post.created_at, datetime):
            created_at = post.created_at.isoformat()
        else:
            created_at = str(post.created_at)

    # 构建响应 - href 使用 /article/{slug} 格式
    response = {
        "id": post.id,
        "title": post.title,
        "slug": slug,
        "href": f"/{POST_URL_PREFIX}/{slug}",  # 格式: /article/{slug}
        "content": post.content or "",
        "summary": (post.content[:200] + "...") if post.content and len(post.content) > 200 else (post.content or ""),
        "tags": tags,
        "type": "Post",
        "status": "Published"
    }

    # 添加可选字段
    if created_at:
        response["created_at"] = created_at
        response["createdTime"] = created_at
        response["date"] = {
            "start_date": created_at.split("T")[0] if "T" in created_at else created_at
        }

    return response


# 搜索接口：支持标题和内容模糊匹配
@app.get("/api/search")
def search_posts(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    results = db.query(Article).filter(
        (Article.title.ilike(f"%{q}%")) | (Article.content.ilike(f"%{q}%"))
    ).all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "summary": (p.content[:200] + "...") if p.content and len(p.content) > 200 else (p.content or ""),
            "tags": [t.strip() for t in p.tags.split(",")] if p.tags else [],
            "slug": p.slug or str(p.id),
            "href": f"/{POST_URL_PREFIX}/{p.slug or p.id}"  # 使用 article 前缀
        }
        for p in results
    ]