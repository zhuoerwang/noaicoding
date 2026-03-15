# Blackjack

Design and implement a simplified Blackjack card game engine. The system should model cards, decks, hands, players, and game logic — all programmatically (no interactive input).

## Rules

- A standard deck has 52 cards: 4 suits x 13 values (2-10, J, Q, K, A).
- Card values: 2-10 are face value, J/Q/K = 10, A = 1 or 11.
- Ace counts as 11 unless it would cause the hand to bust (exceed 21), in which case it counts as 1. Multiple aces are handled independently.
- **Blackjack**: a score of 21 with exactly 2 cards (an Ace + a 10-value card). Pays 1.5x the bet.
- **Bust**: a score exceeding 21. The busted party loses immediately.
- **Dealer rule**: the dealer must hit (draw) while their score is below 17, and stand at 17 or above.

## Level 1 — Card, Deck, Hand

Implement the foundational data structures.

### Suit (Enum)
- Members: `CLUBS`, `DIAMONDS`, `HEARTS`, `SPADES`

### Card
- `Card(suit: Suit, value: int)` — value is 1-13 (1 = Ace, 11 = Jack, 12 = Queen, 13 = King).
- `get_value() -> int` — returns the blackjack point value: face value for 2-10, 10 for J/Q/K, 11 for Ace (the Hand is responsible for ace adjustment).
- `is_ace() -> bool` — returns True if this card is an Ace.
- `__str__()` — e.g. `"A of Spades"`, `"10 of Hearts"`, `"K of Clubs"`.

### Deck
- `Deck(seed=None)` — creates a full 52-card deck and shuffles it. If `seed` is provided, use it for reproducible shuffling.
- `draw() -> Card` — removes and returns the top card. Raises `ValueError` if deck is empty.
- `cards_remaining() -> int` — number of cards left.
- `reshuffle()` — resets to a full 52-card deck and shuffles again (using the original seed if one was provided).

### Hand
- `Hand()` — starts empty.
- `add_card(card: Card)` — adds a card to the hand.
- `get_score() -> int` — calculates the best score. Aces count as 11, but each ace is reduced to 1 (one at a time) if the total exceeds 21.
- `is_bust() -> bool` — True if score > 21.
- `is_blackjack() -> bool` — True if score == 21 and exactly 2 cards.
- `get_cards() -> list[Card]` — returns the list of cards in the hand.
- `clear()` — removes all cards from the hand.

### Examples

```python
card = Card(Suit.SPADES, 1)   # Ace of Spades
card.get_value()               # 11
card.is_ace()                  # True
str(card)                      # "A of Spades"

deck = Deck(seed=42)
deck.cards_remaining()         # 52
card = deck.draw()
deck.cards_remaining()         # 51

hand = Hand()
hand.add_card(Card(Suit.HEARTS, 1))   # Ace
hand.add_card(Card(Suit.CLUBS, 13))   # King
hand.get_score()                       # 21
hand.is_blackjack()                    # True
```

---

## Level 2 — Game, Player, Dealer

Implement game flow with a player and a dealer.

### Game
- `Game(balance=1000, seed=None)` — initializes the game with a deck, a player, and a dealer.
- `deal_initial_cards()` — deals 2 cards each to the player and the dealer, alternating (player, dealer, player, dealer).
- `player_hit()` — draws a card for the player. Returns the card drawn.
- `player_stand()` — ends the player's turn and triggers the dealer's turn.
- `play_dealer_turn()` — dealer draws cards until score >= 17.
- `get_result() -> str` — returns one of: `"player_win"`, `"dealer_win"`, `"draw"`, `"blackjack"`. Call after both turns are complete.
- `get_player_hand() -> Hand` — returns the player's current hand.
- `get_dealer_hand() -> Hand` — returns the dealer's current hand.

### Result Logic
1. If player busts -> `"dealer_win"`.
2. If player has blackjack and dealer does not -> `"blackjack"`.
3. If dealer busts -> `"player_win"`.
4. If both have blackjack -> `"draw"`.
5. Higher score wins; tie is `"draw"`.

### Examples

```python
game = Game(seed=42)
game.deal_initial_cards()
game.player_stand()          # triggers dealer turn
result = game.get_result()   # "player_win", "dealer_win", "draw", or "blackjack"
```

---

## Level 3 — Gambling

Add betting mechanics to the game.

### Game (extended)
- `place_bet(amount: int) -> bool` — places a bet before dealing. Returns False if amount exceeds balance or is <= 0.
- `settle_bet() -> int` — settles the current bet based on the result. Returns the net change in balance.
  - `"blackjack"` -> player wins 1.5x the bet (rounded down).
  - `"player_win"` -> player wins 1x the bet.
  - `"dealer_win"` -> player loses the bet.
  - `"draw"` -> bet is returned (no change).
- `get_balance() -> int` — returns current balance.

### Examples

```python
game = Game(balance=500, seed=42)
game.place_bet(100)
game.deal_initial_cards()
game.player_stand()
result = game.get_result()
net = game.settle_bet()      # e.g., +100 for a win, -100 for a loss
game.get_balance()           # updated balance
```

---

## Level 4 — Multi-Round and Statistics

Support multiple rounds of play with statistics tracking.

### Game (extended)
- `play_round(bet: int, actions: list[str]) -> str` — plays a full round. `actions` is a list of `"hit"` or `"stand"` strings representing the player's decisions in order. Returns the result string.
- `get_stats() -> dict` — returns a dictionary:
  ```python
  {
      "rounds_played": int,
      "wins": int,          # includes blackjacks
      "losses": int,
      "draws": int,
      "current_balance": int
  }
  ```
- The deck automatically reshuffles when fewer than 15 cards remain (checked at the start of each round).

### Examples

```python
game = Game(balance=1000, seed=42)
result = game.play_round(100, ["stand"])
stats = game.get_stats()
# stats = {"rounds_played": 1, "wins": ..., "losses": ..., "draws": ..., "current_balance": ...}
```
