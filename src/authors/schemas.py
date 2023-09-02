from typing import Optional
from pydantic import BaseModel


class AuthorBase(BaseModel):
    name: str

class AuthorRead(AuthorBase):
    id: int

    class Config:
        orm_mode = True


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    name: Optional[str] = None