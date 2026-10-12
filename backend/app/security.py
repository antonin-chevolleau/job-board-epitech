import hashlib
import hmac
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.clock import utcnow
from app.database import get_db
from app.models.auth import AuthSession
from app.models.person import Person, PersonRole

bearer = HTTPBearer(auto_error=False)
Db = Annotated[Session, Depends(get_db)]


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600_000)
    return f"pbkdf2_sha256$600000${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    _, iterations, salt, digest = stored.split("$")
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), int(iterations)
    )
    return hmac.compare_digest(actual.hex(), digest)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def optional_user(
    db: Db,
    authorization: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Person | None:
    if authorization is None:
        return None
    session = db.get(AuthSession, token_hash(authorization.credentials))
    if session is None or session.expires_at <= utcnow():
        raise HTTPException(401, "Session expirée. Reconnectez-vous.")
    person = db.get(Person, session.people_id)
    if person is None:
        raise HTTPException(401, "Compte introuvable.")
    return person


def current_user(person: Annotated[Person | None, Depends(optional_user)]) -> Person:
    if person is None:
        raise HTTPException(401, "Connexion nécessaire.")
    return person


def admin_user(person: Annotated[Person, Depends(current_user)]) -> Person:
    if person.role != PersonRole.admin:
        raise HTTPException(403, "Accès réservé aux administrateurs.")
    return person


User = Annotated[Person, Depends(current_user)]
Admin = Annotated[Person, Depends(admin_user)]
OptionalUser = Annotated[Person | None, Depends(optional_user)]
