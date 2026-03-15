# Movie Recommendation System

Design a movie recommendation system that suggests movies to users based on collaborative filtering — finding similar users by comparing their ratings and recommending movies those similar users enjoyed.

## Similarity Metric

For two users, compute the sum of absolute differences `|rating1 - rating2|` for all co-rated movies (movies both users have rated). A lower score means higher similarity. If two users share no co-rated movies, their similarity is infinity.

## Recommendation Algorithm

- **Existing user (has ratings):** Find the most similar reviewer (lowest similarity score). From that reviewer's rated movies, recommend the highest-rated movie that the target user has not yet seen.
- **New user (no ratings):** Recommend the movie with the highest average rating across all users.

---

## Level 1 — Core Data Model

Implement the foundational classes for storing movies, users, and ratings.

### Classes

- `Movie(movie_id: int, title: str)` — represents a movie.
- `User(user_id: int, name: str)` — represents a user.
- `RatingRegistry()` — central registry for movies, users, and ratings.

### RatingRegistry Methods

- `add_movie(movie_id: int, title: str)` — register a new movie.
- `add_user(user_id: int, name: str)` — register a new user.
- `rate_movie(user_id: int, movie_id: int, rating: int)` — record a rating (1-5) from a user for a movie.
- `get_average_rating(movie_id: int) -> float` — return the average rating for a movie.
- `get_user_ratings(user_id: int) -> dict[int, int]` — return a dict mapping movie_id to rating for all movies rated by the user.

---

## Level 2 — Queries and Ranking

Add ranking and lookup capabilities to the registry.

### Additional RatingRegistry Methods

- `get_top_rated(n: int) -> list[int]` — return the top `n` movie IDs sorted by average rating descending. Break ties by movie_id ascending.
- `get_movie_ratings(movie_id: int) -> dict[int, int]` — return a dict mapping user_id to rating for all users who rated the movie.

---

## Level 3 — Recommendation Engine

Implement the core recommendation algorithm using collaborative filtering.

### Classes

- `MovieRecommender(registry: RatingRegistry)` — recommendation engine backed by a rating registry.

### MovieRecommender Methods

- `recommend(user_id: int) -> int` — recommend a single movie_id to the user.
  - For users with ratings: find the most similar user (lowest sum of absolute rating differences on co-rated movies). From that user's movies, return the highest-rated movie the target user hasn't seen.
  - For users with no ratings: return the movie with the highest average rating.

---

## Level 4 — Extended Features

Add batch recommendations, similar-user queries, and genre filtering.

### Changes

- `add_movie(movie_id: int, title: str, genre: str = None)` — now accepts an optional genre.

### Additional MovieRecommender Methods

- `recommend_n(user_id: int, n: int) -> list[int]` — return the top `n` recommended movie IDs for the user.
- `get_similar_users(user_id: int, n: int) -> list[tuple[int, float]]` — return the `n` most similar users as `(user_id, similarity_score)` pairs, sorted by similarity ascending.
- `recommend_by_genre(user_id: int, genre: str) -> int` — recommend a single movie_id restricted to movies of the given genre, using the same algorithm.
