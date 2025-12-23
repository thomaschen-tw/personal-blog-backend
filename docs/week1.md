# Week 1（Day 1–5）基础骨架与搜索功能（复盘版）

> 本文根据 `docs/week1/day1.md` ~ `day5.md` 的日更记录汇总，目标是把“本周真实做过的事情 + 关键踩坑与解决 + 可复现流程”整理成一份周总结。

## 每日工作文档索引

- Day 1：FastAPI 后端与 NotionNext 前端联调（最小 API + CORS）→ [day1.md](./week1/day1.md)
- Day 2：统一 Python 环境 + Postgres（Docker）+ seed 脚本 → [day2.md](./week1/day2.md)
- Day 3：接入 SQLAlchemy + 实现 `/api/search` → [day3.md](./week1/day3.md)
- Day 4：前后端搜索链路打通 + 测试/CI + slug 迁移思考 → [day4.md](./week1/day4.md)
- Day 5：实现 `POST /api/posts` + 前端保存按钮联调 + 文章详情页对接 → [day5.md](./week1/day5.md)

## 本周目标（以实际落地为准）

- **后端骨架**：FastAPI + CORS + `/api/health`，可访问 OpenAPI（`/docs`）。
- **数据库链路**：Postgres（Docker）+ SQLAlchemy model + `scripts/seed_db.py` 可生成测试数据。
- **搜索功能**：`GET /api/search?q=...` 支持标题/内容模糊匹配，前端页面可展示结果。
- **创建文章**：`POST /api/posts` 落库，前端可创建并跳转到详情页。
- **URL/路由**：引入 `slug` 与 `href=/article/{slug}`，解决前端渲染/路由冲突与字段不一致问题。

## 交付物（验收清单）

- **API**：
  - `GET /api/health`：返回 `{"status":"ok"}`
  - `GET /api/search?q=demo`：返回列表（包含 `id/title/summary/tags/slug/href`）
  - `POST /api/posts`：创建文章并返回统一响应（含 `id/slug/href/created_at` 等）
  - `GET /api/post/slug/{slug}`：详情页可通过 slug 拉取文章
- **数据**：`scripts/seed_db.py` 可生成 50–200 条文章并写入 Postgres。
- **联调**：NotionNext 搜索页可调用后端搜索；创建文章页可保存并跳转详情。

## 本周“最小闭环”流程图（端到端）

```mermaid
flowchart LR
  FE[NotionNext: 搜索/创建页面] -->|fetch| API[FastAPI]
  API --> DB[(Postgres)]
  API --> FE
  FE -->|打开详情 /article/{slug}| FE2[NotionNext: 详情页]
  FE2 -->|fetch /api/post/slug/{slug}| API
```

## 操作清单（可复现）

### 1) 运行数据库（Docker Compose）

- **本仓库已提供**：`docker-compose.yaml`
- **端口约定**：宿主机 `5433` → 容器 `5432`

常用验证点：
- `docker compose up -d` 后，容器 `demo-postgres` 正常运行
- 能 `docker exec -it demo-postgres psql -U demo -d demo` 进入并查询

### 2) 运行后端（两种方式）

- **方式 A（开发）**：本地 `uvicorn` + 本地 venv（Day 1/2 的主路径）
  - 优点：调试快、改代码立刻生效
  - 注意：默认 DB 连接为 `localhost:5433`（见 `app/main.py` 的 `DATABASE_URL` 默认值）

- **方式 B（容器）**：Compose 起 backend（仓库里已有）
  - Compose 内 `DATABASE_URL` 会使用服务名 `postgres-demo:5432`（避免“容器里 localhost 不是宿主机”）

### 3) 生成测试数据

- 运行 `scripts/seed_db.py` 生成文章
- 进入数据库确认 `articles` 表有数据

### 4) 手动验收（建议顺序）

- 打开 `http://localhost:8000/docs`
- 访问 `GET /api/health`
- 访问 `GET /api/search?q=article`
- 创建文章：`POST /api/posts`
- 用返回的 `slug` 访问：`GET /api/post/slug/{slug}`

## 接口与数据契约（以当前仓库实现为准）

### `/api/search` 返回字段（前端渲染需要）

- **必备字段**：`id`、`title`、`summary`、`tags`（数组）、`slug`、`href`
- **关键点**：
  - `tags` 必须是数组（Day 4 解决了前端 `.map()` 报错）
  - `href` 必须可用（避免 `href={undefined}`）

### 文章统一响应（列表/详情/创建）

- 通过 `format_post_response()` 统一输出（Day 5）
- `href` 规范：`/article/{slug}`（其中 `slug` 为空时降级为 `id`）

## 关键问题与解决（来自 Day 1–5 的高频踩坑）

- **Python 环境混乱（多个 Python/conda 干扰）**
  - **现象**：安装了依赖但运行/导入失败，路径指向不确定
  - **解决**：统一使用 Homebrew Python + `venv`；每次激活后用 `which python` 验证指向 `.venv`

- **容器内连接数据库不能用 `localhost`**
  - **现象**：backend 容器连 DB 失败，但本机能连
  - **解决**：Compose 内用服务名（本仓库为 `postgres-demo:5432`），不要用 `localhost:5433`

- **Next.js 页面路由与 API 路由冲突 / 搜索逻辑不一致**
  - **现象**：前端 `/search/[keyword]` 走了页面缓存逻辑，导致与后端搜索不一致
  - **解决**：前端改为直接调用后端 `GET /api/search`，并移除/绕开 cache 依赖（Day 4）

- **前端出现 `ioredis` 的 `dns` 模块报错**
  - **原因**：页面引入了 Redis/cache 逻辑（Node 环境依赖）导致构建/运行异常
  - **解决**：去掉对 `cache_manager` 的依赖，改为直接请求后端（Day 4）

- **后端 tags 存储与前端展示类型不一致**
  - **现象**：后端存字符串，前端当数组用导致 `.map()` 报错
  - **解决**：响应层把 tags 统一转换为数组（Day 4/5 的格式化响应）

- **新增字段（如 `slug`）后，数据库表结构不更新**
  - **现象**：SQLAlchemy 查询报列不存在
  - **解决**：引入 Alembic 迁移（Day 4 给出迁移流程与思路）

- **测试/CI 里数据库依赖导致不稳定**
  - **现象**：导入阶段建表或连接 DB，CI/本地收集测试时失败
  - **解决思路（Day 4）**：
    - 用 `dependency_overrides` 注入 FakeSession，减少对真实 DB 的依赖
    - 或在 CI job 里显式启动 Postgres 并等待就绪
    - 确保 `httpx` 在依赖中（FastAPI TestClient 需要）

## 本周复盘要点（建议延续到 Week 2）

- **优先打通链路**：先端到端可用（搜索 + 创建 + 详情），再做“性能/结构优化”。
- **接口契约要稳定**：`tags/slug/href/created_at` 这类字段不稳定会让前端排障变慢。
- **把踩坑写进文档**：尤其是“路由冲突”“容器网络”“CI 数据库”这三类问题。
