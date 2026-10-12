from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.person import PersonCreate, PersonRead, PersonUpdate


class Register(PersonCreate):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(min_length=10, max_length=128)


class Login(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AccountUpdate(PersonUpdate):
    model_config = ConfigDict(extra="forbid")


class LoginRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: PersonRead


class Apply(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    firstname: str | None = Field(default=None, min_length=1, max_length=50)
    lastname: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    message: str = Field(min_length=1, max_length=10000)
