import random
from util import dice_combination_score_map

def initialize_game(full=False):
    return {
            "roll_count": 0,
            "dices": [1, 2, 3, 4, 5],
            "sheet": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
                    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
                    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],
            "announcement": -1,
        } if full else {
            "roll_count": 0,
            "dices": [1, 2, 3, 4, 5],
            "sheet": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]],
            "announcement": -1,
        }

def is_box_availale(game, column, box):
    if game["sheet"][column][box] != -1:
        return False
    elif column == 0 and len(game["sheet"]) > 1:
        return box == 0 or game["sheet"][column][box - 1] != -1
    elif column == 1:
        return box == 12 or game["sheet"][column][box + 1] != -1
    elif column == 3:
        return box == game["announcement"]
    return column == 2 or column == 0 and len(game["sheet"]) == 1

def roll_dice(game, dice_to_roll):
    game["dices"] = tuple(sorted(random.randint(1, 6) if dice_to_roll & (1 << i) else game["dices"][i] for i in range(5)))
    game["roll_count"] += 1
    
def validate_roll_dice(game):
    return game["roll_count"] < 3 and not is_announcement_required(game)

def fill_box(game, column, box):
    game["sheet"][column][box] = dice_combination_score_map[(game["dices"], box)]
    game["roll_count"] = 0
    game["announcement"] = -1
    
def validate_fill_box(game, column, box):
    return game["roll_count"] > 0 and is_box_available(game, column, box)

def announce(game, box):
    game["announcement"] = box

def validate_announcement(game, box):
    return game["announcement"] == -1 and game["roll_count"] == 1 and len(game["sheet"]) == 4 and game["sheet"][3][box] == -1

def is_box_available(game, column, box):
    if game["sheet"][column][box] != -1:
        return False
    elif column == 0:
        return box == 0 or game["sheet"][column][box - 1] != -1
    elif column == 1:
        return box == 12 or game["sheet"][column][box + 1] != -1
    elif column == 3:
        return box == game["announcement"]
    return column == 2

def is_completed(game):
    return all(all(box != -1 for box in column) for column in game["sheet"])
    
def is_announcement_required(game):
    return game["roll_count"] == 1 and game["announcement"] == -1 and are_all_non_anouncement_columns_completed(game)       

def are_all_non_anouncement_columns_completed(game):
    return all(all(box != -1 for box in column) for column in game["sheet"][:-1]) 

def get_total_sum(game):
    return get_top_sum(game) + get_middle_difference(game) + get_bottom_sum(game)

def get_top_sum(game):
    return sum(get_top_sum_column(column) for column in game["sheet"])

def get_top_sum_column(column):
    top_sum = sum(column[:6])
    return top_sum + 30 if top_sum >= 60 else top_sum
    
def get_middle_difference(game):
    return sum(get_middle_difference_column(column) for column in game["sheet"])

def get_middle_difference_column(column):
    return (column[6] - column[7]) * column[0] if column[6] != -1 and column[7] != -1 and column[0] != -1 else 0

def get_bottom_sum(game):
    return sum(get_bottom_sum_column(column) for column in game["sheet"])

def get_bottom_sum_column(column):
    return sum(column[8:])

def get_potential_scores(game):
    potential_scores = []
    for column in range(len(game["sheet"])):
        for box in range(len(column)):
            if is_box_available(game, column, box) or (column == 3 and is_announcement_required(game) and game["sheet"][column][box] == -1):
                if box == 7:  # Min
                    potential_scores.append(30-dice_combination_score_map[(game["dices"], box)])
                else:
                    potential_scores.append(dice_combination_score_map[(game["dices"], box)])
    return potential_scores

if __name__ == "__main__":
    game = initialize_game()
    print(game)
