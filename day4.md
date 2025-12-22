# Day4 项目总结

## 📌 总体目标
主要任务是完成 **前后端联调、搜索功能实现、数据库结构扩展与迁移**。最终实现了一个完整的搜索功能：前端输入关键词 → 调用后端 API → 查询数据库 → 返回结果并渲染到页面。

---

## 🗓️ Day4.1：前后端联调
- **前端**
  - 编写 `SearchInput` 组件，支持输入关键词并调用 `/api/search`,重写handleSearch逻辑。
  - 使用 `fetch` 请求后端接口，更新全局状态 `setFilteredNavPages`。
  - 添加清空搜索、回车触发搜索等交互逻辑。

- **后端**
  - 使用 FastAPI 编写 `/api/search` 接口，支持标题和内容模糊匹配。
  - 返回 JSON 格式：`[{id, title, summary, tags, slug, href}]`。
  - 解决了 Next.js 页面路由和 API 路由冲突问题，确保前端调用 `/api/search?q=xxx`。

---

## 🗓️ Day4.2：前端页面渲染与后端数据对接
- **问题排查**
  - Next.js 默认的 `/search/[keyword]` 页面使用内存缓存搜索，导致和后端接口不一致。
  - 出现 `ioredis` 的 `dns` 模块报错，因为前端页面引入了 Redis 缓存逻辑。

- **解决方案**
  - 去掉前端对 `cache_manager` 的依赖，改为直接调用后端 API。
  - 使用 `getServerSideProps` 或 `useEffect` 在页面加载时请求后端。
  - 修改后端返回的 `tags` 字段为数组，避免前端 `.map()` 报错。
  - 新增 `slug` 字段，用于生成唯一的文章 URL。

- **成果**
  - 页面 `/search/xxx` 能正确显示数据库里的搜索结果。
  - 标签渲染正常，避免了 `href={undefined}` 的错误。

---
## 🗓️ Day4.3：编写测试用例
- 针对数据库参数和接口编写测试用例（使用 `pytest`）。
- 编写了三类测试：
  - `tests/test_seed_db.py`：针对 `scripts/seed_db.py` 中的 `generate_slug` 函数编写纯函数测试，避免依赖数据库。
  - `tests/test_settings_json.py`：校验 `.vscode/settings.json` 中的 pytest 配置（存在时才校验）。
  - `tests/test_main.py`：对 `app/main.py` 多个接口编写集成风格测试，使用 `app.dependency_overrides` 注入 `FakeSession` 模拟数据库，避免触发真实 DB 连接。

---

## 🗓️ Day4.4：CI / 容器化与自动部署
- **目标**：每次推送代码到 GitHub 后自动运行测试、构建镜像并可选部署到远端服务器。

- **主要实现**：
  - 添加 `Dockerfile`（项目根或 `backend/Dockerfile`）用于构建运行镜像，运行命令为 `uvicorn app.main:app`。
  - 添加 GitHub Actions workflow：`.github/workflows/ci-cd.yml`，包含三个阶段：
    1. Run tests：安装依赖（`pip install -r requirements.txt`、`pytest`、`httpx` 等），并运行 `pytest -q`。
    2. Build and publish：用 `docker/build-push-action` 构建镜像并推送到 GHCR（使用 `GITHUB_TOKEN`）。
    3. Optional SSH deploy：通过 SSH 在目标服务器拉取镜像并启动容器（支持 `docker run` / `docker-compose`）。

- **CI 中的 PostgreSQL 处理**：
  - 因为 `app/main.py` 在导入时会触发 `Base.metadata.create_all(bind=engine)`，测试收集需要数据库可用；为保证 CI 独立性，workflow 在 `test` job 中直接用 `docker run` 启动一个 `postgres:15` 容器（`POSTGRES_USER=demo` / `POSTGRES_PASSWORD=demo` / `POSTGRES_DB=demo`），并通过小脚本循环尝试连接（使用 `psycopg2`）等待数据库就绪后再运行测试。
  - 这种做法不依赖 runner 预装服务，便于在任何 GitHub-hosted runner 上复现本地环境。

- **若干故障与修复记录（便于复盘）**：
  - 修复了 workflow 中错误的路径（最初错误地使用 `backend/requirements.txt`，但仓库根即为后端，导致 CI 找不到文件）；现在使用仓库根的 `requirements.txt`。
  - 因 FastAPI `TestClient` 需要 `httpx`，在 CI 安装步骤中加入 `pip install httpx`，避免导入时报错。
  - 为避免在解析 SQLAlchemy 表达式时引入脆弱的断言，测试对 DB 查询使用 `FakeSession` 和 `FakeQuery` 做可控模拟；对于搜索等复杂 `ilike` 表达式，测试断言为“期望条目存在”，而不是精确匹配 SQL 行为。

- **安全与 Secrets 配置**：
  - GHCR 推送使用 `GITHUB_TOKEN`（自动可用）。
  - 若使用 Docker Hub 请配置 `DOCKERHUB_USERNAME` 与 `DOCKERHUB_TOKEN`。
  - 自动 SSH 部署请在仓库 Secrets 中配置 `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`, `SSH_PORT`。

- **本地验证（Dry run）**：
  - 在本地执行过与 CI 相同的关键步骤（安装依赖、运行 pytest），确认测试在本地通过，这是一种常见的“干运行”实践，用于在提交到 CI 前尽量减少失败。

---

## 🗓️ 生产环境思考：数据库扩展与迁移
- **需求**
  - 在 `articles` 表中新增 `slug` 字段，用于生成唯一的文章 URL。

- **问题**
  - 修改模型后，数据库表结构未自动更新，导致 SQLAlchemy 查询时报错。

- **解决方案**
  - 学习并引入 **Alembic** 作为迁移工具。
  - 使用流程：
    1. `alembic init alembic` 初始化迁移环境。
    2. 配置数据库连接，导入 `Base.metadata`。
    3. 修改模型，新增字段。
    4. 执行 `alembic revision --autogenerate -m "add slug column"` 生成迁移脚本。
    5. 执行 `alembic upgrade head` 更新数据库结构。
  - 这样保证了生产环境下数据不丢失，结构变更可控。

---

## 🎯 最终成果
- 前端搜索框与后端 API 完成联调。
- 搜索结果能正确渲染在页面上，包括标题、摘要和标签。
- 数据库支持新增字段（如 `slug`），并通过 Alembic 管理迁移。
- 项目从 **前端交互 → 后端接口 → 数据库查询 → 页面渲染** 全链路打通。

---

## 📖 收获
- 理解了 Next.js 页面路由与 API 路由的区别。
- 掌握了 FastAPI 与 PostgreSQL 的基本联调。
- 解决了前端与后端数据结构不一致的问题，保证了渲染稳定性。
- 了解如何通过 Alembic 管理数据库迁移，避免手动改表。

