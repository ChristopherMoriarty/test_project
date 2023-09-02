from sqlalchemy import Column, Integer, MetaData, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship

Base: DeclarativeMeta = declarative_base()
metadata: MetaData = Base.metadata


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    books = relationship("Book", back_populates="author", lazy="joined")

    __table_args__ = (
        UniqueConstraint(
            "name", name="uq_author_name"
        ),
    )


class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    author_id = Column(Integer, ForeignKey("author.id"))

    author = relationship("Author", back_populates="books", lazy="joined")

    __table_args__ = (
        UniqueConstraint(
            "name", "author_id", name="uq_book_name_author_id"
        ),
    )
