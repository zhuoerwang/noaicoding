import pytest
from solution import Suit, Card, Deck, Hand, Game


# ============================================================
# Level 1: Card, Deck, Hand
# ============================================================

class TestLevel1:
    """Tests for Card, Deck, and Hand."""

    # --- Card tests ---

    def test_card_ace_value(self):
        card = Card(Suit.SPADES, 1)
        assert card.get_value() == 11
        assert card.is_ace() is True

    def test_card_number_value(self):
        card = Card(Suit.HEARTS, 7)
        assert card.get_value() == 7
        assert card.is_ace() is False

    def test_card_face_card_values(self):
        jack = Card(Suit.CLUBS, 11)
        queen = Card(Suit.DIAMONDS, 12)
        king = Card(Suit.SPADES, 13)
        assert jack.get_value() == 10
        assert queen.get_value() == 10
        assert king.get_value() == 10

    def test_card_str_ace(self):
        card = Card(Suit.SPADES, 1)
        assert str(card) == "A of Spades"

    def test_card_str_number(self):
        card = Card(Suit.HEARTS, 10)
        assert str(card) == "10 of Hearts"

    def test_card_str_face(self):
        assert str(Card(Suit.CLUBS, 11)) == "J of Clubs"
        assert str(Card(Suit.DIAMONDS, 12)) == "Q of Diamonds"
        assert str(Card(Suit.SPADES, 13)) == "K of Spades"

    # --- Deck tests ---

    def test_deck_has_52_cards(self):
        deck = Deck(seed=1)
        assert deck.cards_remaining() == 52

    def test_deck_draw_reduces_count(self):
        deck = Deck(seed=1)
        deck.draw()
        assert deck.cards_remaining() == 51

    def test_deck_draw_empty_raises(self):
        deck = Deck(seed=1)
        for _ in range(52):
            deck.draw()
        with pytest.raises(ValueError):
            deck.draw()

    def test_deck_all_unique_cards(self):
        deck = Deck(seed=1)
        cards = [deck.draw() for _ in range(52)]
        card_ids = [(c.suit, c.value) for c in cards]
        assert len(set(card_ids)) == 52

    def test_deck_seeded_is_deterministic(self):
        deck1 = Deck(seed=42)
        deck2 = Deck(seed=42)
        for _ in range(10):
            c1 = deck1.draw()
            c2 = deck2.draw()
            assert c1.suit == c2.suit and c1.value == c2.value

    def test_deck_reshuffle_restores_52(self):
        deck = Deck(seed=99)
        for _ in range(30):
            deck.draw()
        deck.reshuffle()
        assert deck.cards_remaining() == 52

    def test_deck_reshuffle_deterministic(self):
        deck = Deck(seed=42)
        first_card_a = deck.draw()
        deck.reshuffle()
        first_card_b = deck.draw()
        assert first_card_a.suit == first_card_b.suit
        assert first_card_a.value == first_card_b.value

    # --- Hand tests ---

    def test_hand_simple_score(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 5))
        hand.add_card(Card(Suit.CLUBS, 9))
        assert hand.get_score() == 14

    def test_hand_ace_as_11(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 1))
        hand.add_card(Card(Suit.CLUBS, 7))
        assert hand.get_score() == 18  # Ace=11 + 7

    def test_hand_ace_reduced_to_1(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 1))   # 11
        hand.add_card(Card(Suit.CLUBS, 9))     # 9 -> 20
        hand.add_card(Card(Suit.DIAMONDS, 5))  # 5 -> 25, reduce ace -> 15
        assert hand.get_score() == 15

    def test_hand_two_aces(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 1))    # 11
        hand.add_card(Card(Suit.CLUBS, 1))     # 11 -> 22, reduce one -> 12
        assert hand.get_score() == 12

    def test_hand_three_aces(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 1))
        hand.add_card(Card(Suit.CLUBS, 1))
        hand.add_card(Card(Suit.DIAMONDS, 1))
        # 33 -> 23 -> 13
        assert hand.get_score() == 13

    def test_hand_four_aces(self):
        hand = Hand()
        for suit in Suit:
            hand.add_card(Card(suit, 1))
        # 44 -> 34 -> 24 -> 14
        assert hand.get_score() == 14

    def test_hand_blackjack(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 1))    # Ace
        hand.add_card(Card(Suit.CLUBS, 13))    # King
        assert hand.is_blackjack() is True
        assert hand.get_score() == 21

    def test_hand_21_not_blackjack_with_3_cards(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 7))
        hand.add_card(Card(Suit.CLUBS, 7))
        hand.add_card(Card(Suit.DIAMONDS, 7))
        assert hand.get_score() == 21
        assert hand.is_blackjack() is False

    def test_hand_bust(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 10))
        hand.add_card(Card(Suit.CLUBS, 9))
        hand.add_card(Card(Suit.DIAMONDS, 5))
        assert hand.is_bust() is True

    def test_hand_clear(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 10))
        hand.clear()
        assert hand.get_score() == 0
        assert len(hand.get_cards()) == 0

    def test_hand_get_cards_returns_copy(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, 5))
        cards = hand.get_cards()
        cards.append(Card(Suit.CLUBS, 10))
        assert len(hand.get_cards()) == 1  # original unchanged


# ============================================================
# Level 2: Game, Player, Dealer
# ============================================================

class TestLevel2:
    """Tests for Game flow, dealing, hitting, standing, and result logic."""

    def test_deal_initial_cards_count(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        assert len(game.get_player_hand().get_cards()) == 2
        assert len(game.get_dealer_hand().get_cards()) == 2

    def test_deal_uses_4_cards_from_deck(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        assert game._deck.cards_remaining() == 48

    def test_player_hit_adds_card(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        card = game.player_hit()
        assert isinstance(card, Card)
        assert len(game.get_player_hand().get_cards()) == 3

    def test_player_stand_triggers_dealer(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        game.player_stand()
        # Dealer should have at least 2 cards and score >= 17
        assert game.get_dealer_hand().get_score() >= 17

    def test_result_player_bust(self):
        """Manually construct a scenario where the player busts."""
        game = Game(seed=42)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 9))
        game._player_hand.add_card(Card(Suit.DIAMONDS, 5))
        assert game.get_result() == "dealer_win"

    def test_result_dealer_bust(self):
        """Manually construct a scenario where the dealer busts."""
        game = Game(seed=42)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 8))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 10))
        game._dealer_hand.add_card(Card(Suit.SPADES, 9))
        game._dealer_hand.add_card(Card(Suit.HEARTS, 5))
        assert game.get_result() == "player_win"

    def test_result_blackjack(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 1))
        game._player_hand.add_card(Card(Suit.CLUBS, 13))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 10))
        game._dealer_hand.add_card(Card(Suit.SPADES, 8))
        assert game.get_result() == "blackjack"

    def test_result_both_blackjack_is_draw(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 1))
        game._player_hand.add_card(Card(Suit.CLUBS, 13))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 1))
        game._dealer_hand.add_card(Card(Suit.SPADES, 12))
        assert game.get_result() == "draw"

    def test_result_draw_equal_scores(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 8))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 9))
        game._dealer_hand.add_card(Card(Suit.SPADES, 9))
        assert game.get_result() == "draw"

    def test_result_player_higher(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 10))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 9))
        game._dealer_hand.add_card(Card(Suit.SPADES, 8))
        assert game.get_result() == "player_win"

    def test_result_dealer_higher(self):
        game = Game(seed=42)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 8))
        game._player_hand.add_card(Card(Suit.CLUBS, 7))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 10))
        game._dealer_hand.add_card(Card(Suit.SPADES, 9))
        assert game.get_result() == "dealer_win"

    def test_dealer_stops_at_17(self):
        """Dealer should stop hitting at exactly 17."""
        game = Game(seed=42)
        game.deal_initial_cards()
        game._dealer_hand.clear()
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 10))
        game._dealer_hand.add_card(Card(Suit.SPADES, 7))
        initial_count = len(game._dealer_hand.get_cards())
        game.play_dealer_turn()
        # Score is already 17, dealer should NOT draw
        assert len(game.get_dealer_hand().get_cards()) == initial_count


# ============================================================
# Level 3: Gambling
# ============================================================

class TestLevel3:
    """Tests for betting, balance, and payout logic."""

    def test_place_bet_valid(self):
        game = Game(balance=1000, seed=42)
        assert game.place_bet(100) is True

    def test_place_bet_exceeds_balance(self):
        game = Game(balance=100, seed=42)
        assert game.place_bet(200) is False

    def test_place_bet_zero(self):
        game = Game(balance=1000, seed=42)
        assert game.place_bet(0) is False

    def test_place_bet_negative(self):
        game = Game(balance=1000, seed=42)
        assert game.place_bet(-50) is False

    def test_settle_bet_player_win(self):
        game = Game(balance=1000, seed=42)
        game.place_bet(100)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 10))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 9))
        game._dealer_hand.add_card(Card(Suit.SPADES, 8))
        net = game.settle_bet()
        assert net == 100
        assert game.get_balance() == 1100

    def test_settle_bet_dealer_win(self):
        game = Game(balance=1000, seed=42)
        game.place_bet(100)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 9))
        game._player_hand.add_card(Card(Suit.DIAMONDS, 5))  # bust
        net = game.settle_bet()
        assert net == -100
        assert game.get_balance() == 900

    def test_settle_bet_draw(self):
        game = Game(balance=1000, seed=42)
        game.place_bet(100)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 8))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 9))
        game._dealer_hand.add_card(Card(Suit.SPADES, 9))
        net = game.settle_bet()
        assert net == 0
        assert game.get_balance() == 1000

    def test_settle_bet_blackjack_pays_1_5x(self):
        game = Game(balance=1000, seed=42)
        game.place_bet(100)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 1))
        game._player_hand.add_card(Card(Suit.CLUBS, 13))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 10))
        game._dealer_hand.add_card(Card(Suit.SPADES, 8))
        net = game.settle_bet()
        assert net == 150
        assert game.get_balance() == 1150

    def test_settle_bet_blackjack_odd_bet_rounds_down(self):
        game = Game(balance=1000, seed=42)
        game.place_bet(75)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 1))
        game._player_hand.add_card(Card(Suit.CLUBS, 13))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 10))
        game._dealer_hand.add_card(Card(Suit.SPADES, 8))
        net = game.settle_bet()
        assert net == 112  # int(75 * 1.5) = 112
        assert game.get_balance() == 1112

    def test_balance_after_multiple_bets(self):
        game = Game(balance=500, seed=42)

        # Win
        game.place_bet(100)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 10))
        game._dealer_hand.add_card(Card(Suit.DIAMONDS, 9))
        game._dealer_hand.add_card(Card(Suit.SPADES, 8))
        game.settle_bet()
        assert game.get_balance() == 600

        # Lose
        game.place_bet(200)
        game.deal_initial_cards()
        game._player_hand.clear()
        game._dealer_hand.clear()
        game._player_hand.add_card(Card(Suit.HEARTS, 10))
        game._player_hand.add_card(Card(Suit.CLUBS, 9))
        game._player_hand.add_card(Card(Suit.DIAMONDS, 5))  # bust
        game.settle_bet()
        assert game.get_balance() == 400

    def test_place_bet_exact_balance(self):
        game = Game(balance=100, seed=42)
        assert game.place_bet(100) is True

    def test_get_balance_initial(self):
        game = Game(balance=750, seed=42)
        assert game.get_balance() == 750


# ============================================================
# Level 4: Multi-Round and Statistics
# ============================================================

class TestLevel4:
    """Tests for multi-round play and statistics tracking."""

    def test_play_round_returns_valid_result(self):
        game = Game(balance=1000, seed=42)
        result = game.play_round(100, ["stand"])
        assert result in ("player_win", "dealer_win", "draw", "blackjack")

    def test_play_round_updates_stats(self):
        game = Game(balance=1000, seed=42)
        game.play_round(100, ["stand"])
        stats = game.get_stats()
        assert stats["rounds_played"] == 1
        assert stats["wins"] + stats["losses"] + stats["draws"] == 1

    def test_play_round_updates_balance(self):
        game = Game(balance=1000, seed=42)
        result = game.play_round(100, ["stand"])
        balance = game.get_balance()
        if result in ("player_win", "blackjack"):
            assert balance > 1000
        elif result == "dealer_win":
            assert balance < 1000
        else:
            assert balance == 1000

    def test_multiple_rounds_stats_accumulate(self):
        game = Game(balance=5000, seed=42)
        for _ in range(10):
            game.play_round(50, ["stand"])
        stats = game.get_stats()
        assert stats["rounds_played"] == 10
        assert stats["wins"] + stats["losses"] + stats["draws"] == 10

    def test_play_round_with_hits(self):
        game = Game(balance=1000, seed=100)
        result = game.play_round(50, ["hit", "stand"])
        assert result in ("player_win", "dealer_win", "draw", "blackjack")
        stats = game.get_stats()
        assert stats["rounds_played"] == 1

    def test_play_round_hit_until_bust(self):
        """Player hits many times; should eventually bust or complete."""
        game = Game(balance=1000, seed=55)
        result = game.play_round(50, ["hit", "hit", "hit", "hit", "hit"])
        assert result in ("player_win", "dealer_win", "draw", "blackjack")

    def test_reshuffle_when_low_cards(self):
        game = Game(balance=10000, seed=42)
        # Play many rounds to deplete the deck
        for _ in range(20):
            game.play_round(10, ["stand"])
        # Should not crash — deck reshuffles automatically
        assert game._deck.cards_remaining() >= 0
        stats = game.get_stats()
        assert stats["rounds_played"] == 20

    def test_stats_structure(self):
        game = Game(balance=1000, seed=42)
        stats = game.get_stats()
        assert "rounds_played" in stats
        assert "wins" in stats
        assert "losses" in stats
        assert "draws" in stats
        assert "current_balance" in stats

    def test_stats_initial(self):
        game = Game(balance=1000, seed=42)
        stats = game.get_stats()
        assert stats["rounds_played"] == 0
        assert stats["wins"] == 0
        assert stats["losses"] == 0
        assert stats["draws"] == 0
        assert stats["current_balance"] == 1000

    def test_stats_current_balance_matches_get_balance(self):
        game = Game(balance=1000, seed=42)
        game.play_round(100, ["stand"])
        stats = game.get_stats()
        assert stats["current_balance"] == game.get_balance()

    def test_play_round_stand_immediately(self):
        """Standing immediately is valid — no hits."""
        game = Game(balance=1000, seed=99)
        result = game.play_round(100, ["stand"])
        assert result in ("player_win", "dealer_win", "draw", "blackjack")
        assert game.get_stats()["rounds_played"] == 1

    def test_wins_include_blackjacks(self):
        """If a blackjack result occurs, it should count toward wins."""
        game = Game(balance=10000, seed=42)
        blackjack_seen = False
        for _ in range(100):
            result = game.play_round(10, ["stand"])
            if result == "blackjack":
                blackjack_seen = True
                break
        if blackjack_seen:
            stats = game.get_stats()
            assert stats["wins"] >= 1
