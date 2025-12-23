# Personal Blog Backend

基于 FastAPI 的个人博客后端。

推荐架构概览
前端 Next.js NotionNext 模板：搜索 UI、保存按钮、触发工作流按钮。

后端 FastAPI：提供 /search、/posts（CRUD）、/workflow/trigger（可选代理）等接口，负责 DB 读写与对 n8n 的 webhook 调用。

数据库 PostgreSQL：存储文章、工作流日志表（可选）。

工作流引擎 n8n 自托管：接收 webhook、调用后端 API、发送邮件、写入 DB、调用外部服务。

本地编排 docker‑compose：frontend, backend, postgres, n8n, mailhog（用于本地邮件测试）。

K8s 练习 kind 或 minikube：部署同样组件的 manifests 或 Helm chart。

CI/CD GitHub Actions：build → push → deploy（到 kind 或云）。

Infra as Code Terraform：可选，写最小 plan（ECR/ECS/EKS/RDS）。

**4 周详细日程 (12/15–1/14)**，已经调整好顺序。

---

# 📅 四周详细日程 (12/15–1/14)

## 第1周 Day 1–5 基础骨架与搜索功能
- **Day 1** 仓库初始化，Fork NotionNext，创建 backend skeleton，写 README。  
- **Day 2** 设计 Postgres schema，写 `seed_db.py` 生成 100 条文章。  
- **Day 3** 实现 FastAPI `/search`（全文或 LIKE），本地联调。  
- **Day 4** 在 NotionNext 前端添加搜索页面并调用 `/search`。  
- **Day 5** 实现 `/posts` 创建接口并联调前端保存按钮（先不触发 n8n）。  

---

## 第2周 Day 6–10 K8s 本地部署与 CI 初版
- **Day 6** 安装并配置 kind，创建本地 K8s 集群。  
- **Day 7** 编写 K8s manifests 或 Helm chart（frontend/backend/postgres/n8n）。  
- **Day 8** 在 kind 上部署并调试 Ingress 或 port-forward。  
- **Day 9** 编写 GitHub Actions：build images → push to GHCR → deploy to kind。  
- **Day 10** 在 CI 中加入后端测试步骤，做一次代码变更触发 CI 并验证自动部署。  

---

## 第3周 Day 11–15 容器化与 n8n 集成
- **Day 11** 为 frontend/backend/postgres 写 Dockerfile。  
- **Day 12** 搭建 docker-compose（含 n8n、mailhog），本地一键启动。  
- **Day 13** 在 n8n 中创建 webhook 工作流：HTTP Trigger → HTTP Request to backend → DB write → Email。  
- **Day 14** 修改后端在创建文章后调用 n8n webhook。  
- **Day 15** 本地端到端测试并修复 CORS、网络问题，增加工作流分支逻辑（publish vs save），在前端展示工作流状态。  

---

## 第4周 Day 16–20 云上准备与演示完善
- **Day 16** 编写 Terraform 最小模块（只做 plan）。  
- **Day 17** 将 CI 的 deploy 步骤扩展为可选云部署（用 env 切换）。  
- **Day 18** 若可上云，短期部署到 ECS Fargate 或 EKS（优先 ECS 以节省时间）；否则录屏 `terraform apply` 流程。  
- **Day 19** 配置 Route53 子域名或记录 DNS 步骤。  
- **Day 20** 加入基本监控或健康检查，准备 PPT、演示脚本、FAQ，并彩排录制 5–8 分钟最终演示视频，整理仓库交付物。  

---

# ⚠️ 常见踩坑点总结

- **数据库连接**：容器内不能用 `localhost:5433` 访问宿主机数据库，需用 `host.docker.internal` 或 Compose 服务名。  
- **镜像构建**：M1/M2 Mac 需构建多平台镜像 (`linux/amd64,linux/arm64`)，否则拉取时报 `manifest not found`。  
- **GHCR 权限**：默认私有，需登录或改为 Public；推送用 `GITHUB_TOKEN`。  
- **CI 测试**：FastAPI `TestClient` 依赖 `httpx`，必须在 CI 安装。  
- **K8s 部署**：Ingress 配置容易出错，建议先用 `port-forward` 验证服务可用。  
- **n8n 集成**：CORS 与网络配置是常见问题，需在后端允许跨域。  
- **Terraform**：初学者容易直接 `apply`，建议先 `plan`，避免误操作。


Day1:
git clone https://github.com/thomaschen-tw/NotionNext.git
cd personal-blog/backend
python -m venv .venv
mac:source 
    .venv/bin/activate
windows:
    .venv\Scripts\Activate.ps1

pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic
pip freeze > requirements.txt

第一周交付清单
frontend/ 能在 http://localhost:3000/search 搜索并显示结果。

backend/ 提供 /search 与 /posts 接口并在 http://localhost:8000/docs 可查看 OpenAPI（FastAPI 自动生成）。

scripts/seed_db.py 能生成 50–200 条测试数据。

README 包含一键启动步骤、已知问题与解决办法、下一步计划。

3 分钟录屏演示（搜索流程 + 数据生成 + 简短问题总结）。