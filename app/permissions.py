from schemas.user import UserOutLogin
from schemas.user import UserShow


def is_owner(
    current_user: UserOutLogin,
    target_user: UserShow,
):
    return current_user.user_id == target_user.user_id