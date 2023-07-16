from fastapi import APIRouter

from api.v1.routers.auth import auth_router
from api.v1.routers.user import user_router
from api.v1.routers.post import post_router


v1_router = APIRouter(prefix='/api/v1', tags=['v1'])

v1_router.include_router(auth_router, prefix="/login", tags=["login"])
v1_router.include_router(user_router, prefix='/user', tags=['user'])
v1_router.include_router(post_router, prefix='/post', tags=['post'])
