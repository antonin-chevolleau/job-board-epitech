import secrets
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select

from app.clock import utcnow
from app.config import settings
from app.models.auth import AuthSession, Credential
from app.models.person import Person
from app.schemas.auth import AccountUpdate, Login, LoginRead, Register
from app.schemas.person import PersonRead
from app.security import Db, User, bearer, hash_password, token_hash, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])
# Same expensive operation even for unknown accounts, avoiding a trivial timing oracle.
DUMMY_HASH = hash_password("not-a-real-account-password")


@router.post("/register", response_model=PersonRead, status_code=201)
def register(payload: Register, db: Db):
    email = payload.email.lower()
    if db.scalar(select(Person).where(Person.email == email)):
        raise HTTPException(
            409,
            "Cette adresse est déjà utilisée. "
            "Connectez-vous ou contactez l’administrateur.",
        )
    person = Person(**payload.model_dump(exclude={"password", "email"}), email=email)
    db.add(person)
    db.flush()
    db.add(
        Credential(people_id=person.id, password_hash=hash_password(payload.password))
    )
    db.commit()
    db.refresh(person)
    return person


@router.post("/login", response_model=LoginRead)
def login(payload: Login, db: Db):
    person = db.scalar(select(Person).where(Person.email == payload.email.lower()))
    credential = db.get(Credential, person.id) if person else None
    valid = verify_password(
        payload.password, credential.password_hash if credential else DUMMY_HASH
    )
    if not credential or not valid:
        raise HTTPException(401, "Email ou mot de passe incorrect.")
    token = secrets.token_urlsafe(32)
    db.add(
        AuthSession(
            token_hash=token_hash(token),
            people_id=person.id,
            expires_at=utcnow() + timedelta(hours=settings.session_hours),
        )
    )
    db.commit()
    return {"access_token": token, "user": person}


@router.get("/me", response_model=PersonRead)
def me(user: User):
    return user


@router.patch("/me", response_model=PersonRead)
def update_me(payload: AccountUpdate, user: User, db: Db):
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is None and field != "phone":
            raise HTTPException(422, f"{field} ne peut pas être null.")
        setattr(user, field, value.lower() if field == "email" else value)
    db.commit()
    db.refresh(user)
    return user


@router.post("/logout", status_code=204)
def logout(
    user: User,
    db: Db,
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
):
    session = db.get(AuthSession, token_hash(authorization.credentials))
    db.delete(session)
    db.commit()
    return Response(status_code=204)
