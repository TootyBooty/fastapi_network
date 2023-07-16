import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import constr


class CustomModel(BaseModel):
    class Config:
        orm_mode = True


class PostReaction(str, enum.Enum):
    LIKE = 'LIKE'
    DISLIKE = 'DISLIKE'


class PostCreate(CustomModel):
    title: constr(min_length=1, max_length=50)
    content: constr(min_length=1, max_length=5000)


class PostUpdate(CustomModel):
    title: Optional[constr(min_length=1, max_length=50)]
    content: Optional[constr(min_length=1, max_length=5000)]


class Post(PostCreate):
    post_id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime


class CountPostRate(BaseModel):
    like_count: int 
    dislike_count: int


class PostShow(Post):
    rate: CountPostRate


class PostOut(CustomModel):
    post_id: UUID


class UnratePost(BaseModel):
    user_id: UUID
    post_id: UUID


class RatePost(UnratePost):
    reaction: PostReaction


