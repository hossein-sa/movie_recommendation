from django.contrib import admin
from .models import Genre, Movie, UserProfile, Watchlist


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'genre', 'release_date', 'rating')
    search_fields = ('title', 'genre__name')
    list_filter = ('genre', 'release_date')
    ordering = ('-release_date',)  # Default order by release date (newest first)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('favorite_genres',)  # Makes it easier to manage many-to-many relationships


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie')
    search_fields = ('user__username', 'movie__title')
