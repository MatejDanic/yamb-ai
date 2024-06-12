import random
from constants import DICE_ART
from util import int_to_binary_array

class DiceGame:
    def __init__(self):
        self.dices = [1, 2, 3, 4, 5]
        self.roll_count = 0
        self.roll_dice(31)

    def reset(self):
        self.dices = [1, 2, 3, 4, 5]
        self.roll_count = 0
        self.roll_dice(31)

    def roll_dice(self, dice_to_roll):
        dice_to_roll = int_to_binary_array(dice_to_roll)
        self.dices = tuple(sorted([random.randint(1, 6) if dice_to_roll[i] == 1 else self.dices[i] for i in range(5)]))
        self.roll_count += 1

    def validate_roll_dice(self) -> bool:
        return self.roll_count < 3

    def is_completed(self):
        return self.roll_count == 3
    
    def __str__(self):
        lines = ['  '.join(DICE_ART[dice][line] for dice in self.dices) for line in range(5)]
        return "\n".join(lines)

if __name__ == "__main__":
    game = DiceGame()
    print(game)


