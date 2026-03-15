import math
import pytest
from solution import RatingRegistry, MovieRecommender, Movie, User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_registry():
    """Create a registry with some default movies and users."""
    reg = RatingRegistry()
    reg.add_movie(1, "The Matrix")
    reg.add_movie(2, "Inception")
    reg.add_movie(3, "Interstellar")
    reg.add_movie(4, "The Godfather")
    reg.add_movie(5, "Pulp Fiction")
    reg.add_user(1, "Alice")
    reg.add_user(2, "Bob")
    reg.add_user(3, "Charlie")
    return reg


def make_neetcode_registry():
    """The exact NeetCode example setup."""
    reg = RatingRegistry()
    reg.add_movie(1, "Movie1")
    reg.add_movie(2, "Movie2")
    reg.add_movie(3, "Movie3")
    reg.add_user(1, "User1")
    reg.add_user(2, "User2")
    reg.add_user(3, "User3")
    reg.rate_movie(1, 1, 5)  # user1 rates movie1=5
    reg.rate_movie(1, 2, 2)  # user1 rates movie2=2
    reg.rate_movie(2, 2, 2)  # user2 rates movie2=2
    reg.rate_movie(2, 3, 4)  # user2 rates movie3=4
    return reg


# ===========================================================================
# LEVEL 1 — Core Data Model
# ===========================================================================

class TestLevel1:
    def test_movie_creation(self):
        m = Movie(1, "The Matrix")
        assert m.movie_id == 1
        assert m.title == "The Matrix"

    def test_user_creation(self):
        u = User(1, "Alice")
        assert u.user_id == 1
        assert u.name == "Alice"

    def test_add_movie(self):
        reg = RatingRegistry()
        reg.add_movie(1, "The Matrix")
        assert 1 in reg.movies

    def test_add_user(self):
        reg = RatingRegistry()
        reg.add_user(1, "Alice")
        assert 1 in reg.users

    def test_rate_movie(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        assert reg.get_user_ratings(1) == {1: 5}

    def test_rate_movie_invalid_rating(self):
        reg = make_registry()
        with pytest.raises(ValueError):
            reg.rate_movie(1, 1, 0)
        with pytest.raises(ValueError):
            reg.rate_movie(1, 1, 6)

    def test_average_rating_single(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 4)
        assert reg.get_average_rating(1) == 4.0

    def test_average_rating_multiple(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 4)
        reg.rate_movie(2, 1, 2)
        assert reg.get_average_rating(1) == 3.0

    def test_average_rating_no_ratings(self):
        reg = make_registry()
        assert reg.get_average_rating(1) == 0.0

    def test_get_user_ratings_multiple_movies(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(1, 2, 3)
        reg.rate_movie(1, 3, 4)
        result = reg.get_user_ratings(1)
        assert result == {1: 5, 2: 3, 3: 4}

    def test_get_user_ratings_empty(self):
        reg = make_registry()
        assert reg.get_user_ratings(1) == {}

    def test_rate_movie_updates_existing(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 3)
        reg.rate_movie(1, 1, 5)
        assert reg.get_user_ratings(1) == {1: 5}
        assert reg.get_average_rating(1) == 5.0


# ===========================================================================
# LEVEL 2 — Queries and Ranking
# ===========================================================================

class TestLevel2:
    def test_get_top_rated_basic(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(1, 2, 3)
        reg.rate_movie(1, 3, 4)
        result = reg.get_top_rated(2)
        assert result == [1, 3]

    def test_get_top_rated_all(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(1, 2, 3)
        reg.rate_movie(1, 3, 4)
        result = reg.get_top_rated(5)
        assert result == [1, 3, 2]

    def test_get_top_rated_tie_broken_by_movie_id(self):
        reg = make_registry()
        reg.rate_movie(1, 3, 4)
        reg.rate_movie(1, 1, 4)
        reg.rate_movie(1, 2, 4)
        result = reg.get_top_rated(3)
        assert result == [1, 2, 3]

    def test_get_top_rated_n_greater_than_available(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        result = reg.get_top_rated(10)
        assert result == [1]

    def test_get_top_rated_empty(self):
        reg = RatingRegistry()
        assert reg.get_top_rated(5) == []

    def test_get_movie_ratings_basic(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(2, 1, 3)
        result = reg.get_movie_ratings(1)
        assert result == {1: 5, 2: 3}

    def test_get_movie_ratings_empty(self):
        reg = make_registry()
        assert reg.get_movie_ratings(1) == {}

    def test_get_movie_ratings_single(self):
        reg = make_registry()
        reg.rate_movie(1, 2, 4)
        assert reg.get_movie_ratings(2) == {1: 4}

    def test_top_rated_with_multiple_raters(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(2, 1, 3)  # avg 4.0
        reg.rate_movie(1, 2, 4)
        reg.rate_movie(2, 2, 4)  # avg 4.0
        reg.rate_movie(1, 3, 2)  # avg 2.0
        # Tie between movie 1 and 2 at 4.0 — movie 1 first by id
        result = reg.get_top_rated(3)
        assert result == [1, 2, 3]

    def test_get_top_rated_excludes_unrated(self):
        reg = make_registry()
        reg.rate_movie(1, 2, 5)
        reg.rate_movie(1, 4, 3)
        result = reg.get_top_rated(5)
        assert 1 not in result
        assert 3 not in result
        assert 5 not in result


# ===========================================================================
# LEVEL 3 — Recommendation Engine
# ===========================================================================

class TestLevel3:
    def test_neetcode_recommend_user1(self):
        """NeetCode example: recommend(user1) -> movie3."""
        reg = make_neetcode_registry()
        rec = MovieRecommender(reg)
        assert rec.recommend(1) == 3

    def test_neetcode_recommend_user2(self):
        """NeetCode example: recommend(user2) -> movie1."""
        reg = make_neetcode_registry()
        rec = MovieRecommender(reg)
        assert rec.recommend(2) == 1

    def test_neetcode_recommend_new_user(self):
        """NeetCode example: recommend(user3 with no ratings) -> movie1 (highest avg 5.0)."""
        reg = make_neetcode_registry()
        rec = MovieRecommender(reg)
        assert rec.recommend(3) == 1

    def test_similarity_identical_ratings(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(1, 2, 3)
        reg.rate_movie(2, 1, 5)
        reg.rate_movie(2, 2, 3)
        rec = MovieRecommender(reg)
        assert rec._compute_similarity(1, 2) == 0

    def test_similarity_different_ratings(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(1, 2, 1)
        reg.rate_movie(2, 1, 1)
        reg.rate_movie(2, 2, 5)
        rec = MovieRecommender(reg)
        assert rec._compute_similarity(1, 2) == 8  # |5-1| + |1-5| = 8

    def test_similarity_no_corated(self):
        reg = make_registry()
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(2, 2, 3)
        rec = MovieRecommender(reg)
        assert rec._compute_similarity(1, 2) == math.inf

    def test_recommend_picks_highest_rated_unwatched(self):
        reg = RatingRegistry()
        reg.add_movie(1, "A")
        reg.add_movie(2, "B")
        reg.add_movie(3, "C")
        reg.add_movie(4, "D")
        reg.add_user(1, "Alice")
        reg.add_user(2, "Bob")
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(2, 1, 5)  # co-rated, identical -> similarity 0
        reg.rate_movie(2, 2, 3)
        reg.rate_movie(2, 3, 5)
        reg.rate_movie(2, 4, 1)
        rec = MovieRecommender(reg)
        # Bob's unwatched by Alice: movie2=3, movie3=5, movie4=1 -> recommend movie3
        assert rec.recommend(1) == 3

    def test_recommend_no_similar_user(self):
        reg = RatingRegistry()
        reg.add_movie(1, "A")
        reg.add_movie(2, "B")
        reg.add_user(1, "Alice")
        reg.rate_movie(1, 1, 5)
        rec = MovieRecommender(reg)
        # Only one user, no similar user
        assert rec.recommend(1) is None

    def test_recommend_multiple_similar_users(self):
        """When two users have same similarity, pick the one with lower user_id."""
        reg = RatingRegistry()
        reg.add_movie(1, "A")
        reg.add_movie(2, "B")
        reg.add_movie(3, "C")
        reg.add_user(1, "Alice")
        reg.add_user(2, "Bob")
        reg.add_user(3, "Charlie")
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(2, 1, 5)  # sim(1,2) = 0
        reg.rate_movie(3, 1, 5)  # sim(1,3) = 0
        reg.rate_movie(2, 2, 4)
        reg.rate_movie(3, 3, 3)
        rec = MovieRecommender(reg)
        # Tie in similarity -> user2 picked (lower id), recommend movie2
        assert rec.recommend(1) == 2

    def test_new_user_highest_avg(self):
        reg = RatingRegistry()
        reg.add_movie(1, "A")
        reg.add_movie(2, "B")
        reg.add_user(1, "Alice")
        reg.add_user(2, "Bob")
        reg.rate_movie(1, 1, 3)
        reg.rate_movie(1, 2, 5)
        rec = MovieRecommender(reg)
        assert rec.recommend(2) == 2


# ===========================================================================
# LEVEL 4 — Extended Features
# ===========================================================================

class TestLevel4:
    def test_recommend_n_basic(self):
        reg = make_neetcode_registry()
        rec = MovieRecommender(reg)
        result = rec.recommend_n(1, 2)
        assert result[0] == 3  # from most similar user2

    def test_recommend_n_new_user(self):
        reg = make_neetcode_registry()
        rec = MovieRecommender(reg)
        result = rec.recommend_n(3, 3)
        # Sorted by avg rating desc: movie1=5.0, movie3=4.0, movie2=2.0
        assert result == [1, 3, 2]

    def test_recommend_n_limited(self):
        reg = make_neetcode_registry()
        rec = MovieRecommender(reg)
        result = rec.recommend_n(3, 1)
        assert result == [1]

    def test_get_similar_users_basic(self):
        reg = make_neetcode_registry()
        rec = MovieRecommender(reg)
        result = rec.get_similar_users(1, 2)
        assert len(result) == 2
        # user2 has sim = |2-2| = 0, user3 has sim = inf
        assert result[0] == (2, 0)
        assert result[1][0] == 3
        assert result[1][1] == math.inf

    def test_get_similar_users_limited(self):
        reg = make_neetcode_registry()
        rec = MovieRecommender(reg)
        result = rec.get_similar_users(1, 1)
        assert len(result) == 1
        assert result[0] == (2, 0)

    def test_genre_support_in_movie(self):
        reg = RatingRegistry()
        reg.add_movie(1, "The Matrix", genre="Sci-Fi")
        assert reg.movies[1].genre == "Sci-Fi"

    def test_genre_default_none(self):
        reg = RatingRegistry()
        reg.add_movie(1, "The Matrix")
        assert reg.movies[1].genre is None

    def test_recommend_by_genre_basic(self):
        reg = RatingRegistry()
        reg.add_movie(1, "The Matrix", genre="Sci-Fi")
        reg.add_movie(2, "Inception", genre="Sci-Fi")
        reg.add_movie(3, "The Godfather", genre="Crime")
        reg.add_user(1, "Alice")
        reg.add_user(2, "Bob")
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(2, 1, 5)  # co-rated, sim = 0
        reg.rate_movie(2, 2, 4)
        reg.rate_movie(2, 3, 5)
        rec = MovieRecommender(reg)
        # Bob's unwatched Sci-Fi for Alice: movie2 (rated 4)
        assert rec.recommend_by_genre(1, "Sci-Fi") == 2

    def test_recommend_by_genre_excludes_other_genres(self):
        reg = RatingRegistry()
        reg.add_movie(1, "The Matrix", genre="Sci-Fi")
        reg.add_movie(2, "The Godfather", genre="Crime")
        reg.add_movie(3, "Interstellar", genre="Sci-Fi")
        reg.add_user(1, "Alice")
        reg.add_user(2, "Bob")
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(2, 1, 5)
        reg.rate_movie(2, 2, 5)  # Crime — excluded
        reg.rate_movie(2, 3, 3)  # Sci-Fi — included
        rec = MovieRecommender(reg)
        assert rec.recommend_by_genre(1, "Sci-Fi") == 3

    def test_recommend_by_genre_new_user(self):
        reg = RatingRegistry()
        reg.add_movie(1, "The Matrix", genre="Sci-Fi")
        reg.add_movie(2, "The Godfather", genre="Crime")
        reg.add_movie(3, "Interstellar", genre="Sci-Fi")
        reg.add_user(1, "Alice")
        reg.add_user(2, "Bob")
        reg.rate_movie(1, 1, 3)  # Sci-Fi avg 3.0
        reg.rate_movie(1, 2, 5)  # Crime avg 5.0
        reg.rate_movie(1, 3, 4)  # Sci-Fi avg 4.0
        rec = MovieRecommender(reg)
        # New user, Sci-Fi only: movie3 avg 4.0 > movie1 avg 3.0
        assert rec.recommend_by_genre(2, "Sci-Fi") == 3

    def test_recommend_n_from_multiple_similar_users(self):
        reg = RatingRegistry()
        reg.add_movie(1, "A")
        reg.add_movie(2, "B")
        reg.add_movie(3, "C")
        reg.add_movie(4, "D")
        reg.add_movie(5, "E")
        reg.add_user(1, "Alice")
        reg.add_user(2, "Bob")
        reg.add_user(3, "Charlie")
        # Alice rates movie1
        reg.rate_movie(1, 1, 5)
        # Bob co-rates movie1 identically, also has movie2 and movie3
        reg.rate_movie(2, 1, 5)
        reg.rate_movie(2, 2, 4)
        reg.rate_movie(2, 3, 3)
        # Charlie co-rates movie1 with diff of 1, also has movie4 and movie5
        reg.rate_movie(3, 1, 4)
        reg.rate_movie(3, 4, 5)
        reg.rate_movie(3, 5, 2)
        rec = MovieRecommender(reg)
        result = rec.recommend_n(1, 4)
        # Bob (sim=0) first: movie2=4, movie3=3
        # Charlie (sim=1) next: movie4=5, movie5=2
        assert result == [2, 3, 4, 5]

    def test_get_similar_users_sorted(self):
        reg = RatingRegistry()
        reg.add_movie(1, "A")
        reg.add_user(1, "Alice")
        reg.add_user(2, "Bob")
        reg.add_user(3, "Charlie")
        reg.add_user(4, "Dave")
        reg.rate_movie(1, 1, 5)
        reg.rate_movie(2, 1, 3)  # sim = 2
        reg.rate_movie(3, 1, 5)  # sim = 0
        reg.rate_movie(4, 1, 4)  # sim = 1
        rec = MovieRecommender(reg)
        result = rec.get_similar_users(1, 3)
        assert result == [(3, 0), (4, 1), (2, 2)]
