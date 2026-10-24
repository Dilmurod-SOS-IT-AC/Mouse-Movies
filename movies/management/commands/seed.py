import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from movies.models import Genre, Movie, Review, WatchlistItem

GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", "Fantasy",
    "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller",
]

# title, year, director, cast, runtime, genres, overview
MOVIES = [
    ("The Shawshank Redemption", 1994, "Frank Darabont", "Tim Robbins, Morgan Freeman, Bob Gunton", 142,
     ["Drama", "Crime"], "A banker convicted of murder forms a deep friendship with a fellow inmate and slowly plans his way to freedom."),
    ("The Godfather", 1972, "Francis Ford Coppola", "Marlon Brando, Al Pacino, James Caan", 175,
     ["Drama", "Crime"], "The aging patriarch of an organized crime dynasty hands control of his empire to his reluctant youngest son."),
    ("The Dark Knight", 2008, "Christopher Nolan", "Christian Bale, Heath Ledger, Aaron Eckhart", 152,
     ["Action", "Crime", "Thriller"], "Batman faces the Joker, an anarchic criminal mastermind who pushes Gotham to its breaking point."),
    ("Pulp Fiction", 1994, "Quentin Tarantino", "John Travolta, Uma Thurman, Samuel L. Jackson", 154,
     ["Crime", "Thriller"], "The lives of two hitmen, a boxer and a gangster's wife intertwine in four tales of violence and redemption."),
    ("Inception", 2010, "Christopher Nolan", "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page", 148,
     ["Action", "Sci-Fi", "Thriller"], "A thief who steals secrets through dream-sharing is offered a chance to plant an idea in a target's mind."),
    ("Fight Club", 1999, "David Fincher", "Brad Pitt, Edward Norton, Helena Bonham Carter", 139,
     ["Drama", "Thriller"], "An insomniac office worker and a soap salesman build an underground fight club that spirals out of control."),
    ("Forrest Gump", 1994, "Robert Zemeckis", "Tom Hanks, Robin Wright, Gary Sinise", 142,
     ["Drama", "Romance", "Comedy"], "A kind-hearted man with a low IQ witnesses and influences several decades of American history."),
    ("The Matrix", 1999, "Lana Wachowski, Lilly Wachowski", "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss", 136,
     ["Action", "Sci-Fi"], "A hacker discovers that reality is a simulation and joins a rebellion against its machine overlords."),
    ("Interstellar", 2014, "Christopher Nolan", "Matthew McConaughey, Anne Hathaway, Jessica Chastain", 169,
     ["Adventure", "Drama", "Sci-Fi"], "Explorers travel through a wormhole in space in an attempt to ensure humanity's survival."),
    ("Spirited Away", 2001, "Hayao Miyazaki", "Rumi Hiiragi, Miyu Irino, Mari Natsuki", 125,
     ["Animation", "Fantasy", "Adventure"], "A girl wanders into a world ruled by gods and witches where humans are changed into beasts."),
    ("Parasite", 2019, "Bong Joon-ho", "Song Kang-ho, Lee Sun-kyun, Cho Yeo-jeong", 132,
     ["Drama", "Thriller", "Comedy"], "A poor family schemes to become employed by a wealthy household, with unforeseen consequences."),
    ("Toy Story", 1995, "John Lasseter", "Tom Hanks, Tim Allen, Don Rickles", 81,
     ["Animation", "Comedy", "Adventure"], "A cowboy doll is threatened when a new spaceman action figure becomes the favourite toy in the room."),
    ("Gladiator", 2000, "Ridley Scott", "Russell Crowe, Joaquin Phoenix, Connie Nielsen", 155,
     ["Action", "Adventure", "Drama"], "A betrayed Roman general rises through the gladiator arena to take revenge on the emperor who murdered his family."),
    ("The Silence of the Lambs", 1991, "Jonathan Demme", "Jodie Foster, Anthony Hopkins, Scott Glenn", 118,
     ["Crime", "Horror", "Thriller"], "A young FBI cadet seeks the help of an imprisoned cannibal killer to catch another serial murderer."),
    ("Back to the Future", 1985, "Robert Zemeckis", "Michael J. Fox, Christopher Lloyd, Lea Thompson", 116,
     ["Adventure", "Comedy", "Sci-Fi"], "A teenager is accidentally sent thirty years into the past in a time-travelling DeLorean."),
    ("Alien", 1979, "Ridley Scott", "Sigourney Weaver, Tom Skerritt, John Hurt", 117,
     ["Horror", "Sci-Fi"], "The crew of a commercial spaceship encounters a deadly lifeform after investigating a distress signal."),
    ("Se7en", 1995, "David Fincher", "Brad Pitt, Morgan Freeman, Gwyneth Paltrow", 127,
     ["Crime", "Mystery", "Thriller"], "Two detectives hunt a serial killer who uses the seven deadly sins as his motives."),
    ("Amelie", 2001, "Jean-Pierre Jeunet", "Audrey Tautou, Mathieu Kassovitz, Rufus", 122,
     ["Comedy", "Romance"], "A shy waitress in Montmartre decides to secretly improve the lives of those around her."),
    ("Mad Max: Fury Road", 2015, "George Miller", "Tom Hardy, Charlize Theron, Nicholas Hoult", 120,
     ["Action", "Adventure", "Sci-Fi"], "In a desert wasteland, a drifter and a rebel warrior flee a tyrant across the sands in a high-speed chase."),
    ("The Lord of the Rings: The Fellowship of the Ring", 2001, "Peter Jackson", "Elijah Wood, Ian McKellen, Viggo Mortensen", 178,
     ["Adventure", "Fantasy", "Action"], "A meek hobbit and eight companions set out to destroy a powerful ring and save Middle-earth."),
    ("Get Out", 2017, "Jordan Peele", "Daniel Kaluuya, Allison Williams, Catherine Keener", 104,
     ["Horror", "Mystery", "Thriller"], "A young Black man visits his white girlfriend's family estate and uncovers a disturbing secret."),
    ("La La Land", 2016, "Damien Chazelle", "Ryan Gosling, Emma Stone, John Legend", 128,
     ["Comedy", "Drama", "Romance"], "A jazz pianist and an aspiring actress fall in love while pursuing their dreams in Los Angeles."),
    ("Coco", 2017, "Lee Unkrich", "Anthony Gonzalez, Gael Garcia Bernal, Benjamin Bratt", 105,
     ["Animation", "Fantasy", "Adventure"], "An aspiring musician enters the Land of the Dead to find his great-great-grandfather, a legendary singer."),
    ("Blade Runner 2049", 2017, "Denis Villeneuve", "Ryan Gosling, Harrison Ford, Ana de Armas", 164,
     ["Drama", "Mystery", "Sci-Fi"], "A young blade runner's discovery of a long-buried secret leads him to track down a former blade runner."),
]

REVIEW_TEXTS = [
    "Absolutely loved it. Would happily watch again.",
    "Great pacing and a fantastic cast.",
    "A bit overrated, but still worth a watch.",
    "Masterpiece. The ending stayed with me for days.",
    "Beautiful cinematography, story could be tighter.",
    "Rewatched this with friends and it holds up perfectly.",
    "",
]

DEMO_USERS = ["alice", "bob", "carol", "dave"]


class Command(BaseCommand):
    help = "Populate the database with demo genres, movies, users, reviews and watchlists."

    def add_arguments(self, parser):
        parser.add_argument("--password", default="demo12345", help="Password for the demo users (default: demo12345).")
        parser.add_argument("--with-admin", action="store_true", help="Also create an 'admin' superuser with the same password.")
        parser.add_argument("--flush", action="store_true", help="Delete existing movies, genres, reviews and watchlist items first.")

    @transaction.atomic
    def handle(self, *args, **opts):
        User = get_user_model()
        rng = random.Random(42)

        if opts["flush"]:
            WatchlistItem.objects.all().delete()
            Review.objects.all().delete()
            Movie.objects.all().delete()
            Genre.objects.all().delete()
            self.stdout.write("Flushed existing catalogue data.")

        genres = {}
        for name in GENRES:
            genres[name], _ = Genre.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
        self.stdout.write(f"Genres: {len(genres)}")

        movies = []
        created = 0
        for title, year, director, cast, runtime, genre_names, overview in MOVIES:
            movie = Movie.objects.filter(title=title, release_year=year).first()
            if movie is None:
                movie = Movie(title=title, release_year=year, director=director, cast=cast,
                              runtime=runtime, overview=overview)
                movie.save()
                created += 1
            movie.genres.set([genres[g] for g in genre_names])
            movies.append(movie)
        self.stdout.write(f"Movies: {len(movies)} ({created} new)")

        users = []
        for username in DEMO_USERS:
            user, is_new = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
            if is_new:
                user.set_password(opts["password"])
                user.save()
            users.append(user)

        if opts["with_admin"]:
            admin, is_new = User.objects.get_or_create(
                username="admin", defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True})
            if is_new:
                admin.set_password(opts["password"])
                admin.save()
                self.stdout.write("Superuser 'admin' created.")

        reviews = watch = 0
        for user in users:
            for movie in rng.sample(movies, k=8):
                _, is_new = Review.objects.get_or_create(
                    movie=movie, user=user,
                    defaults={"rating": rng.randint(5, 10), "text": rng.choice(REVIEW_TEXTS)})
                reviews += is_new
            for movie in rng.sample(movies, k=5):
                _, is_new = WatchlistItem.objects.get_or_create(user=user, movie=movie)
                watch += is_new
        self.stdout.write(f"Users: {len(users)} | new reviews: {reviews} | new watchlist items: {watch}")
        self.stdout.write(self.style.SUCCESS("Seed complete."))
