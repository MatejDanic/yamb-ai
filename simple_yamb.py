import random
from dice_game import DiceGame
from util import dice_combination_score_map
from constants import DICE_ART, BOX_WIDTH, COLUMN_TYPES, ROW_HEADER_WIDTH, BORDERS, BOX_TYPES

class SimpleYamb(DiceGame):
    def __init__(self):
        super().__init__()  
        self.sheet = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]  

    def reset(self):
        super().reset()
        self.sheet = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]  

    def roll_dice(self, dice_to_roll):
        binary_str = f"{dice_to_roll:05b}"
        self.dices = tuple(sorted([random.randint(1, 6) if binary_str[i] == '1' else self.dices[i] for i in range(5)]))
        self.roll_count += 1
    
    def validate_roll_dice(self):
        return self.roll_count < 3 and not self.is_announcement_required()

    def fill_box(self, column, box):
        self.sheet[column][box] = dice_combination_score_map[(self.dices, box)]
        self.roll_count = 0
        self.announcement = -1
        self.roll_dice(31)
        
    def validate_fill_box(self, column, box):
        return self.roll_count > 0 and self.is_box_available(column, box)

    def is_box_available(self, column, box):
        if self.sheet[column][box] == -1:
            if column == 0:
                return box == 0 or self.sheet[column][box - 1] != -1
            elif column == 1:
                return box == 12 or self.sheet[column][box + 1] != -1
            elif column == 3:
                return box == self.announcement
            return column == 2
        return False

    def is_completed(self):
        return all(all(box != -1 for box in column) for column in self.sheet) 

    def get_total_sum(self):
        return self.get_top_sum() + self.get_middle_difference() + self.get_bottom_sum()

    def get_top_sum(self):
        return sum(self.get_top_sum_column(column) for column in self.sheet)

    def get_top_sum_column(self, column):
        top_sum = sum(box if box != -1 else 0 for box in column[:6])
        return top_sum + 30 if top_sum >= 60 else top_sum
        
    def get_middle_difference(self):
        return sum(self.get_middle_difference_column(column) for column in self.sheet)

    def get_middle_difference_column(self, column):
        return (column[6] - column[7]) * column[0] if column[6] != -1 and column[7] != -1 and column[0] != -1 else 0

    def get_bottom_sum(self):
        return sum(self.get_bottom_sum_column(column) for column in self.sheet)

    def get_bottom_sum_column(self, column):
        return sum(box if box != -1 else 0 for box in column[8:])   
        
    def __repr__(self):
        lines = ['  '.join(DICE_ART[dice][line] for dice in self.dices) for line in range(5)]
        if len(self.sheet) == 0:
            return "\n".join(lines)

        column_headers = " ".join(f"{label:^{BOX_WIDTH}}" for label in COLUMN_TYPES)
        header_row = f"{'':^{ROW_HEADER_WIDTH + 3}}{column_headers}"
        lines.extend([header_row, BORDERS["border_top"]])

        top_sum = [self.get_top_sum_column(col) for col in self.sheet]
        middle_difference = [self.get_middle_difference_column(col) for col in self.sheet]
        bottom_sum = [self.get_bottom_sum_column(col) for col in self.sheet]

        column_totals = [top + mid + bottom for top, mid, bottom in zip(top_sum, middle_difference, bottom_sum)]
        grand_total = sum(column_totals)

        for row_idx, label in enumerate(BOX_TYPES):
            if row_idx == 6:
                lines.append(format_total_row('Σ(1-6)', top_sum))
                lines.append(BORDERS["long_border_bottom"])
            elif row_idx == 8:
                lines.append(format_total_row('Δ', middle_difference))
                lines.append(BORDERS["long_border_bottom"])
            
            row = "│".join(f"{self.sheet[column][row_idx] if self.sheet[column][row_idx] != -1 else ' ':^{BOX_WIDTH}}" for column in range(len(self.sheet)))
            row = f"  {label:<{ROW_HEADER_WIDTH}} │{row}│"
            lines.append(row)
            
            if row_idx in [5, 7, 12]:
                lines.append(BORDERS["long_border_top"])
            else:
                lines.append(BORDERS["border"])

        lines.append(format_total_row('Σ', bottom_sum))
        lines.append(BORDERS["long_border_bottom_final"])

        grand_total_row = f"{'':^{(ROW_HEADER_WIDTH + 3) + (BOX_WIDTH + 1) * 3}}│{grand_total:^{BOX_WIDTH * 2 + 1}}│"
        lines.append(grand_total_row)
        lines.append(BORDERS["border_bottom_final"])

        return "\n".join(lines)

def format_total_row(label, values):
    total_sum = sum(values)
    return f"│{label:^{ROW_HEADER_WIDTH + 2}}│" + "│".join(f"{value:^{BOX_WIDTH}}" for value in values) + f"│{total_sum:^{BOX_WIDTH}}│"

if __name__ == "__main__":
    game = SimpleYamb()
    print(game)
