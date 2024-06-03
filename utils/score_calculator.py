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

def calculate_sum(dice_values, box=None):
    if box is None:
        return sum(dice_values)
    return sum(value for value in dice_values if value == (box + 1))

def calculate_trips(dice_values):
    sum_value = calculate_recurring_value_sum(dice_values, 3)
    if sum_value > 0:
        sum_value += BONUS_TRIPS
    return sum_value

def calculate_straight(dice_values):
    found_values = [False] * 6
    for value in dice_values:
        found_values[value - 1] = True
    if all(found_values[:5]):
        return BONUS_STRAIGHT_SMALL
    elif all(found_values[1:]):
        return BONUS_STRAIGHT_LARGE
    return 0

def calculate_boat(dice_values):
    trips_sum = calculate_recurring_value_sum(dice_values, 3)
    if trips_sum > 0:
        remaining_dice_values = [value for value in dice_values if value != trips_sum // 3]
        pair_sum = calculate_recurring_value_sum(remaining_dice_values, 2)
        if pair_sum > 0:
            return pair_sum + trips_sum + BONUS_BOAT
    return 0

def calculate_carriage(dice_values):
    sum_value = calculate_recurring_value_sum(dice_values, 4)
    if sum_value > 0:
        sum_value += BONUS_CARRIAGE
    return sum_value

def calculate_yamb(dice_values):
    sum_value = calculate_recurring_value_sum(dice_values, 5)
    if sum_value > 0:
        sum_value += BONUS_YAMB
    return sum_value

def calculate_recurring_value_sum(dice_values, threshold):
    for i in range(1, 7):
        count = dice_values.count(i)
        if count >= threshold:
            return i * threshold
    return 0