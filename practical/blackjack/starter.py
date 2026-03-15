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


class Card:
    """
    Represents a single playing card.

    Args:
        suit: The suit of the card (Suit enum).
        value: Integer 1-13 where 1=Ace, 11=Jack, 12=Queen, 13=King.
    """

    def __init__(self, suit: Suit, value: int) -> None:
        pass

    def get_value(self) -> int:
        """
        Returns the blackjack point value of this card.
        2-10 -> face value, J/Q/K -> 10, Ace -> 11.
        (Ace adjustment for busting is handled by Hand.)
        """
        pass

    def is_ace(self) -> bool:
        """Returns True if this card is an Ace."""
        pass

    def __str__(self) -> str:
        """
        String representation, e.g. 'A of Spades', '10 of Hearts', 'K of Clubs'.
        """
        pass


class Deck:
    """
    A standard 52-card deck with shuffle and draw operations.

    Args:
        seed: Optional random seed for reproducible shuffling.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        pass

    def draw(self) -> Card:
        """
        Removes and returns the top card from the deck.
        Raises ValueError if the deck is empty.
        """
        pass

    def cards_remaining(self) -> int:
        """Returns the number of cards left in the deck."""
        pass

    def reshuffle(self) -> None:
        """Resets to a full 52-card deck and shuffles (using original seed if provided)."""
        pass


class Hand:
    """
    Represents a player's hand of cards with score calculation.
    Handles ace logic: aces count as 11 unless that would bust,
    then they count as 1 (adjusted one at a time).
    """

    def __init__(self) -> None:
        pass

    def add_card(self, card: Card) -> None:
        """Adds a card to the hand."""
        pass

    def get_score(self) -> int:
        """
        Calculates the best score for this hand.
        Aces start as 11 and are reduced to 1 one at a time if total > 21.
        """
        pass

    def is_bust(self) -> bool:
        """Returns True if the hand's score exceeds 21."""
        pass

    def is_blackjack(self) -> bool:
        """Returns True if the hand is a blackjack (score 21 with exactly 2 cards)."""
        pass

    def get_cards(self) -> list:
        """Returns the list of cards in the hand."""
        pass

    def clear(self) -> None:
        """Removes all cards from the hand."""
        pass


# ============================================================
# Level 2: Game with Player and Dealer
# ============================================================

class Game:
    """
    Blackjack game engine.

    Args:
        balance: Starting balance for the player (used in L3).
        seed: Optional random seed for the deck.
    """

    def __init__(self, balance: int = 1000, seed: Optional[int] = None) -> None:
        pass

    def deal_initial_cards(self) -> None:
        """Deals 2 cards each to player and dealer, alternating (player, dealer, player, dealer)."""
        pass

    def player_hit(self) -> Card:
        """Draws a card for the player. Returns the card drawn."""
        pass

    def player_stand(self) -> None:
        """Ends the player's turn and triggers the dealer's turn."""
        pass

    def play_dealer_turn(self) -> None:
        """Dealer draws cards until their score is >= 17."""
        pass

    def get_result(self) -> str:
        """
        Returns the result of the current round.
        Returns one of: 'player_win', 'dealer_win', 'draw', 'blackjack'.
        """
        pass

    def get_player_hand(self) -> Hand:
        """Returns the player's current hand."""
        pass

    def get_dealer_hand(self) -> Hand:
        """Returns the dealer's current hand."""
        pass

    # ============================================================
    # Level 3: Gambling
    # ============================================================

    def place_bet(self, amount: int) -> bool:
        """
        Places a bet before dealing.
        Returns False if amount exceeds balance or is <= 0.
        """
        pass

    def settle_bet(self) -> int:
        """
        Settles the current bet based on the result.
        Returns the net change in balance.
        - 'blackjack' -> +1.5x bet (rounded down)
        - 'player_win' -> +1x bet
        - 'dealer_win' -> -1x bet
        - 'draw' -> 0
        """
        pass

    def get_balance(self) -> int:
        """Returns the player's current balance."""
        pass

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
            The result string ('player_win', 'dealer_win', 'draw', 'blackjack').
        """
        pass

    def get_stats(self) -> dict:
        """
        Returns game statistics:
        {
            'rounds_played': int,
            'wins': int,          # includes blackjacks
            'losses': int,
            'draws': int,
            'current_balance': int
        }
        """
        pass
