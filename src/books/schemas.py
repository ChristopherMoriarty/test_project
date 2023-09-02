from typing import Optional
from pydantic import BaseModel


class BookBase(BaseModel):
    name: str
    author_id: int


class BookRead(BookBase):
    id: int

    class Config:
        orm_mode = True
        

class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    name: Optional[str] = None
    author_id: Optional[int] = None




