from django.db import models
from django.db.models import Avg
from ninja import Schema
from datetime import date, datetime
from typing import Optional
from .models import Movie  # Import the Movie model


class GenreSchema(Schema):
    id: int
    name: str


class GenreCreateSchema(Schema):
    name: str


class MovieSchema(Schema):
    id: int
    title: str
    description: str
    genre: GenreSchema
    release_date: date
    rating: float
    average_rating: Optional[float] = None  # Add this line
    created_at: date

    @staticmethod
    def resolve_average_rating(movie: Movie):
        return movie.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']


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


class ReviewSchema(Schema):
    id: int
    user: UserSchema
    movie: MovieSchema
    rating: float
    comment: Optional[str] = None
    created_at: datetime


class ReviewCreateSchema(Schema):
    rating: float
    comment: Optional[str] = None
    movie_id: int
