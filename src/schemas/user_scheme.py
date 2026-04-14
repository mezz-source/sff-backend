from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)

class ModifyUser(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=32)
    password: str | None = Field(default=None, min_length=8, max_length=128)

class LoginUser(BaseModel):
    username: str
    password: str