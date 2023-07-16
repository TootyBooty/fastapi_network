from api.depends import get_user_repository
from api.depends import get_user_data_from_token
from schemas.user import UserCreate
from schemas.user import UserOut
from schemas.user import UserShow
from schemas.user import UserUpdate
from db.repositories.user import UserRepository
from permissions import is_owner
import exceptions as exc

from uuid6 import UUID

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Query
from fastapi import Path
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError


user_router = APIRouter()


@user_router.get("/", response_model=list[UserShow])
async def get_user_list(
    repo: UserRepository = Depends(get_user_repository),
    limit: int = Query(ge=1, default=50),
    offset: int = Query(ge=0, default=0),
):
    users = await repo.get_all_users(offset=offset, limit=limit)
    return [UserShow(**user.dict()) for user in users]


@user_router.get("/{user_id}/", response_model=UserShow)
async def get_user_by_id(
    user_id: UUID = Path(),
      repo: UserRepository = Depends(get_user_repository)
):
    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise exc.InvalidUserId
    return user


@user_router.get("/profile", response_model=UserShow)
async def get_user_by_email(
    email: EmailStr = Query(), repo: UserRepository = Depends(get_user_repository)
):
    user = await repo.get_user_by_email(email)
    if user is None:
        raise exc.InvalidUserId
    return user


@user_router.post("/", response_model=UserShow)
async def create_user(
    user_data: UserCreate = Body(), repo: UserRepository = Depends(get_user_repository)
):
    try:
        return await repo.create_user(user_data)
    except IntegrityError:
        raise exc.EmailAlreadyTaken


@user_router.patch("/", response_model=UserOut)
async def update_user_by_id(
    body: UserUpdate,
    current_user = Depends(get_user_data_from_token),
    target_user_id: UUID = Query(),
    repo: UserRepository = Depends(get_user_repository),
):
    target_user = await repo.get_user_by_id(user_id=target_user_id)
    if target_user is None:
        raise exc.InvalidUserId
    
    if not is_owner(current_user=current_user, target_user=target_user):
        raise exc.PermissionDenied

    update_data = body.dict(exclude_none=True)
    if update_data == {}:
        raise exc.EmptyUpdatedData

    try:
        updated_user_id = await repo.update_user(target_user_id, update_data)
    except IntegrityError:
        raise exc.EmailAlreadyTaken

    return UserOut(user_id=updated_user_id)


@user_router.delete("/", response_model=UserOut)
async def delete_user(
    current_user = Depends(get_user_data_from_token),
    target_user_id: UUID = Query(),
    repo: UserRepository = Depends(get_user_repository)
):
    target_user = await repo.get_user_by_id(user_id=target_user_id)
    if target_user is None:
        raise exc.InvalidUserId
    
    if not is_owner(current_user=current_user, target_user=target_user):
        raise exc.PermissionDenied
    
    deleted_user_id = await repo.delete_user(target_user_id)

    return UserOut(user_id=deleted_user_id)