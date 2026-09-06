from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.auth import UserProfileResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
def get_current_user(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> UserProfileResponse:
    user = AuthService().get_current_user(db, user_id)
    return UserProfileResponse.model_validate(user)
