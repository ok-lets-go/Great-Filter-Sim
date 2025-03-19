import random

class Die:
    def __init__(self):
        self.value_options = (4, 6, 8, 10, 12, 20)
        self.value_index = 0
        self.value = self.value_options[self.value_index]
        self.die_resources = {
            1: 'water',
            2: 'food',
            3: 'wood',
            4: 'brick'
        }

        self.die_upgrade_cost = {
            0: 3,
            1: 4,
            2: 5,
            3: 6,
            4: 7,
        }

    def promote(self):
        self.value_index += 1
        self.value = self.value_options[self.value_index]

    def roll(self):
        return random.randint(1, self.value)


class Player:
    def __init__(self, name="Bot"):
        self.name = name
        self.dice = [Die()]
        self.roll_values = None

        self.resources = {
            'water': 0,
            'food': 0,
            'wood': 0,
            'brick': 0
        }

    def roll_dice(self):
        self.roll_values = []
        for die in self.dice:
            self.roll_values.append((f"d{die.value}", die.roll()))

        for value in self.roll_values:
            self.resources[die.die_resources[value[1]]] += 1


class Game:
    def __init__(self):
        default_names = ["John", "Mike", "Steve"]

        print("\n")
        print("Player Names \n")
        self.players = []
        if (input("Default Names? ") != 'yes'):
            self.number_players = int(input("How Many Players? Entry: "))
            for n in range(self.number_players):
                self.players.append(Player(input(f"Player {n+1}: ")))

        else:
            self.number_players = 3
            for n in range(self.number_players):
                self.players.append(Player(default_names[n]))

        self.round_number = 1
        self.active_player_index = 0
        self.active_player: Player = None
        print('\n')
        print("Round 1")
        self.game_loop()

    def game_loop(self):  
        self.active_player: Player = self.players[self.active_player_index%self.number_players]
        print(f"{self.active_player.name}, what would you like to do? (roll=Roll Dice, view=View Stats, shop=Visit Shop, quit=Exit Game)")
        action = input("Action: ")
        if action == "roll":
            self.roll()
        elif action == "view":
            self.view_stats()
        elif action == "shop":
            self.shop()
        elif action == 'quit':
            quit()
        else:
            print("Invalid input, try again")
        print('\n')
        self.game_loop()

    def roll(self):
        self.active_player.roll_dice()
        roll_results = self.active_player.roll_values
        print(f'{self.active_player.name}: {roll_results}\n')
        self.next_player()


    def view_stats(self):
        resources = self.active_player.resources
        print(f'{self.active_player.name}: {resources}')

    def shop(self):
        print("Purchase or upgrade? (all lowercase)")
        action = input("Action: ")
        
        if action == "purchase":
            action_performed = self.purchase()
            if action_performed: 
                pass
            else: 
                self.shop()

        elif action == "upgrade":
            action_performed = self.upgrade() 
            if action_performed: 
                pass
            else: 
                self.shop()
        elif action == "quit":
            return
        else: 
            print("Invalid input, try again")
            action_performed = False
        if action_performed: 
            self.next_player()


    def purchase(self):
        if self.active_player.resources[''] >= 3: 
            print("Confirm die purchase? (y/n)")
            confirmation = 'invalid'
            while confirmation == 'invalid':
                confirmation = self.confirm()
            if confirmation: 
                self.active_player.dice.append(Die())
                self.active_player.resources['gold'] -= 3
                return True
            else: 
                return False
        else: 
            print("Insufficient funds")
            return False


    def upgrade(self):
        
        print(self.active_player.name)
        print([f"{index}: d{die.value}" for index, die in enumerate(self.active_player.dice)])
        print("Choose index of die to upgrade")
        response = int(input("selection="))
        print('\n')
        if self.active_player.resources['gold'] >= self.active_player.dice[response].die_upgrade_cost[self.active_player.dice[response].value_index]: 

            print(f"Confirm you want to upgrade your d{self.active_player.dice[response].value} (y/n)")
            confirmation = 'invalid'
            while confirmation == "invalid":
                confirmation = self.confirm()
            if confirmation: 
                self.players[self.active_player_index].dice[response].promote()
                print("Promoted\n")
                return True
            else: 
                print("Cancelled\n")
                return False
            
        else: 
            print("Insufficient funds\n")
            return False

    def confirm(self): 
        confirmation = input("Confirm: ")
        if confirmation == 'y':
            return True
        elif confirmation == 'n':
            return False
        else: 
            print("Try Again")
            return "invalid"
        

    def next_player(self): 
        self.active_player_index +=1
        if self.active_player_index%self.number_players == 0: 
            self.round_number += 1
            print(f"Round {self.round_number}")

if __name__ == "__main__":
    Game()
