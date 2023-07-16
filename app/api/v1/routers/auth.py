from api.depends import get_user_repository
from core.security import verify_password
from core.security import create_access_token
from db.repositories.user import UserRepository
from exceptions import CredentialsException
from fastapi import APIRouter
from fastapi import Depends

from schemas.auth import Token
from core.security import create_access_token
from fastapi.security import OAuth2PasswordRequestForm


auth_router = APIRouter()


@auth_router.post("/token")
async def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: UserRepository = Depends(get_user_repository)
):
    user = await repo.get_user_by_email(form_data.username)

    if user is None:
        raise CredentialsException

    if not verify_password(form_data.password, user.password):
        raise CredentialsException


    access_token = create_access_token(
        data={"sub": user.email,
              'user_id': user.user_id.hex}
    )

    return Token(access_token=access_token, token_type="bearer")