import aiomcache
import json

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import Query
from fastapi import Path
from sqlalchemy.exc import IntegrityError

from api.depends import get_post_repository
from api.depends import get_user_data_from_token
from api.depends import get_cache_client

from schemas.post import PostCreate
from schemas.post import PostUpdate
from schemas.post import Post
from schemas.post import PostShow
from schemas.post import PostOut
from schemas.post import RatePost
from schemas.post import UnratePost
from schemas.post import PostReaction
from schemas.user import UserOut


from db.repositories.post import PostRepository
from permissions import is_owner
import exceptions as exc
from uuid6 import UUID


post_router = APIRouter()


@post_router.get("/", response_model=list[Post])
async def get_post_list(
    repo: PostRepository = Depends(get_post_repository),
    limit: int = Query(ge=1, default=50),
    offset: int = Query(ge=0, default=0),
):
    posts = await repo.get_post_list(offset=offset, limit=limit)
    return [Post(**post.dict()) for post in posts]


@post_router.get("/{post_id}/", response_model=PostShow)
async def get_post_by_id(
    post_id: UUID = Path(),
    repo: PostRepository = Depends(get_post_repository),
    cache: aiomcache.Client = Depends(get_cache_client)
):
    post = await repo.get_post_by_id(post_id)
    if post is None:
        raise exc.InvalidPostId
    
    cache_key = f'post_{post_id}'
    post_rate_str = await cache.get(cache_key)
    if post_rate_str:
        post_rate = json.loads(post_rate_str)
    else:
        post_rate = await repo.get_count_post_rate(post_id)
        post_rate_str = json.dumps(post_rate.dict())
        await cache.set(key=cache_key, value=post_rate_str, exptime=30)
    
    return PostShow(**post.dict(), rate=post_rate)


@post_router.post("/", response_model=Post)
async def create_post(
    current_user = Depends(get_user_data_from_token),
    post_data: PostCreate = Body(),
    repo: PostRepository = Depends(get_post_repository)
):
    try:
        return await repo.create_post(current_user.user_id, post_data)
    except IntegrityError:
        raise exc.EmailAlreadyTaken


@post_router.patch("/", response_model=PostOut)
async def update_post_by_id(
    body: PostUpdate,
    current_user = Depends(get_user_data_from_token),
    post_id: UUID = Query(),
    repo: PostRepository = Depends(get_post_repository)
):
    post = await repo.get_post_by_id(post_id)
    if post is None:
        raise exc.InvalidUserId

    if not is_owner(current_user=current_user, target_user=UserOut(user_id=post.author_id)):
        raise exc.PermissionDenied

    update_data = body.dict(exclude_none=True)
    if update_data == {}:
        raise exc.EmptyUpdatedData

    updated_post_id = await repo.update_post(post_id, update_data)

    return PostOut(post_id=updated_post_id)


@post_router.delete("/", response_model=PostOut)
async def delete_post(
    current_user = Depends(get_user_data_from_token),
    post_id: UUID = Query(),
    repo: PostRepository = Depends(get_post_repository)
):
    post = await repo.get_post_by_id(post_id)
    if post is None:
        raise exc.InvalidPostId

    if not is_owner(current_user=current_user, target_user=UserOut(user_id=post.author_id)):
        raise exc.PermissionDenied

    deleted_post_id = await repo.delete_post(post_id)

    return PostOut(post_id=deleted_post_id)


@post_router.post("/{post_id}/rate/", response_model=PostOut)
async def add_post_rating(
    current_user = Depends(get_user_data_from_token),
    post_id: UUID = Path(),
    reaction: PostReaction = Body(),
    repo: PostRepository = Depends(get_post_repository)
):
    post = await repo.get_post_by_id(post_id=post_id)
    if post is None:
        raise exc.InvalidPostId
    if post.author_id == current_user.user_id:
        raise exc.ReactionOwnPost
    
    post_rate = RatePost(user_id=current_user.user_id,
                         post_id=post_id,
                         reaction=reaction)
    
    return await repo.rate_post(post_rate)


@post_router.delete("/{post_id}/rate/", response_model=PostOut)
async def delete_post_rating(
    current_user = Depends(get_user_data_from_token),
    post_id: UUID = Path(),
    repo: PostRepository = Depends(get_post_repository)
):
    post = await repo.get_post_by_id(post_id=post_id)
    if post is None:
        raise exc.InvalidPostId
    
    post_rate = UnratePost(user_id=current_user.user_id, post_id=post_id,)
    
    return await repo.unrate_post(post_rate)
