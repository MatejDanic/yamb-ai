from itertools import combinations_with_replacement

BONUS_TRIPS = 10
BONUS_STRAIGHT_SMALL = 35
BONUS_STRAIGHT_LARGE = 45
BONUS_BOAT = 30
BONUS_CARRIAGE = 40
BONUS_YAMB = 50

def calculate_score(dices, box):
    if box in [0, 1, 2, 3, 4, 5]:
        return calculate_sum(dices, box)
    elif box in [6, 7]:
        return calculate_sum(dices)
    elif box == 8:
        return calculate_trips(dices)
    elif box == 9:
        return calculate_straight(dices)
    elif box == 10:
        return calculate_boat(dices)
    elif box == 11:
        return calculate_carriage(dices)
    elif box == 12:
        return calculate_yamb(dices)
    else:
        return 0

def calculate_sum(dices, box=None):
    if box is None:
        return sum(dices)
    return sum(dice for dice in dices if dice == (box + 1))

def calculate_trips(dices):
    sum_value = calculate_recurring_value_sum(dices, 3)
    return (sum_value + BONUS_TRIPS) if sum_value > 0 else 0

def calculate_straight(dices):
    dice_set = set(dices)
    if dice_set == {1, 2, 3, 4, 5}:
        return BONUS_STRAIGHT_SMALL
    elif dice_set == {2, 3, 4, 5, 6}:
        return BONUS_STRAIGHT_LARGE
    return 0

def calculate_boat(dices):
    recurring_values = [value for value in set(dices) if dices.count(value) in [2, 3]]
    if len(recurring_values) == 2:
        return sum(dices) + BONUS_BOAT
    return 0

def calculate_carriage(dices):
    sum_value = calculate_recurring_value_sum(dices, 4)
    return (sum_value + BONUS_CARRIAGE) if sum_value > 0 else 0

def calculate_yamb(dices):
    sum_value = calculate_recurring_value_sum(dices, 5)
    return (sum_value + BONUS_YAMB) if sum_value > 0 else 0

def calculate_recurring_value_sum(dices, threshold):
    recurring_values = [value for value in set(dices) if dices.count(value) >= threshold]
    if recurring_values:
        return recurring_values[0] * threshold
    return 0

print("Calculating scores for all possible dice combinations and boxes...")

dice_combinations = list(combinations_with_replacement(range(1, 7), 5))
dice_combination_map = {combination: i for i, combination in enumerate(dice_combinations)}

dice_combination_score_map = {}
for combination in list(combinations_with_replacement(range(1, 7), 5)):
    for box in range(13):
        dice_combination_score_map[(combination, box)] = calculate_score(combination, box)

if __name__ == "__main__":
    print("Dice combination score map:")
    for combination, score in dice_combination_score_map.items():
        print(f"{combination} -> {score}")  