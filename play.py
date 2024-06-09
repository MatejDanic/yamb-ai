from constants import BOX_TYPES
from dice_game_agent import DiceGameQLearningAgent

box = 0
agent = DiceGameQLearningAgent(box)
print("Loading Q-table...")
agent.load_q_table(f"{BOX_TYPES[box]}.json")
print("Q-table loaded successfully.")

agent.exploration_rate = 0.0
state = agent.get_state()

action = 31
print(agent.game)
print(agent.game.get_score())
while not agent.game.is_completed():
    action = agent.choose_action()
    print(f"{action:0b}")
    if action < 32: 
        agent.game.roll_dice(action)
    elif action < 84:
        action -= 32
        agent.game.fill_box(action // 13, action % 13)
    else:
        agent.game.announce(agent.game,  action - 84)
    print(agent.game)
    print(agent.game.get_score())

