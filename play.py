import json
from game import initialize_game, roll_dice, fill_box, announce, is_completed, get_total_sum
from agent import QLearningAgent
from display import render_game

# Load the trained Q-table
agent = QLearningAgent(32 + 13)  # rolling dice, announcing, filling boxes
print("Loading Q-table...")
agent.load_q_table('q_table.json')
print("Q-table loaded successfully.")

# Set exploration rate to 0 to ensure the agent always exploits the learned policy
agent.exploration_rate = 0.0

# Initialize the game
state = agent.get_state()

while not is_completed(agent.game):
    valid_actions = agent.get_valid_actions(agent.game)
    action = agent.choose_action(state, valid_actions)
    if action < 32:
            roll_dice(agent.game, action)
    elif action < 84:
        action -= 32
        fill_box(agent.game, action // 13, action % 13)
    else:
        announce(agent.game,  action - 84)

    next_state = agent.get_state()
    state = next_state

# Display the final state of the game
render_game(agent.game)