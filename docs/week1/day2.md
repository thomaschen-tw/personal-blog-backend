
# 📘 Day 2 工作文档

## 🧠 思考过程
- 我需要为 **personal-blog** 项目搭建一个后端环境。  
- 目标是使用 **FastAPI + SQLAlchemy + Postgres**，并且能通过脚本往数据库里插入测试数据。  
- 我发现自己有多个 Python 环境（系统自带、Homebrew、pyenv、Miniconda），导致包引入混乱。  
- 决定以后只用 **Homebrew Python 3.13**，并且用 `venv` 来管理虚拟环境，避免 conda 干扰。  
- 数据库部分用 Docker 启动 Postgres，避免在本机安装和冲突。  

---

## ⚙️ 操作步骤

### 1. 清理环境
- 删除旧的虚拟环境：
  ```bash
  rm -rf backend/.venv
  ```
- 确认 Python 版本：
  ```bash
  which python3
  python3 --version
  ```
  → 使用 Homebrew 的 Python 3.13。

### 2. 创建虚拟环境
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```
验证：
```bash
which python
```
→ 指向 `backend/.venv/bin/python`。

### 3. 安装依赖
```bash
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic
pip freeze > requirements.txt
```

### 4. 配置数据库（Docker）
在 `backend/docker-compose.yaml` 写入：
```yaml
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
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

启动：
```bash
docker compose up -d
```

### 5. 测试数据库连接
进入容器：
```bash
docker exec -it demo-postgres psql -U demo -d demo
```
在 psql 中：
```sql
\dt   -- 查看表
```

### 6. 编写数据模型
在 `backend/app/models.py`：
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 7. 编写数据填充脚本
在 `backend/scripts/seed_db.py`：
```python
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.model import Base, Article

DATABASE_URL = "postgresql://demo:demo@localhost:5433/demo"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed(n=100):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    for i in range(n):
        a = Article(
            title=f"Sample Article {i}",
            content="This is sample content about demo data. " * random.randint(3, 10),
            tags="demo,example"
        )
        session.add(a)
    session.commit()
    session.close()

if __name__ == "__main__":
    seed(100)
```

运行：
```bash
cd backend
python -m scripts.seed_db
```

### 8. 验证数据
进入 psql：
```sql
SELECT * FROM articles LIMIT 5;
```
→ 可以看到插入的测试数据。


### 9. 目录结构标准化
```
backend/
├── app/
│   ├── __init__.py
│   ├── models.py
│   └── main.py
├── scripts/
│   └── seed_db.py
├── requirements.txt
└── docker-compose.yaml
```

---

## 📌 Day 2 总结
- 明确了环境混乱的原因：多个 Python 版本和 Miniconda 干扰。  
- 决定以后只用 **Homebrew Python 3.13 + venv**。  
- 成功搭建了 FastAPI + SQLAlchemy + Postgres 的基本后端环境。  
- 写好了 `Article` 模型和 `seed_db.py` 脚本，并成功插入测试数据。  

---



