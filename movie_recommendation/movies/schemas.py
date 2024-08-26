from ninja import Schema
from datetime import date
from typing import Optional


class GenreSchema(Schema):
    id: int
    name: str


class MovieSchema(Schema):
    id: int
    title: str
    description: str
    genre: GenreSchema  # Nested schema to include genre details
    release_date: date
    rating: float
    created_at: date
