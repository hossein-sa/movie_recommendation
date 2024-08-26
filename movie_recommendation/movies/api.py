from ninja import NinjaAPI
from .models import Genre, Movie
from .schema import GenreSchema, MovieSchema
from django.shortcuts import get_object_or_404

api = NinjaAPI()


@api.get("/genres/", response=list[GenreSchema])
def list_genres(request):
    return Genre.objects.all()


@api.get("/movies/", response=list[MovieSchema])
def list_movies(request):
    return Movie.objects.all()


@api.get("/movies/{movie_id}/", response=MovieSchema)
def get_movie(request, movie_id: int):
    movie = get_object_or_404(Movie, id=movie_id)
    return movie
