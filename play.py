from constants import BOX_TYPES
from dice_game import DiceGame
from dice_game_agent import DiceGameQLearningAgent
from simple_yamb import SimpleYamb
from simple_yamb_agent import SimpleYambQLearningAgent
from util import int_to_binary_array, dice_combination_score_map

# box = 9

# agent = DiceGameQLearningAgent(box=box, exploration_rate=0.0)
# print("Loading Q-table...")
# agent.load_q_table()
# print("Q-table loaded successfully.")

# game = DiceGame()
# print(game)
# while not game.is_completed():
#     input()
#     state = agent.get_state(game)
#     action = agent.choose_action(game)
#     print(f"Rolling for {BOX_TYPES[box]}: {int_to_binary_array(action)}")
#     game.roll_dice(action)
#     print(game)
#     print("Score:", dice_combination_score_map[game.dices, box])


agent = SimpleYambQLearningAgent(exploration_rate=0.0)
print("Loading Q-table...")
agent.load_q_table()
print("Q-table loaded successfully.")

game = SimpleYamb()
print(game.dices)
while not game.is_completed():
    input()
    state = agent.get_state(game)
    action = agent.choose_action(game)
    if action < 13: 
        roll_dice_action = agent.agents[action].choose_action(game)
        print(f"Rolling for {BOX_TYPES[action]}: {int_to_binary_array(roll_dice_action)}")
        game.roll_dice(roll_dice_action)
        print(game.dices)
    else:
        action -= 13
        print(f"Filling box {action % 13}")
        game.fill_box(action // 13, action % 13)
        print(game)
    print(game.get_total_sum())

