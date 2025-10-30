from .schemas import UserResponse
from .models import User


class UserMapper:
    @staticmethod
    def to_user_response(user: User) -> UserResponse:
       return UserResponse.model_validate(user)
