import math


class Movie:
    def __init__(self, movie_id: int, title: str, genre: str = None):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre


class User:
    def __init__(self, user_id: int, name: str):
        self.user_id = user_id
        self.name = name


class RatingRegistry:
    def __init__(self):
        self.movies: dict[int, Movie] = {}
        self.users: dict[int, User] = {}
        # user_id -> {movie_id: rating}
        self.user_ratings: dict[int, dict[int, int]] = {}
        # movie_id -> {user_id: rating}
        self.movie_ratings: dict[int, dict[int, int]] = {}

    def add_movie(self, movie_id: int, title: str, genre: str = None) -> None:
        self.movies[movie_id] = Movie(movie_id, title, genre)
        if movie_id not in self.movie_ratings:
            self.movie_ratings[movie_id] = {}

    def add_user(self, user_id: int, name: str) -> None:
        self.users[user_id] = User(user_id, name)
        if user_id not in self.user_ratings:
            self.user_ratings[user_id] = {}

    def rate_movie(self, user_id: int, movie_id: int, rating: int) -> None:
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        self.user_ratings[user_id][movie_id] = rating
        self.movie_ratings[movie_id][user_id] = rating

    def get_average_rating(self, movie_id: int) -> float:
        ratings = self.movie_ratings.get(movie_id, {})
        if not ratings:
            return 0.0
        return sum(ratings.values()) / len(ratings)

    def get_user_ratings(self, user_id: int) -> dict[int, int]:
        return dict(self.user_ratings.get(user_id, {}))

    # Level 2

    def get_top_rated(self, n: int) -> list[int]:
        movie_ids = [mid for mid, ratings in self.movie_ratings.items() if ratings]
        movie_ids.sort(key=lambda mid: (-self.get_average_rating(mid), mid))
        return movie_ids[:n]

    def get_movie_ratings(self, movie_id: int) -> dict[int, int]:
        return dict(self.movie_ratings.get(movie_id, {}))


class MovieRecommender:
    def __init__(self, registry: RatingRegistry):
        self.registry = registry

    def _compute_similarity(self, user_id_a: int, user_id_b: int) -> float:
        """Sum of |r1 - r2| for co-rated movies. Infinity if no co-rated movies."""
        ratings_a = self.registry.user_ratings.get(user_id_a, {})
        ratings_b = self.registry.user_ratings.get(user_id_b, {})
        co_rated = set(ratings_a.keys()) & set(ratings_b.keys())
        if not co_rated:
            return math.inf
        return sum(abs(ratings_a[mid] - ratings_b[mid]) for mid in co_rated)

    def _find_most_similar_user(self, user_id: int) -> int | None:
        """Find the user with the lowest similarity score to the given user."""
        best_user = None
        best_score = math.inf
        for other_id in self.registry.users:
            if other_id == user_id:
                continue
            score = self._compute_similarity(user_id, other_id)
            if score < best_score or (score == best_score and (best_user is None or other_id < best_user)):
                best_score = score
                best_user = other_id
        if best_score == math.inf:
            return None
        return best_user

    def _highest_avg_movie(self, exclude: set[int] = None, genre: str = None) -> int | None:
        """Return movie_id with highest average rating, optionally filtering by genre and exclusions."""
        if exclude is None:
            exclude = set()
        candidates = []
        for mid in self.registry.movies:
            if mid in exclude:
                continue
            if genre is not None and self.registry.movies[mid].genre != genre:
                continue
            avg = self.registry.get_average_rating(mid)
            if avg > 0:
                candidates.append((mid, avg))
        if not candidates:
            return None
        candidates.sort(key=lambda x: (-x[1], x[0]))
        return candidates[0][0]

    # Level 3

    def recommend(self, user_id: int) -> int | None:
        user_ratings = self.registry.user_ratings.get(user_id, {})

        # New user fallback: highest average-rated movie
        if not user_ratings:
            return self._highest_avg_movie()

        # Find most similar user
        similar_user = self._find_most_similar_user(user_id)
        if similar_user is None:
            return None

        # From similar user's movies, recommend their highest-rated unwatched movie
        similar_ratings = self.registry.user_ratings.get(similar_user, {})
        candidates = [
            (mid, rating)
            for mid, rating in similar_ratings.items()
            if mid not in user_ratings
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda x: (-x[1], x[0]))
        return candidates[0][0]

    # Level 4

    def recommend_n(self, user_id: int, n: int) -> list[int]:
        user_ratings = self.registry.user_ratings.get(user_id, {})

        if not user_ratings:
            # New user: top n by average rating
            candidates = []
            for mid in self.registry.movies:
                avg = self.registry.get_average_rating(mid)
                if avg > 0:
                    candidates.append((mid, avg))
            candidates.sort(key=lambda x: (-x[1], x[0]))
            return [mid for mid, _ in candidates[:n]]

        # Collect recommendations from similar users in order of similarity
        similar_users = self.get_similar_users(user_id, len(self.registry.users) - 1)
        recommended = []
        seen = set(user_ratings.keys())

        for sim_user_id, score in similar_users:
            if score == math.inf:
                break
            sim_ratings = self.registry.user_ratings.get(sim_user_id, {})
            # Get unwatched movies from this similar user, sorted by their rating desc then movie_id asc
            unwatched = [
                (mid, rating)
                for mid, rating in sim_ratings.items()
                if mid not in seen
            ]
            unwatched.sort(key=lambda x: (-x[1], x[0]))
            for mid, _ in unwatched:
                if mid not in seen:
                    recommended.append(mid)
                    seen.add(mid)
                    if len(recommended) == n:
                        return recommended

        return recommended

    def get_similar_users(self, user_id: int, n: int) -> list[tuple[int, float]]:
        similarities = []
        for other_id in self.registry.users:
            if other_id == user_id:
                continue
            score = self._compute_similarity(user_id, other_id)
            similarities.append((other_id, score))
        # Sort by score ascending, then user_id ascending for ties
        similarities.sort(key=lambda x: (x[1], x[0]))
        return similarities[:n]

    def recommend_by_genre(self, user_id: int, genre: str) -> int | None:
        user_ratings = self.registry.user_ratings.get(user_id, {})

        # New user fallback: highest average-rated movie in genre
        if not user_ratings:
            return self._highest_avg_movie(genre=genre)

        # Find most similar user
        similar_user = self._find_most_similar_user(user_id)
        if similar_user is None:
            return self._highest_avg_movie(exclude=set(user_ratings.keys()), genre=genre)

        # From similar user's movies in the given genre, recommend their highest-rated unwatched
        similar_ratings = self.registry.user_ratings.get(similar_user, {})
        candidates = [
            (mid, rating)
            for mid, rating in similar_ratings.items()
            if mid not in user_ratings and self.registry.movies[mid].genre == genre
        ]
        if not candidates:
            return self._highest_avg_movie(exclude=set(user_ratings.keys()), genre=genre)
        candidates.sort(key=lambda x: (-x[1], x[0]))
        return candidates[0][0]
