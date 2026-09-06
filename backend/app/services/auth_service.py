from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, UserRegister
from app.core.security import create_access_token, hash_password, verify_password


class UserAlreadyExistsError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


class AuthService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def register(self, db: Session, data: UserRegister) -> User:
        if self.repository.get_by_user_name(db, data.user_name) is not None:
            raise UserAlreadyExistsError("Unable to create account with these details.")
        user = User(
            user_name=data.user_name,
            pass_hash=hash_password(data.password),
            age=data.age,
            gender=data.gender,
        )
        return self.repository.create(db, user)

    def login(self, db: Session, data: LoginRequest) -> str:
        user = self.repository.get_by_user_name(db, data.user_name)
        if user is None or not verify_password(data.password, user.pass_hash):
            raise InvalidCredentialsError("Invalid username or password.")
        return create_access_token(user.user_id)

    def get_current_user(self, db: Session, user_id):
        user = self.repository.get_by_id(db, user_id)
        if user is None:
            raise InvalidCredentialsError("Invalid authentication credentials.")
        return user
