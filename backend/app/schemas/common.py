"""Building blocks shared by all schemas."""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _max_72_bytes(password: str) -> str:
    # bcrypt rejects passwords longer than 72 bytes
    if len(password.encode()) > 72:
        raise ValueError("Password must be at most 72 bytes long")
    return password


Password = Annotated[
    str, Field(min_length=8, max_length=72), AfterValidator(_max_72_bytes)
]
Phone = Annotated[str, Field(min_length=3, max_length=20)]
# no "@": login accepts a user name or an email, the two must never collide
UserName = Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[^@]+$")]
# MySQL TEXT holds 65 535 bytes (up to 4 bytes per character): stay well below
LongText = Annotated[str, Field(max_length=10_000)]
# primary / foreign keys are INT in MySQL
Id = Annotated[int, Field(ge=1, le=2_147_483_647)]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    limit: int
