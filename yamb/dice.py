import random

class Dice: 
    def __init__(self, index):
        self.index = index
        self.value = 6 

    def roll(self):
        self.value = random.randint(1, 6)