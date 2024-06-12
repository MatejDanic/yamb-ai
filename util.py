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

def get_count_of_dice_values_score(dices, box):
    count = dices.count(box + 1)
    score = count ** 2
    if count >= 3:
        score += 6
    return score
    
def get_recurring_values_score(dices, box):
    max_recurring = max(dices, key=dices.count)
    score = sum([dice for dice in dices if dice == max_recurring]) if max_recurring > 1 else 0
    if dice_combination_score_map[dices, box] > 0:
        score = dice_combination_score_map[dices, box]
    return score

def get_consecutive_values_score(dices, box):
    consecutive_count = 1
    max_consecutive_count = 1
    for i in range(1, len(dices)):
        if dices[i] == dices[i-1] + 1:
            consecutive_count += 1
            max_consecutive_count = max(max_consecutive_count, consecutive_count)
        else:
            consecutive_count = 1
        score = max_consecutive_count
    if dice_combination_score_map[dices, box] > 0:
        score = dice_combination_score_map[dices, box]
    return score

print("Calculating all possible dice combinations of dice and their category scores...")

dice_combinations = list(combinations_with_replacement(range(1, 7), 5))
dice_combination_map = {combination: i for i, combination in enumerate(dice_combinations)}

dice_combination_score_map = {}
for combination in list(combinations_with_replacement(range(1, 7), 5)):
    for box in range(13):
        dice_combination_score_map[(combination, box)] = calculate_score(combination, box)

print(f"{len(dice_combinations)} unique dice combinations found.")
