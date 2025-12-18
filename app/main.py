from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# 健康检查接口：用于快速验证后端是否运行
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# 示例：返回文章列表（模拟数据）
@app.get("/api/posts")
async def get_posts():
    return [
        {"id": 1, "title": "第一篇文章", "content": "这是后端返回的内容"},
        {"id": 2, "title": "第二篇文章", "content": "联调成功！"},
    ]

# 示例：返回单篇文章
@app.get("/api/posts/{post_id}")
async def get_post(post_id: int):
    return {"id": post_id, "title": f"文章 {post_id}", "content": "这是某篇文章的内容"}
