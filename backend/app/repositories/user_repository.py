from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def get_by_id(self, db: Session, user_id):
        return db.scalar(select(User).where(User.user_id == user_id))

    def get_by_user_name(self, db: Session, user_name: str):
        return db.scalar(select(User).where(User.user_name == user_name))

    def create(self, db: Session, user: User) -> User:
        db.add(user)
        db.flush()
        return user
