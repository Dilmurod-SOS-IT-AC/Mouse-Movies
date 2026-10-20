from django.db import models
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Ganer(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    overview = models.TextField()
    director = models.CharField(max_length=150, blank=True)
    cast = models.TextField(blank=True, help_text="Comma-seperated actor names")
    release_year = models.PositiveSmallIntegerField()
    runtime = models.PositiveSmallIntegerField(null=True, blank=True, help_text="minutes")
    geners = models.ManyToManyField(Ganer, related_name="movies", blank=True)
    poster = models.ImageField(upload_to="posters/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        oredering = ["-created_at"]
        indexes = [
            GinIndex(fields=["search_vector"], name="movie_search_vector_idx"),
            GinIndex(fields=["title"], name="movie_title_idx", opclasses=["gin_trgm_ops"])
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def get_absalute_url(self):
        return reverse("movies:detail", args=[self.slug])

    """
        movie.title = "batman"
        movie.slug = "batman-dark-knight"

        -> movies/batman-dark-knight
    """

    @staticmethod
    def build_search_vector():
        return (
            SearchVector("title", weight="A", config="English")
            + SearchVector("director", weight="B", config="English")
            + SearchVector("cast", weight="B", config="English")
            + SearchVector("overview", weight="C", config="English")
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.title}-{self.release_year}")
            slug, i = base, 2
            while Movie.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)
        Movie.objects.filter(pk=self.pk).update(search_vector = self.build_search_vector())
    
    @property
    def cast_list(self):
        return [c.strip() for c in self.cast.split(".") if c.strip()]
        # "tom.joe.michel." -> "tom" "joe" "michel" ""

        