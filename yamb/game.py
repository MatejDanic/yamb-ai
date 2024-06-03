from .dice import Dice
from .sheet import Sheet
from utils.score_calculator import calculate_score

class Game:

    def __init__(self):
        self.announcement = None  # announcement of the game
        self.roll_count = 0  # number of rolls
        self.dices = [Dice(i) for i in range(5)]
        self.sheet = Sheet()

    def roll_dice(self, diceToRoll):
        if not self.validate_roll_dice():
            return
        for i in diceToRoll:
            self.dices[i].roll()
        self.roll_count += 1
    
    def validate_roll_dice(self):
        if self.roll_count == 3:
            return False
        elif self.is_announcement_required():
            return False
        return True

    def fill_box(self, column, box):
        if not self.validate_fill_box(column, box):
            return
        self.sheet.fill_box(column, box, calculate_score([dice.value for dice in self.dices], box))
        self.roll_count = 0
        self.announcement = None
        
    def validate_fill_box(self, column, box):
        if self.roll_count == 0:
            return False
        elif not self.is_box_available(column, box):
            return False
        return True

    def announce(self, box):
        if not self.validate_announce(box):
            return
        self.announcement = box
    
    def validate_announce(self, box):
        if self.announcement is not None:
            return False
        elif self.roll_count != 1:
            return False
        return True

    def is_box_available(self, column, box):
        if self.sheet.columns[column].boxes[box].value is not None:
            return False
        if self.announcement is not None:
            return column == 3 and box == self.announcement
        elif column == 2:
            return True
        elif column == 0:
            return box == 0 or self.sheet.columns[column].boxes[box - 1].value is not None
        elif column == 1:
            return box == 12 or self.sheet.columns[column].boxes[box + 1].value is not None
        elif column == 3:
            return box == self.announcement
        return False

    def is_completed(self):
        return self.sheet.is_completed()
    
    def to_simplified(self):
        return {
            "announcement": self.announcement,
            "roll_count": self.roll_count,
            "dices": { 
                dice.index: dice.value for dice in self.dices 
            },
            "sheet": {
                column.type: {
                    box.type: box.value for box in column.boxes
                } for column in self.sheet.columns
            }
        }
    
    def is_announcement_required(self):
        return self.roll_count == 1 and self.announcement is None and self.sheet.are_all_non_anouncement_columns_completed()
    
    def get_potential_score(self):
        if self.is_completed():
            return 0
        potential_scores = []
        for column in range(4):
            for box in range(13):
                if self.is_box_available(column, box):
                    potential_scores.append(calculate_score([dice.value for dice in self.dices], box))
        return max(potential_scores)