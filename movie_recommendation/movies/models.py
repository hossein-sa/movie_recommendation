from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    genre = models.ForeignKey(Genre, related_name='movies', on_delete=models.CASCADE)
    release_date = models.DateField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_genres = models.ManyToManyField(Genre, related_name='users')

    def __str__(self):
        return self.user.username


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Watchlist - {self.movie.title}"

    class Meta:
        unique_together = ("user", "movie")  # Prevents duplicate entries for the same movie in a user's watchlist


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")  # Add related_name="reviews"
    rating = models.DecimalField(max_digits=2, decimal_places=1)  # Rating out of 10, e.g., 8.5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")  # Ensures one review per user per movie

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating})"


