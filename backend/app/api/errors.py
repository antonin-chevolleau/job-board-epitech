"""Lookups and database errors mapped to HTTP errors."""

from fastapi import HTTPException, status
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

# MySQL error codes
_DUPLICATE_ENTRY = 1062
_FK_CHILD_FAILS = 1452  # inserting / updating a reference to a missing row
_FK_PARENT_FAILS = 1451  # deleting a row that is still referenced


def get_or_404[M](db: Session, model: type[M], object_id: int) -> M:
    obj = db.get(model, object_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{model.__name__} not found")
    return obj


def commit(db: Session) -> None:
    """Commit, turning integrity errors into clean HTTP errors."""
    try:
        db.commit()
    except DataError as exc:
        # value too long / out of range for the column (schemas should catch it first)
        db.rollback()
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Value too long or out of range"
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        code = exc.orig.args[0] if exc.orig and exc.orig.args else None
        if code == _DUPLICATE_ENTRY:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "A record with the same unique value already exists"
            ) from exc
        if code == _FK_CHILD_FAILS:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT, "Referenced record does not exist"
            ) from exc
        if code == _FK_PARENT_FAILS:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Record is still referenced by other records"
            ) from exc
        raise HTTPException(status.HTTP_409_CONFLICT, "Integrity constraint violated") from exc
