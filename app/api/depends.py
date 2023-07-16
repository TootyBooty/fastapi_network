from fastapi.security import OAuth2PasswordBearer
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException

from jose import jwt
from jose import JWTError

from schemas.user import UserOutLogin
from core.config import Config
from db.repositories.user import UserRepository
from db.repositories.post import PostRepository
from db.session import get_session

from cache.memcached import MemcachedState

import exceptions as exc
from uuid6 import UUID


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=Config.TOKEN_URL)


async def get_user_repository(session=Depends(get_session)) -> UserRepository:
    return UserRepository(session)


async def get_post_repository(session=Depends(get_session)) -> PostRepository:
    return PostRepository(session)


async def get_authorized_user(authorized_user=Body()):
    if not authorized_user:
        raise HTTPException(status_code=400, detail="user not authorized.")
    user_data = authorized_user.get("authorized_user")
    return {"email": user_data.get("email")}


async def get_user_data_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        email: str = payload.get("sub")
        user_id: UUID = payload.get('user_id')
        if not(email or user_id):
            raise exc.CredentialsException
    except JWTError:
        raise exc.CredentialsException
    return UserOutLogin(user_id=user_id, email=email)


async def get_cache_client():
    return MemcachedState()