from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentClaims, UserServiceDependency
from app.schemas.users import ProfileUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user(
    claims: CurrentClaims,
    service: UserServiceDependency,
) -> UserResponse:
    user_id = UUID(claims["sub"])
    profile = service.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    return UserResponse(**profile.__dict__)


@router.patch("/me", response_model=UserResponse)
def update_current_user(
    payload: ProfileUpdate,
    claims: CurrentClaims,
    service: UserServiceDependency,
) -> UserResponse:
    user_id = UUID(claims["sub"])
    profile = service.update_display_name(user_id, payload.display_name)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    return UserResponse(**profile.__dict__)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    claims: CurrentClaims,
    service: UserServiceDependency,
) -> UserResponse:
    if claims["sub"] != str(user_id) and claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's profile",
        )
    profile = service.get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    return UserResponse(**profile.__dict__)
