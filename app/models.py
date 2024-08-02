from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Interval
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    auto_reply_enabled = Column(Boolean, default=False)
    auto_reply_delay = Column(Interval)

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="author")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_blocked = Column(Boolean, default=False)

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow())
    is_blocked = Column(Boolean, default=False)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


class ScheduledReply(Base):
    __tablename__ = 'scheduled_replies'

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey('comments.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    reply_text = Column(String, nullable=True)
    scheduled_time = Column(DateTime, default=datetime.utcnow)
    sent = Column(Boolean, default=False)

    comment = relationship("Comment")
    post = relationship("Post")
    user = relationship("User")
