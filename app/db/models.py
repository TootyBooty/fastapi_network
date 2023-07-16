from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field
from sqlmodel import SQLModel, Column, DateTime, Relationship
from sqlmodel import Enum

from schemas.post import PostReaction
from utils import get_current_time


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: Optional[UUID] = Field(default=None, primary_key=True)
    name: str = Field(max_length=15)
    surname: str = Field(max_length=15)
    email: EmailStr = Field(unique=True)
    password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default=get_current_time())
    updated_at: datetime = Field(default=get_current_time(), sa_column=Column(DateTime, onupdate=get_current_time))
    rated_posts: list['UserPostRate'] = Relationship(back_populates='user')

class Post(SQLModel, table=True):
    __tablename__ = "posts"

    post_id: Optional[UUID] = Field(default=None, primary_key=True)
    author_id: Optional[UUID] = Field(default=None, foreign_key='users.user_id')
    title: str = Field(max_length=50)
    content: str = Field(max_length=5000)
    created_at: datetime = Field(default=get_current_time())
    updated_at: datetime = Field(default=get_current_time(), sa_column=Column(DateTime, onupdate=get_current_time))
    rated_users: list['UserPostRate'] = Relationship(back_populates='post')


class UserPostRate(SQLModel, table=True):
    __tablename__ = "user_posts_likes"

    user_id: Optional[UUID] = Field(
        default=None, foreign_key='users.user_id', primary_key=True
    )
    post_id: Optional[UUID] = Field(
        default=None, foreign_key='posts.post_id', primary_key=True
    )
    reaction: Optional[PostReaction] = Field(
        sa_column=Column(Enum(PostReaction)),
    )

    user: "User" = Relationship(back_populates="rated_posts")
    post: "Post" = Relationship(back_populates="rated_users")

