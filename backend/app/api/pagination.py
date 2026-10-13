"""Pagination of list routes."""

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, Query
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


@dataclass
class PageParams:
    page: Annotated[int, Query(ge=1, le=100_000)] = 1
    limit: Annotated[int, Query(ge=1, le=100)] = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


PageQuery = Annotated[PageParams, Depends()]


def paginate(
    db: Session, stmt: Select[Any], params: PageParams, *options: Any
) -> dict[str, Any]:
    """Run `stmt` (already filtered and ordered) and return a `Page` payload."""
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    rows = db.scalars(
        stmt.options(*options).offset(params.offset).limit(params.limit)
    ).all()
    return {"items": rows, "total": total or 0, "page": params.page, "limit": params.limit}
