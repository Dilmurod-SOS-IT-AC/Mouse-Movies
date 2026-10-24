from django.contrib import admin
from django.db.models import Avg, Count
from django.utils.html import format_html

from .models import Genre, Movie, Review, WatchlistItem


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "movie_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_movie_count=Count("movies"))

    @admin.display(description="Movies", ordering="_movie_count")
    def movie_count(self, obj):
        return obj._movie_count


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ("user", "rating", "text", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("poster_thumb", "title", "release_year", "director", "runtime", "avg_rating", "created_at")
    list_display_links = ("poster_thumb", "title")
    list_filter = ("release_year", "genres")
    search_fields = ("title", "director", "cast")
    filter_horizontal = ("genres",)
    readonly_fields = ("created_at", "poster_preview")
    date_hierarchy = "created_at"
    inlines = [ReviewInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "overview")}),
        ("Details", {"fields": ("director", "cast", "release_year", "runtime", "genres")}),
        ("Poster", {"fields": ("poster", "poster_preview")}),
        ("Meta", {"fields": ("created_at",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_avg_rating=Avg("reviews__rating"))

    @admin.display(description="Rating", ordering="_avg_rating")
    def avg_rating(self, obj):
        return f"{obj._avg_rating:.1f}" if obj._avg_rating else "—"

    @admin.display(description="Poster")
    def poster_thumb(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="height:48px;border-radius:4px;">', obj.poster.url)
        return "—"

    @admin.display(description="Preview")
    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="max-height:240px;border-radius:6px;">', obj.poster.url)
        return "No poster uploaded"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("movie__title", "user__username", "text")
    autocomplete_fields = ("movie", "user")
    readonly_fields = ("created_at",)


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "added_at")
    list_filter = ("added_at",)
    search_fields = ("movie__title", "user__username")
    autocomplete_fields = ("movie", "user")
    readonly_fields = ("added_at",)
