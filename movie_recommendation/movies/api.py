from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from ninja import NinjaAPI
from .models import Genre, Movie, Watchlist, Review
from .schemas import GenreSchema, GenreCreateSchema, MovieSchema, MovieCreateSchema, MovieUpdateSchema, UserSchema, \
    LoginSchema, WatchlistSchema, ReviewSchema, ReviewCreateSchema
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.authentication import JWTAuth
from django.db.models import Q

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
                start_date: str = None, end_date: str = None, sort_by: str = "title", order: str = "asc",
                limit: int = 10, offset: int = 0):
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

    # Sorting
    sorting_options = {
        "title": "title",
        "release_date": "release_date",
        "rating": "rating"
    }

    # Determine sort order
    if sort_by in sorting_options:
        sort_field = sorting_options[sort_by]
        if order == "desc":
            sort_field = f"-{sort_field}"  # Prefix with "-" for descending order
        movies = movies.order_by(sort_field)

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


@api.get("/recommendations/", response=list[MovieSchema], auth=JWTAuth())
def get_recommendations(request):
    user = request.user

    # Get the user's favorite genres
    favorite_genres = user.userprofile.favorite_genres.all()

    # Get the movies in the user's watchlist
    watchlist_movies = Watchlist.objects.filter(user=user).values_list('movie_id', flat=True)

    # Recommend movies that are not in the user's watchlist but match the user's favorite genres
    recommended_movies = Movie.objects.filter(
        Q(genre__in=favorite_genres) & ~Q(id__in=watchlist_movies)
    ).distinct()[:10]  # Limit to 10 recommendations

    return recommended_movies


# Get all reviews for a specific movie
@api.get("/movies/{movie_id}/reviews/", response=list[ReviewSchema], auth=JWTAuth())
def get_movie_reviews(request, movie_id: int):
    reviews = Review.objects.filter(movie_id=movie_id)
    return reviews


# Add a review to a movie
@api.post("/movies/{movie_id}/reviews/", response=ReviewSchema, auth=JWTAuth())
def add_movie_review(request, movie_id: int, payload: ReviewCreateSchema):
    movie = get_object_or_404(Movie, id=movie_id)
    review, created = Review.objects.get_or_create(
        user=request.user,
        movie=movie,
        defaults={'rating': payload.rating, 'comment': payload.comment}
    )

    if not created:
        raise HttpError(400, "You have already reviewed this movie")

    return review


# Update an existing review
@api.put("/reviews/{review_id}/", response=ReviewSchema, auth=JWTAuth())
def update_movie_review(request, review_id: int, payload: ReviewCreateSchema):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.rating = payload.rating
    review.comment = payload.comment
    review.save()
    return review


# Delete a review
@api.delete("/reviews/{review_id}/", auth=JWTAuth())
def delete_movie_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return {"success": True}
