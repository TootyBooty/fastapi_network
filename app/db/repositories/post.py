from typing import Union

from schemas.post import PostCreate
from schemas.post import PostOut
from schemas.post import UnratePost
from schemas.post import RatePost
from schemas.post import CountPostRate

from db.repositories.base import BaseRepository
from db.models import Post
from db.models import UserPostRate

from uuid6 import UUID
from uuid6 import uuid6

from sqlmodel import select
from sqlmodel import update
from sqlmodel import delete
from sqlmodel import and_
from sqlmodel import func
from sqlmodel import case


class PostRepository(BaseRepository):
    async def get_post_list(self, offset, limit):
        async with self.session.begin():
            query = select(Post).offset(offset).limit(limit)
            res = await self.session.execute(query)
            users = res.scalars().all()
            return users


    async def create_post(self, author_id, post: PostCreate) -> Post:
        async with self.session.begin():
            new_post = Post(
                post_id=uuid6(),
                author_id=author_id,
                title=post.title,
                content=post.content,
            )
            self.session.add(new_post)
            return new_post


    async def get_post_by_id(self, post_id: UUID) -> Union[Post, None]:
        async with self.session.begin():
            query = select(Post).where(Post.post_id == post_id)
            res = await self.session.execute(query)
            post_row = res.fetchone()
            if post_row is not None:
                return post_row[0]


    async def update_post(self, post_id: UUID, update_data) -> Union[UUID, None]:
        async with self.session.begin():
            query = (
                update(Post)
                .where(Post.post_id == post_id)
                .values(update_data)
                .returning(Post.post_id)
            )
            res = await self.session.execute(query)
            update_post_id_row = res.fetchone()
            if update_post_id_row is not None:
                return update_post_id_row[0]


    async def delete_post(self, post_id: UUID) -> Union[UUID, None]:
        async with self.session.begin():
            query = (
                delete(Post)
                .where(Post.post_id == post_id)
            )
            res = await self.session.execute(query)
            if res:
                return post_id
            

    async def rate_post(self, post_rate: RatePost) -> PostOut:
        async with self.session.begin():
            new_reaction = UserPostRate(
                user_id=post_rate.user_id,
                post_id=post_rate.post_id,
                reaction=post_rate.reaction,
            )
            await self.session.merge(new_reaction)
            return PostOut(post_id=post_rate.post_id)


    async def unrate_post(self, post_rate: UnratePost) -> Union[PostOut, None]:
        async with self.session.begin():
            query = (
                delete(UserPostRate)
                .where(
                    and_(
                        UserPostRate.user_id == post_rate.user_id,
                        UserPostRate.post_id == post_rate.post_id,
                    )
                )
            )
            res = await self.session.execute(query)
            if res:
                return PostOut(post_id=post_rate.post_id)


    async def get_count_post_rate(self, post_id: UUID) -> CountPostRate:

        query = (
            select(
                UserPostRate.post_id,
                func.count(case([(UserPostRate.reaction == 'LIKE', 1)])).label('like_count'),
                func.count(case([(UserPostRate.reaction == 'DISLIKE', 1)])).label('dislike_count')
            )
            .where(UserPostRate.post_id == post_id)
            .group_by(UserPostRate.post_id)
        )
        res = await self.session.execute(query)
        row = res.fetchone()
        return CountPostRate(
            like_count=row.like_count,
            dislike_count=row.dislike_count
        )

