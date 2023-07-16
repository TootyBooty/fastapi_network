from typing import Union

from schemas.user import UserCreate
from schemas.user import UserShow
from core.security import get_password_hash
from db.repositories.base import BaseRepository
from db.models import User

from uuid6 import UUID
from uuid6 import uuid6

from sqlmodel import and_
from sqlmodel import select
from sqlmodel import update


class UserRepository(BaseRepository):
    async def get_all_users(self, offset, limit):
        async with self.session.begin():
            query = select(User).offset(offset).limit(limit)
            res = await self.session.execute(query)
            users = res.scalars().all()
            return users

    async def create_user(self, user: UserCreate) -> UserShow:
        async with self.session.begin():
            new_user = User(
                user_id=uuid6(),
                name=user.name,
                surname=user.surname,
                email=user.email,
                password=get_password_hash(user.password),
            )
            self.session.add(new_user)
            return UserShow(
                user_id=new_user.user_id,
                name=new_user.name,
                surname=new_user.surname,
                email=new_user.email,
                is_active=new_user.is_active,
                updated_at=new_user.updated_at,
                created_at=new_user.created_at
            )

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        async with self.session.begin():
            query = select(User).where(User.user_id == user_id)
            res = await self.session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        async with self.session.begin():
            query = select(User).where(User.email == email)
            res = await self.session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]

    async def update_user(self, user_id: UUID, update_data) -> Union[UUID, None]:
        async with self.session.begin():
            query = (
                update(User)
                .where(and_(User.user_id == user_id, User.is_active == True))
                .values(update_data)
                .returning(User.user_id)
            )
            res = await self.session.execute(query)
            update_user_id_row = res.fetchone()
            if update_user_id_row is not None:
                return update_user_id_row[0]

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        async with self.session.begin():
            query = (
                update(User)
                .where(and_(User.user_id == user_id, User.is_active == True))
                .values(is_active=False)
                .returning(User.user_id)
            )
            res = await self.session.execute(query)
            deleted_user_id_row = res.fetchone()
            if deleted_user_id_row is not None:
                return deleted_user_id_row[0]
