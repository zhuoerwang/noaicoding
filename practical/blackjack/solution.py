import random
from enum import Enum
from typing import Optional


# ============================================================
# Level 1: Card, Deck, Hand
# ============================================================

class Suit(Enum):
    """Enum representing the four card suits."""
    CLUBS = "Clubs"
    DIAMONDS = "Diamonds"
    HEARTS = "Hearts"
    SPADES = "Spades"


VALUE_NAMES = {
    1: "A", 11: "J", 12: "Q", 13: "K"
}


class Card:
    """
    Represents a single playing card.

    Args:
        suit: The suit of the card (Suit enum).
        value: Integer 1-13 where 1=Ace, 11=Jack, 12=Queen, 13=King.
    """

    def __init__(self, suit: Suit, value: int) -> None:
        self.suit = suit
        self.value = value

    def get_value(self) -> int:
        """
        Returns the blackjack point value of this card.
        2-10 -> face value, J/Q/K -> 10, Ace -> 11.
        """
        if self.value == 1:
            return 11
        elif self.value >= 11:
            return 10
        else:
            return self.value

    def is_ace(self) -> bool:
        """Returns True if this card is an Ace."""
        return self.value == 1

    def __str__(self) -> str:
        """String representation, e.g. 'A of Spades', '10 of Hearts', 'K of Clubs'."""
        name = VALUE_NAMES.get(self.value, str(self.value))
        return f"{name} of {self.suit.value}"

    def __repr__(self) -> str:
        return self.__str__()


class Deck:
    """
    A standard 52-card deck with shuffle and draw operations.

    Args:
        seed: Optional random seed for reproducible shuffling.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self._seed = seed
        self._rng = random.Random(seed)
        self._cards: list[Card] = []
        self._build_and_shuffle()

    def _build_and_shuffle(self) -> None:
        """Creates a full 52-card deck and shuffles it."""
        self._cards = [
            Card(suit, value)
            for suit in Suit
            for value in range(1, 14)
        ]
        self._rng.shuffle(self._cards)

    def draw(self) -> Card:
        """
        Removes and returns the top card from the deck.
        Raises ValueError if the deck is empty.
        """
        if not self._cards:
            raise ValueError("Cannot draw from an empty deck")
        return self._cards.pop()

    def cards_remaining(self) -> int:
        """Returns the number of cards left in the deck."""
        return len(self._cards)

    def reshuffle(self) -> None:
        """Resets to a full 52-card deck and shuffles (using original seed if provided)."""
        self._rng = random.Random(self._seed)
        self._build_and_shuffle()


class Hand:
    """
    Represents a player's hand of cards with score calculation.
    """

    def __init__(self) -> None:
        self._cards: list[Card] = []

    def add_card(self, card: Card) -> None:
        """Adds a card to the hand."""
        self._cards.append(card)

    def get_score(self) -> int:
        """
        Calculates the best score for this hand.
        Aces start as 11 and are reduced to 1 one at a time if total > 21.
        """
        total = sum(card.get_value() for card in self._cards)
        aces = sum(1 for card in self._cards if card.is_ace())

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def is_bust(self) -> bool:
        """Returns True if the hand's score exceeds 21."""
        return self.get_score() > 21

    def is_blackjack(self) -> bool:
        """Returns True if the hand is a blackjack (score 21 with exactly 2 cards)."""
        return len(self._cards) == 2 and self.get_score() == 21

    def get_cards(self) -> list:
        """Returns the list of cards in the hand."""
        return list(self._cards)

    def clear(self) -> None:
        """Removes all cards from the hand."""
        self._cards.clear()


# ============================================================
# Level 2: Game with Player and Dealer
# ============================================================

class Game:
    """
    Blackjack game engine.

    Args:
        balance: Starting balance for the player.
        seed: Optional random seed for the deck.
    """

    def __init__(self, balance: int = 1000, seed: Optional[int] = None) -> None:
        self._deck = Deck(seed=seed)
        self._player_hand = Hand()
        self._dealer_hand = Hand()
        self._balance = balance
        self._current_bet = 0
        self._result: Optional[str] = None

        # Level 4 stats
        self._rounds_played = 0
        self._wins = 0
        self._losses = 0
        self._draws = 0

    def deal_initial_cards(self) -> None:
        """Deals 2 cards each to player and dealer, alternating."""
        self._player_hand.clear()
        self._dealer_hand.clear()
        self._result = None

        # Alternate: player, dealer, player, dealer
        self._player_hand.add_card(self._deck.draw())
        self._dealer_hand.add_card(self._deck.draw())
        self._player_hand.add_card(self._deck.draw())
        self._dealer_hand.add_card(self._deck.draw())

    def player_hit(self) -> Card:
        """Draws a card for the player. Returns the card drawn."""
        card = self._deck.draw()
        self._player_hand.add_card(card)
        return card

    def player_stand(self) -> None:
        """Ends the player's turn and triggers the dealer's turn."""
        self.play_dealer_turn()

    def play_dealer_turn(self) -> None:
        """Dealer draws cards until their score is >= 17."""
        while self._dealer_hand.get_score() < 17:
            self._dealer_hand.add_card(self._deck.draw())

    def get_result(self) -> str:
        """
        Returns the result of the current round.
        Returns one of: 'player_win', 'dealer_win', 'draw', 'blackjack'.
        """
        if self._result is not None:
            return self._result

        player_score = self._player_hand.get_score()
        dealer_score = self._dealer_hand.get_score()
        player_bj = self._player_hand.is_blackjack()
        dealer_bj = self._dealer_hand.is_blackjack()

        if self._player_hand.is_bust():
            self._result = "dealer_win"
        elif player_bj and dealer_bj:
            self._result = "draw"
        elif player_bj:
            self._result = "blackjack"
        elif self._dealer_hand.is_bust():
            self._result = "player_win"
        elif player_score > dealer_score:
            self._result = "player_win"
        elif dealer_score > player_score:
            self._result = "dealer_win"
        else:
            self._result = "draw"

        return self._result

    def get_player_hand(self) -> Hand:
        """Returns the player's current hand."""
        return self._player_hand

    def get_dealer_hand(self) -> Hand:
        """Returns the dealer's current hand."""
        return self._dealer_hand

    # ============================================================
    # Level 3: Gambling
    # ============================================================

    def place_bet(self, amount: int) -> bool:
        """
        Places a bet before dealing.
        Returns False if amount exceeds balance or is <= 0.
        """
        if amount <= 0 or amount > self._balance:
            return False
        self._current_bet = amount
        return True

    def settle_bet(self) -> int:
        """
        Settles the current bet based on the result.
        Returns the net change in balance.
        """
        result = self.get_result()
        net = 0

        if result == "blackjack":
            net = int(self._current_bet * 1.5)
        elif result == "player_win":
            net = self._current_bet
        elif result == "dealer_win":
            net = -self._current_bet
        else:  # draw
            net = 0

        self._balance += net
        self._current_bet = 0
        return net

    def get_balance(self) -> int:
        """Returns the player's current balance."""
        return self._balance

    # ============================================================
    # Level 4: Multi-Round and Statistics
    # ============================================================

    def play_round(self, bet: int, actions: list) -> str:
        """
        Plays a full round of blackjack.

        Args:
            bet: Amount to bet.
            actions: List of 'hit' or 'stand' strings for player decisions.

        Returns:
            The result string.
        """
        # Reshuffle if fewer than 15 cards remain
        if self._deck.cards_remaining() < 15:
            self._deck.reshuffle()

        self.place_bet(bet)
        self.deal_initial_cards()

        # Process player actions
        for action in actions:
            if action == "hit":
                self.player_hit()
                if self._player_hand.is_bust():
                    break
            elif action == "stand":
                break

        # If player didn't bust and didn't get blackjack, play dealer turn
        if not self._player_hand.is_bust() and not self._player_hand.is_blackjack():
            self.play_dealer_turn()

        result = self.get_result()
        self.settle_bet()

        # Update stats
        self._rounds_played += 1
        if result in ("player_win", "blackjack"):
            self._wins += 1
        elif result == "dealer_win":
            self._losses += 1
        else:
            self._draws += 1

        return result

    def get_stats(self) -> dict:
        """Returns game statistics."""
        return {
            "rounds_played": self._rounds_played,
            "wins": self._wins,
            "losses": self._losses,
            "draws": self._draws,
            "current_balance": self._balance,
        }
