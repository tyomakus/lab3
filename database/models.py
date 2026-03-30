from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from database.sql_db import engine

Base = declarative_base()

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    articles = relationship("Article", back_populates="author")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True)
    articles = relationship("Article", back_populates="category")

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    publish_date = Column(Date, nullable=False)
    articles = relationship("Article", back_populates="issue")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    issue_id = Column(Integer, ForeignKey("issues.id"))
    created_at = Column(TIMESTAMP)

    author = relationship("Author", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    issue = relationship("Issue", back_populates="articles")