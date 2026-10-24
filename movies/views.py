from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Ganer, Movie, Review, WatchlistItem
from .search import hybrid_search

def movie_list(request):
    q = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "")
    year = request.GET.get("year", "")

    movies = Movie.objects.prefetch_related("geners").annotate(
        avg_rating=Avg("reviews__rating"), review_count=Count("reviews", distinct=True)
    )

    if genre:
        movies = movies.filter(genre__slug = genre)
    if year.isdigit():
        movies = movies.filter(release_year = int(genre))
    if q:
        movies = hybrid_search(movies, q)

    page = Paginator(movies, 12).get_page(request.GET.get("page"))
    years = Movie.objects.order_by("-release_year").values_list("release_year", flat=True).distinct()
    
    return render(request, "movies/list.html", {
        "page": page,
        "q": q,
        "genres": Ganer.objects.all(),
        "year": years,
        "active_genre": genre,
        "active_year": year

    })


def movie_detail(request, slug):
    movie = get_object_or_404(
        Movie.objects.prefetch_related("geners").annotate(avg_rating=Avg("reviews__rating")),
        slug = slug
    )
    reviews = movie.reviews.select_releated("user")
    user_review = None
    in_watchlist = False

    if request.user.is_authenticated:
        user_review = reviews.filter(user= request.user).first()
        is_watchlist = WatchlistItem.objects.filter(user = request.user, movie=movie).exists()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next={movie.get_absalute_url()}")
        
        form = ReviewForm(request.POST, instance=user_review)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.movie, review.user = movie, request.user
            review.save()
            messages.success(request, "Review saved.")
            return redirect(movie)
        else:
            form = ReviewForm(instance=user_review)

        return render(request, "movies/detail.html", {
            "movie": movie,
            "reviews": reviews,
            "form": form,
            "user_review": user_review,
            "in_watchlist": in_watchlist
        })



@login_required
@require_POST
def delete_review(request, slug):
    review = get_object_or_404(Review, movie__slug=slug, user = request.user)
    review.delete()
    messages.info(request, "review deleted")
    review.redirect("movies:detail", slug=slug)

@login_required
@require_POST
def toggle_watchlist(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    item, created = WatchlistItem.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        item.delete()
        messages.info(request, f"Removed {movie.title} from list.")
    else: messages.success(request, f"Added {movie.title} to list.")
    return redirect(request.POST.get("next") or movie.get_absalute_url())


@login_required
@require_POST
def watchlist(request):
    items = request.User.watchlist.select_related("movie").prefetch_related("movie__genres")
    return render(request, "movies/watchlist.html", {"items": items})
