
# 📘 Day 1 工作文档
# FastAPI 后端与 NotionNext 前端联调
---

## 环境与准备

- 已在本地有两个独立目录：
  - personal-blog-backend
  - NotionNext
- Python 3.13，使用 venv 虚拟环境

---

## 创建并运行 FastAPI 后端

### 1. 在后端目录创建虚拟环境并安装依赖
```bash
cd personal-blog-backend

# 创建 venv（基于你当前 python 3.13）
python -m venv .venv

# 激活 venv（macOS/Linux）
source .venv/bin/activate
# 如果是 Windows PowerShell：
# .venv\Scripts\Activate.ps1

# 升级基础工具
pip install --upgrade pip setuptools wheel

# 安装最小依赖
pip install fastapi uvicorn
```

可选：如果后续要写数据库，再安装 sqlalchemy、alembic 等。

### 2. 创建目录结构与文件
在 personal-blog-backend 下创建目录和文件：

- backend 目录建议如下（简单版）：
```
personal-blog-backend/
└── app/
    └── main.py
```

创建 app/main.py，内容如下：

```python
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
```

建议添加 .gitignore，避免上传本地环境：
```
# Python
__pycache__/
*.pyc

# Virtual environment
.venv/

# Env files
.env
```

### 3. 运行后端
```bash
# 确保 venv 已激活
uvicorn app.main:app --reload --port 8000
```

打开浏览器访问：
- http://localhost:8000/api/health
- http://localhost:8000/api/posts

看到 JSON 就说明后端跑起来了。

---

## 在 NotionNext 前端调用后端 API

NotionNext 是基于 Next.js 的前端。我们加一个简单页面，从你的后端（http://localhost:8000）取数据。

### 1. 安装依赖并启动前端（如未启动）
在 NotionNext 项目根目录（你的 fork 仓库）
```bash
# 进入前端项目
cd NotionNext

# 安装依赖（根据项目 README，通常是）
npm install
# 或 yarn
# yarn

# 开发启动
npm run dev
# 或 yarn dev
```

前端默认在 http://localhost:3000

### 2. 新增一个页面来调用后端
在 NotionNext 的 pages 目录下创建一个新页面，比如 pages/backend-test.tsx：

```tsx
import { useEffect, useState } from 'react'

type Post = {
  id: number
  title: string
  content: string
}

export default function BackendTestPage() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPosts() {
      try {
        setLoading(true)
        setError(null)
        const res = await fetch('http://localhost:8000/api/posts')
        if (!res.ok) {
          throw new Error(`后端返回错误状态码: ${res.status}`)
        }
        const data = await res.json()
        setPosts(data)
      } catch (e: any) {
        setError(e.message || '请求失败')
      } finally {
        setLoading(false)
      }
    }
    fetchPosts()
  }, [])

  return (
    <main style={{ padding: 24 }}>
      <h1>后端联调测试</h1>
      {loading && <p>加载中...</p>}
      {error && <p style={{ color: 'red' }}>错误：{error}</p>}
      {!loading && !error && (
        <ul>
          {posts.map(p => (
            <li key={p.id}>
              <strong>{p.title}</strong>
              <div>{p.content}</div>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
```

启动前端后访问 http://localhost:3000/backend-test，就能看到从后端取到的数据。

提示：
- 这是一个客户端组件（useEffect 里请求），适合开发阶段快速测试。
- 如果你希望服务端渲染（SSR），可以改用 getServerSideProps 在服务端拉取数据。

### 3. 如果出现跨域问题
- 确认后端 main.py 已配置 CORSMiddleware（上面代码已包含）。
- 确保你访问的是 http://localhost:8000（不是 https）。
- 浏览器 Network 面板查看请求是否成功，状态码是否 200。

---

## 📌 Day 1 总结

- 后端：
  - 终端运行 uvicorn，控制台无明显报错。
  - http://localhost:8000/api/health 返回 {"status":"ok"}
- 前端：
  - npm run dev 正常启动。
  - 打开 http://localhost:3000/backend-test 能看到后端数据。
- 如果请求失败：
  - 浏览器开发者工具 → Network → 查看请求 URL、状态码、响应内容。
  - 后端终端看日志（uvicorn 会打印请求）。
  - 确认防火墙或代理没有阻挡本地端口。

---

## 下一步与部署建议

- 后端继续丰富接口与数据结构（添加 Pydantic schemas、数据库等）。
- 将后端仓库推送到 GitHub（包含 README、requirements.txt、.gitignore）。
- 前端保持 fork 关系，日后可同步上游 NotionNext 更新。
- 部署：
  - 前端到 Vercel（最简），或 AWS S3+CloudFront。
  - 后端到 AWS（EC2/ECS/Fargate），或用 Docker 容器化。