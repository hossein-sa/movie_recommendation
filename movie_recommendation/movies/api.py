from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from ninja import NinjaAPI
from .models import Genre, Movie, Watchlist
from .schemas import GenreSchema, GenreCreateSchema, MovieSchema, MovieCreateSchema, MovieUpdateSchema, UserSchema, \
    LoginSchema, WatchlistSchema
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.authentication import JWTAuth

api = NinjaAPI()


# User Registration (No authentication required)
@api.post("/register/", response=UserSchema)
def register(request, payload: UserSchema):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already exists")
    user = User.objects.create(
        username=payload.username,
        password=make_password(payload.password),  # Hash the password
        email=payload.email
    )
    return user


# User Login (No authentication required)
@api.post("/login/")
def login(request, payload: LoginSchema):
    user = get_object_or_404(User, username=payload.username)
    if not user.check_password(payload.password):
        raise HttpError(400, "Invalid username or password")

    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Genre CRUD operations (Authentication required)
@api.get("/genres/", response=list[GenreSchema], auth=JWTAuth())
def list_genres(request):
    return Genre.objects.all()


@api.post("/genres/", response=GenreSchema, auth=JWTAuth())
def create_genre(request, payload: GenreCreateSchema):
    genre = Genre.objects.create(**payload.dict())
    return genre


@api.put("/genres/{genre_id}/", response=GenreSchema, auth=JWTAuth())
def update_genre(request, genre_id: int, payload: GenreCreateSchema):
    genre = get_object_or_404(Genre, id=genre_id)
    if not genre:
        raise HttpError(404, "Genre not found")

    genre.name = payload.name
    genre.save()
    return genre


@api.delete("/genres/{genre_id}/", auth=JWTAuth())
def delete_genre(request, genre_id: int):
    genre = get_object_or_404(Genre, id=genre_id)
    if not genre:
        raise HttpError(404, "Genre not found")

    genre.delete()
    return {"success": True}


# Movie CRUD operations (Authentication required)
@api.get("/movies/", response=list[MovieSchema], auth=JWTAuth())
def list_movies(request, title: str = None, genre_id: int = None, min_rating: float = None, max_rating: float = None,
                start_date: str = None, end_date: str = None, limit: int = 10, offset: int = 0):
    movies = Movie.objects.all()

    # Search by title
    if title:
        movies = movies.filter(title__icontains=title)

    # Filter by genre
    if genre_id:
        movies = movies.filter(genre_id=genre_id)

    # Filter by rating range
    if min_rating is not None:
        movies = movies.filter(rating__gte=min_rating)
    if max_rating is not None:
        movies = movies.filter(rating__lte=max_rating)

    # Filter by release date range
    if start_date:
        movies = movies.filter(release_date__gte=start_date)
    if end_date:
        movies = movies.filter(release_date__lte=end_date)

    # Apply pagination
    movies = movies[offset:offset + limit]

    return movies


@api.get("/movies/{movie_id}/", response=MovieSchema, auth=JWTAuth())
def get_movie(request, movie_id: int):
    movie = get_object_or_404(Movie, id=movie_id)
    if not movie:
        raise HttpError(404, "Movie not found")

    return movie


@api.post("/movies/", response=MovieSchema, auth=JWTAuth())
def create_movie(request, payload: MovieCreateSchema):
    genre = get_object_or_404(Genre, id=payload.genre_id)
    if not genre:
        raise HttpError(404, "Genre not found")

    movie = Movie.objects.create(
        title=payload.title,
        description=payload.description,
        genre=genre,
        release_date=payload.release_date,
        rating=payload.rating,
    )
    return movie


@api.put("/movies/{movie_id}/", response=MovieSchema, auth=JWTAuth())
def update_movie(request, movie_id: int, payload: MovieUpdateSchema):
    movie = get_object_or_404(Movie, id=movie_id)
    if not movie:
        raise HttpError(404, "Movie not found")

    if payload.title:
        movie.title = payload.title
    if payload.description:
        movie.description = payload.description
    if payload.genre_id:
        genre = get_object_or_404(Genre, id=payload.genre_id)
        if not genre:
            raise HttpError(404, "Genre not found")
        movie.genre = genre
    if payload.release_date:
        movie.release_date = payload.release_date
    if payload.rating:
        movie.rating = payload.rating

    movie.save()
    return movie


@api.delete("/movies/{movie_id}/", auth=JWTAuth())
def delete_movie(request, movie_id: int):
    movie = get_object_or_404(Movie, id=movie_id)
    if not movie:
        raise HttpError(404, "Movie not found")

    movie.delete()
    return {"success": True}


# Get the current user's watchlist
@api.get("/watchlist/", response=list[WatchlistSchema], auth=JWTAuth())
def get_watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)
    return watchlist


# Add a movie to the watchlist
@api.post("/watchlist/", response=WatchlistSchema, auth=JWTAuth())
def add_to_watchlist(request, movie_id: int):
    movie = get_object_or_404(Movie, id=movie_id)
    watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        raise HttpError(400, "Movie is already in the watchlist")

    return watchlist_item


# Remove a movie from the watchlist
@api.delete("/watchlist/{movie_id}/", auth=JWTAuth())
def remove_from_watchlist(request, movie_id: int):
    movie = get_object_or_404(Movie, id=movie_id)
    watchlist_item = get_object_or_404(Watchlist, user=request.user, movie=movie)
    watchlist_item.delete()
    return {"success": True}
