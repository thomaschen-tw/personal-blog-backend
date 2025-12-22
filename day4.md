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
- 针对数据库参数和接口编写测试用例
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

