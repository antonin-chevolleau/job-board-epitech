from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, DbSession
from app.api.errors import commit
from app.api.rate_limit import login_rate_limit
from app.core.security import (
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas import ProfileUpdate, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, db: DbSession):
    """Create a plain `user` account (roles are only granted by an admin)."""
    user = User(
        **data.model_dump(exclude={"password"}),
        hashed_password=hash_password(data.password),
        role="user",
    )
    db.add(user)
    commit(db)
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenOut,
    dependencies=[Depends(login_rate_limit)],
    responses={429: {"description": "Too many login attempts from this IP"}},
)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    """Log in with `username` (user_name or email) and `password`."""
    user = db.scalar(
        select(User).where(
            or_(User.user_name == form.username, User.email == form.username)
        )
    )
    hashed_password = user.hashed_password if user else DUMMY_HASH
    if not verify_password(form.password, hashed_password) or user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenOut(
        access_token=create_access_token(user.id, user.role),
        role=user.role,
        user_id=user.id,
    )


@router.get("/me", response_model=UserOut)
def read_me(user: CurrentUser):
    return user


@router.put("/me", response_model=UserOut)
def update_me(data: ProfileUpdate, user: CurrentUser, db: DbSession):
    """Update the authenticated user's profile and, optionally, password."""
    if data.new_password:
        if not data.current_password or not verify_password(
            data.current_password, user.hashed_password
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Current password is incorrect"
            )
        user.hashed_password = hash_password(data.new_password)
    for field in ("user_name", "first_name", "last_name", "email", "phone"):
        setattr(user, field, getattr(data, field))
    commit(db)
    db.refresh(user)
    return user
