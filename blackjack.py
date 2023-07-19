import random
from gymnasium import Env
from gymnasium import spaces

DECK_COUNT = 6

class BlackjackEnv(Env):
    def __init__(self, render_mode=None):
        super().__init__()
        '''
        self.action_space = spaces.Dict({
            "move": spaces.Discrete(3), # 0 stand, 1 hit, 2 double down
            "bet_amount": spaces.Discrete(cur_funds) # Betting amount
        })
        '''
        self.action_space = spaces.Discrete(2) # 0 stand 1 hit
        self.observation_space = spaces.Dict({
            "player_hand": spaces.MultiDiscrete([14] * 13), # Player's hand, 0 is no card
            "dealer_card": spaces.Discrete(13, start=1),  # Dealer's showing card
            "player_ace": spaces.Discrete(2),   # Whether the player has a usable Ace
            "dealer_ace": spaces.Discrete(2), # Whether the dealer has a usable Ace
            "played_cards": spaces.MultiDiscrete([14] * (13 * 4 * DECK_COUNT)) # Discarded cards
            #"cur_funds": spaces.Discrete(1e9) # Current funds
        })
        #self.initial_funds = cur_funds
        #self.cur_funds = cur_funds
        #self.bet_amount = None
        self.deck = None
        self.player_hand = None
        self.dealer_hand = None
        self.played_cards = None
        self.player_ace = None
        self.dealer_ace = None
        self.render_mode = render_mode
    def reset(self):
        #self.cur_funds = self.initial_funds
        #self.bet_amount = 0
        self.deck = self.create_deck()
        self.reset_game()
        return self._get_obs(), {}
    def step(self, action):
        reward = 0
        terminated = False
        if action:
            self.add_card(True)
            if self.calculate_hand_value(self.player_hand) > 21:
                reward = -10
                terminated = self.reset_game()
        else:
            while self.calculate_hand_value(self.dealer_hand) < 17:
                self.add_card(False)
            player_value = self.calculate_hand_value(self.player_hand)
            dealer_value = self.calculate_hand_value(self.dealer_hand)
            if player_value > 21:
                reward = -10
            elif dealer_value > 21:
                reward = 10
            elif player_value > dealer_value:
                reward = 10
            elif dealer_value > player_value:
                reward = -10
            terminated = self.reset_game()
        return self._get_obs(), reward, terminated, False, {}
    
    def render(self):
        if self.render_mode == "console":
            print("Player: ")
            self.print_hand(self.player_hand)
            print("Dealer: ")
            self.print_hand(self.dealer_hand)

    def close(self):
        return super().close()

    def _get_obs(self):
        return {"player_hand": (self.player_hand + [0] * 13)[:13], "dealer_card": self.dealer_hand[0], "player_ace": self.player_ace, "dealer_ace": self.dealer_ace, "played_cards": self.played_cards}
    
    def reset_game(self):
        if len(self.deck) < 20:
            return True
        self.player_hand = []
        self.dealer_hand = []
        self.player_ace = False
        self.dealer_ace = False
        self.add_card(True, 2)
        self.add_card(False, 2)
        return False

    def add_card(self, player, count=1):
        for i in range(count):
            card = self.deck.pop()
            if player:
                self.player_hand.append(card)
                if card == 1:
                    self.player_ace = True
            else:
                self.dealer_hand.append(card)
                if card == 1:
                    self.dealer_ace = True
            if len(self.deck) < 20:
                self.deck = self.create_deck()
                self.played_cards = []

    def create_deck(self):
        # Create a deck of cards
        deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] * 4 * DECK_COUNT
        random.shuffle(deck)
        return deck

    def get_card_value(self, card):
        # Return the numerical value of a card
        rank = card[0]
        if rank > 10:
            return 10
        elif rank == 1:
            return 11
        else:
            return rank

    def calculate_hand_value(self, hand):
        # Calculate the value of a hand
        value = sum(self.get_card_value(card) for card in hand)
        # Adjust for aces
        num_aces = sum(1 for card in hand if card[0] == 1)
        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1
        return value

    def print_hand(self, hand):
        # Print the cards in a hand
        for card in hand:
            print(f"{card[0]} of {card[1]}")
        print("Current score: {}".format(self.calculate_hand_value(hand))) 

    
    def blackjack_game(self):
        deck = self.create_deck()
        player_hand = []
        dealer_hand = []
        player_money = 1000

        while True:
            print(f"Your current balance: ${player_money}")
            bet = int(input("Enter your bet (0 to quit): "))
            if bet == 0:
                break

            # Deal initial cards
            player_hand.append(deck.pop())
            dealer_hand.append(deck.pop())
            player_hand.append(deck.pop())
            dealer_hand.append(deck.pop())

            # Player's turn
            print("Player's Hand:")
            self.print_hand(player_hand)
            while True:
                choice = input("Do you want to hit or stand? (h/s): ").lower()
                if choice == "h":
                    player_hand.append(deck.pop())
                    print("Player's Hand:")
                    self.print_hand(player_hand)
                    if self.calculate_hand_value(player_hand) > 21:
                        print("Bust! You lose.")
                        player_money -= bet
                        break
                elif choice == "s":
                    break

            # Dealer's turn
            print("Dealer's Hand:")
            self.print_hand(dealer_hand)
            while self.calculate_hand_value(dealer_hand) < 17:
                dealer_hand.append(deck.pop())
                print("Dealer hits.")
                print("Dealer's Hand:")
                self.print_hand(dealer_hand)

            # Determine the winner
            player_value = self.calculate_hand_value(player_hand)
            dealer_value = self.calculate_hand_value(dealer_hand)
            print(f"Player's hand value: {player_value}")
            print(f"Dealer's hand value: {dealer_value}")

            if player_value > 21:
                print("Player busts! You lose.")
                player_money -= bet
            elif dealer_value > 21:
                print("Dealer busts! You win.")
                player_money += bet
            elif player_value > dealer_value:
                print("You win!")
                player_money += bet
            elif dealer_value > player_value:
                print("You lose.")
                player_money -= bet
            else:
                print("Push! It's a tie.")

            # Clear hands for the next round
            player_hand.clear()
            dealer_hand.clear()

            # Check if the deck needs to be reshuffled
            if len(deck) < 20:
                print("Reshuffling the deck...")
                deck = self.create_deck()

            if player_money <= 0:
                print("You're out of money! Game over.")
                break

        print("Thanks for playing!")

