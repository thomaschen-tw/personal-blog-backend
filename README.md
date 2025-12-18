# Personal Blog Backend

基于 FastAPI 的个人博客后端。

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


Day2

1. 删除旧的虚拟环境
bash
cd ~/aiTools/personal-blog/backend
rm -rf .venv
2. 用系统 Python 创建新的虚拟环境
（不要用 Miniconda 的 Python，直接指定系统 Python 路径）

bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m venv .venv
3. 激活虚拟环境
bash
source .venv/bin/activate
检查是否正确：

bash
which python
应该显示：

Code
.../personal-blog/backend/.venv/bin/python
4. 安装依赖
bash
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic
5. 更新 requirements.txt
bash
pip freeze > requirements.txt
6. 启动 Postgres 容器（docker-compose）
在 backend/ 下创建 docker-compose.yaml：

yaml
version: "3.9"

services:
  postgres-demo:
    image: postgres:15-alpine
    container_name: demo-postgres
    restart: always
    environment:
      POSTGRES_USER: demo
      POSTGRES_PASSWORD: demo
      POSTGRES_DB: demo
    ports:
      - "5433:5432"   # 宿主机用 5433，避免和已有 Postgres 冲突
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
启动：

bash
docker compose up -d
7. 测试数据库连接
进入容器：

bash
docker exec -it demo-postgres psql -U demo -d demo
在 psql 里：

sql
\dt   -- 查看表
此时应该还没有表。

8. 运行 seed 脚本
bash
python backend/scripts/seed_db.py
9. 再次验证
进入容器：

bash
docker exec -it demo-postgres psql -U demo -d demo
在 psql 里：

sql
\dt
SELECT * FROM articles LIMIT 5;


本周交付清单（必须完成）
frontend/ 能在 http://localhost:3000/search 搜索并显示结果。

backend/ 提供 /search 与 /posts 接口并在 http://localhost:8000/docs 可查看 OpenAPI（FastAPI 自动生成）。

scripts/seed_db.py 能生成 50–200 条测试数据。

README 包含一键启动步骤、已知问题与解决办法、下一步计划。

3 分钟录屏演示（搜索流程 + 数据生成 + 简短问题总结）。