from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import F, FloatField, Value, Q
from django.db.models.functions import Coalesce, Greatest

FTS_WEIGHT = 0.7
TRGM_WEIGHT = 0.3
TRGM_THERESHOLD = 0.15

def hybrid_search(queryset, q):
    query = SearchQuery(q, search_type="websearch", config="english")

    return(
        queryset.annotate(
            fts_rank=Coalesce(SearchRank(F("search_vector"), query), Value(0.0), output_field=FloatField()),
            trgm=Greatest(
                TrigramSimilarity("title", q),
                TrigramSimilarity("director", q),
                output_field=FloatField()
            ),
        )
        .annotate(score=F("fts_rank") * FTS_WEIGHT + F("trgm") * TRGM_WEIGHT)
        .filter(search_vector=query | Q(trgm__gt=TRGM_THERESHOLD))
        .order_by("-score", "-release_year")
    )

