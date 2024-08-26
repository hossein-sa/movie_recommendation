from ninja import Schema
from datetime import date
from typing import Optional


class GenreSchema(Schema):
    id: int
    name: str


class GenreCreateSchema(Schema):
    name: str


class MovieSchema(Schema):
    id: int
    title: str
    description: str
    genre: GenreSchema  # Nested schema to include genre details
    release_date: date
    rating: float
    created_at: date


class MovieCreateSchema(Schema):
    title: str
    description: str
    genre_id: int  # Reference to the genre
    release_date: date
    rating: float


class MovieUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    genre_id: Optional[int] = None
    release_date: Optional[date] = None
    rating: Optional[float] = None


class UserSchema(Schema):
    username: str
    password: str
    email: Optional[str] = None


class LoginSchema(Schema):
    username: str
    password: str


class WatchlistSchema(Schema):
    id: int
    movie: MovieSchema
