from typing import List
from pydantic import BaseModel
from datetime import date


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int
    comments: List['Comment'] = []

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    author_id: int
    post_id: int
    is_blocked: bool

    class Config:
        orm_mode = True


class CommentDailyBreakdown(BaseModel):
    date: date
    total_comments: int
    blocked_comments: int

    class Config:
        orm_mode = True


class CommentResponse(BaseModel):
    id: int
    author_id: int
    content: str
    post_id: int


Post.update_forward_refs()