from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select

from app.api.deps import AdminUser, DbSession, require_admin
from app.api.errors import commit, get_or_404
from app.api.pagination import PageQuery, paginate
from app.core.security import hash_password
from app.models import User
from app.schemas import Page, UserCreate, UserOut, UserRole, UserUpdate

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(require_admin)]
)


@router.get("", response_model=Page[UserOut])
def list_users(
    db: DbSession,
    params: PageQuery,
    q: str | None = None,
    role: UserRole | None = None,
    company_id: int | None = None,
):
    """List users; `q` searches user name, first/last name and email."""
    stmt = select(User)
    if q:
        stmt = stmt.where(
            or_(
                User.user_name.contains(q, autoescape=True),
                User.first_name.contains(q, autoescape=True),
                User.last_name.contains(q, autoescape=True),
                User.email.contains(q, autoescape=True),
            )
        )
    if role:
        stmt = stmt.where(User.role == role)
    if company_id:
        stmt = stmt.where(User.company_id == company_id)
    return paginate(db, stmt.order_by(User.id), params)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: DbSession):
    return get_or_404(db, User, user_id)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: DbSession):
    values = data.model_dump(exclude={"password"})
    user = User(**values, hashed_password=hash_password(data.password))
    db.add(user)
    commit(db)
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: DbSession, admin: AdminUser):
    user = get_or_404(db, User, user_id)
    if user.id == admin.id and data.role != "admin":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "You cannot remove your own admin role"
        )
    for field, value in data.model_dump(exclude={"password"}).items():
        setattr(user, field, value)
    if data.password:
        user.hashed_password = hash_password(data.password)
    commit(db)
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbSession, admin: AdminUser):
    if user_id == admin.id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "You cannot delete your own account"
        )
    db.delete(get_or_404(db, User, user_id))
    commit(db)
