from fastapi import APIRouter
from fastapi import FastAPI

from api.routers import v1_router


app = FastAPI()


main_api_router = APIRouter()

main_api_router.include_router(v1_router)


app.include_router(main_api_router)