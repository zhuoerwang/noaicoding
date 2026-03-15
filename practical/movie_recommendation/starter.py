class Movie:
    def __init__(self, movie_id: int, title: str, genre: str = None):
        pass


class User:
    def __init__(self, user_id: int, name: str):
        pass


class RatingRegistry:
    def __init__(self):
        pass

    def add_movie(self, movie_id: int, title: str, genre: str = None) -> None:
        pass

    def add_user(self, user_id: int, name: str) -> None:
        pass

    def rate_movie(self, user_id: int, movie_id: int, rating: int) -> None:
        pass

    def get_average_rating(self, movie_id: int) -> float:
        pass

    def get_user_ratings(self, user_id: int) -> dict[int, int]:
        pass

    # Level 2

    def get_top_rated(self, n: int) -> list[int]:
        pass

    def get_movie_ratings(self, movie_id: int) -> dict[int, int]:
        pass


class MovieRecommender:
    def __init__(self, registry: RatingRegistry):
        pass

    # Level 3

    def recommend(self, user_id: int) -> int:
        pass

    # Level 4

    def recommend_n(self, user_id: int, n: int) -> list[int]:
        pass

    def get_similar_users(self, user_id: int, n: int) -> list[tuple[int, float]]:
        pass

    def recommend_by_genre(self, user_id: int, genre: str) -> int:
        pass
