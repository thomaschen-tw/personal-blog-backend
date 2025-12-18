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

4 周详细日程 12/15–1/14 每日任务（每天 6–8 小时）
第一周 Day 1–7 基础骨架与搜索功能
Day 1 仓库初始化，Fork NotionNext，创建 backend skeleton，写 README。

Day 2 设计 Postgres schema，写 seed_db.py 生成 100 条文章。

Day 3 实现 FastAPI /search（全文或 LIKE），本地联调。

Day 4 在 NotionNext 前端添加搜索页面并调用 /search。

Day 5 实现 /posts 创建接口并联调前端保存按钮（先不触发 n8n）。

Day 6 写后端单元测试，准备 demo 脚本。

Day 7 本地演示并录制 3 分钟视频。

第二周 Day 8–14 容器化与 n8n 集成
Day 8 为 frontend/backend/postgres 写 Dockerfile。

Day 9 搭建 docker-compose（含 n8n、mailhog），本地一键启动。

Day 10 在 n8n 中创建 webhook 工作流：HTTP Trigger → HTTP Request to backend → DB write → Email。

Day 11 修改后端在创建文章后调用 n8n webhook。

Day 12 本地端到端测试并修复 CORS、网络问题。

Day 13 增加工作流分支逻辑（publish vs save），在前端展示工作流状态。

Day 14 录制 4–6 分钟端到端演示并更新 README。

第三周 Day 15–21 K8s 本地部署与 CI 初版
Day 15 安装并配置 kind，创建集群。

Day 16 编写 k8s manifests 或 Helm chart（frontend/backend/postgres/n8n）。

Day 17 在 kind 上部署并调试 Ingress 或 port-forward。

Day 18 编写 GitHub Actions：build images → push to GHCR → deploy to kind。

Day 19 在 CI 中加入后端测试步骤。

Day 20 做一次代码变更触发 CI 并验证自动部署。

Day 21 录制 2 分钟展示 CI 与 K8s 部署流程。

第四周 Day 22–31 云上准备与演示完善
Day 22 编写 Terraform 最小模块（只做 plan）。

Day 23 将 CI 的 deploy 步骤扩展为可选云部署（用 env 切换）。

Day 24 若可上云，短期部署到 ECS Fargate 或 EKS（优先 ECS 以节省时间）；否则录屏 terraform apply 流程。

Day 25 配置 Route53 子域名或记录 DNS 步骤。

Day 26 加入基本监控或健康检查。

Day 27–29 准备 PPT、演示脚本、FAQ。

Day 30–31 彩排并录制 5–8 分钟最终演示视频，整理仓库交付物。

项目结构建议
personal-blog/
├─ frontend/                # NotionNext fork
│  ├─ package.json
│  └─ ... 
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ crud.py
│  │  └─ db.py
│  ├─ scripts/
│  │  └─ seed_db.py
│  ├─ requirements.txt
│  └─ Dockerfile (optional)
├─ docker-compose.yml (later)
└─ README.md


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