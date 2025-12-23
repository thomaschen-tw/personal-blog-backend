# # backend/scripts/seed_db.py
# import random
# import re
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from app.model import Base, Article
#
# # 本地数据库连接字符串
# DATABASE_URL = "postgresql://demo:demo@localhost:5433/demo"
#
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine)
#
#
# def generate_slug(title: str) -> str:
#     """
#     从标题生成 slug（不包含 article 前缀）
#     例如: "article1" -> "article-1"
#     """
#     # 转换为小写
#     slug = title.lower()
#     # 替换空格为连字符
#     slug = re.sub(r'\s+', '-', slug)
#     # 移除特殊字符，只保留字母、数字和连字符
#     slug = re.sub(r'[^a-z0-9-]', '', slug)
#     # 移除连续的连字符
#     slug = re.sub(r'-+', '-', slug)
#     # 移除开头和结尾的连字符
#     slug = slug.strip('-')
#     return slug
#
#
# def seed(n=100):
#     # 创建表结构
#     Base.metadata.create_all(bind=engine)
#
#     session = SessionLocal()
#
#     # 清空表并重置序列
#     session.execute(text("TRUNCATE TABLE articles RESTART IDENTITY CASCADE;"))
#     session.commit()
#
#     # 再插入新数据
#     for i in range(n):
#         title = f"article{i + 1}"
#         exists = session.query(Article).filter_by(title=title).first()
#         if exists:
#             continue  # 已存在则跳过
#
#         # 生成 slug（不包含 article 前缀，例如: article1 -> article-1）
#         slug = generate_slug(title)
#
#         # 确保 slug 唯一（如果已存在，添加数字后缀）
#         base_slug = slug
#         counter = 1
#         while session.query(Article).filter_by(slug=slug).first():
#             slug = f"{base_slug}-{counter}"
#             counter += 1
#
#         a = Article(
#             title=title,
#             content="This is sample content about demo data. " * random.randint(3, 10),
#             tags="demo,example",
#             slug=slug  # 例如: article-1, article-2 等
#         )
#         session.add(a)
#
#     session.commit()
#     session.close()
#
#
# if __name__ == "__main__":
#     seed(100)  # 默认生成 100 条

# backend/scripts/seed_db.py
import random
import re
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.model import Base, Article

# 本地数据库连接字符串
DATABASE_URL = "postgresql://demo:demo@localhost:5433/demo"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def generate_slug(title: str, index: int) -> str:
    """
    从标题生成 slug，统一格式为 article-{index}
    例如: "Article 1" -> "article-1"
    """
    return f"article-{index}"


def seed(n=100):
    # 创建表结构
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # 清空表并重置序列
    session.execute(text("TRUNCATE TABLE articles RESTART IDENTITY CASCADE;"))
    session.commit()

    sample_tags = [
        "demo,example",
        "python,fastapi",
        "docker,ci",
        "database,postgres",
        "web,frontend",
        "backend,api"
    ]

    # 插入新数据
    for i in range(1, n + 1):
        title = f"article{i}"
        slug = generate_slug(title, i)

        # 确保 slug 唯一（如果已存在，添加数字后缀）
        base_slug = slug
        counter = 1
        while session.query(Article).filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        content = (
            f"This is sample content for article {i}. "
            * random.randint(2, 5)
        )

        a = Article(
            title=title,
            content=content,
            tags=random.choice(sample_tags),
            slug=slug,
            created_at = datetime.now(timezone.utc)
        )
        session.add(a)

    session.commit()
    session.close()


if __name__ == "__main__":
    seed(100)  # 默认生成 100 条
