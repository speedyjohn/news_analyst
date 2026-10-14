from app.models import User
from app.schemas.common import to_local


def user_public(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.public_name,
        "created_at": to_local(user.created_at),
    }
