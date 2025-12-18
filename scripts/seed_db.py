# backend/scripts/seed_db.py
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.model import Base, Article

# 本地数据库连接字符串
DATABASE_URL = "postgresql://demo:demo@localhost:5433/demo"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed(n=100):
    # 创建表结构
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # 清空表并重置序列
    session.execute(text("TRUNCATE TABLE articles RESTART IDENTITY CASCADE;"))
    session.commit()

    # 再插入新数据
    for i in range(n):
        title = f"Sample Article {i+1}"
        exists = session.query(Article).filter_by(title=title).first()
        if exists:
            continue  # 已存在则跳过
        a = Article(
            title=title,
            content="This is sample content about demo data. " * random.randint(3, 10),
            tags="demo,example"
        )
        session.add(a)

    session.commit()
    session.close()


if __name__ == "__main__":
    seed(100)  # 默认生成 100 条
