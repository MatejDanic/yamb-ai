import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import datetime
from yamb.game import Game
from agent import QLearningAgent

# Suppress TensorFlow INFO and WARNING messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Define the state size based on the maximum possible unique states
dice_state_size = 6 ** 5  # 6 possible values for each of the 5 dice
sheet_state_size = 2 ** (4 * 13)  # Each box can be filled or empty in 4 columns and 13 boxes
roll_count_size = 4  # Roll count can be 0, 1, 2, or 3
announcement_size = 14  # 13 possible announcements plus 1 for None

state_size = dice_state_size * sheet_state_size * roll_count_size * announcement_size
action_size = 1 + 13 + 52  # Rolling dice, announcing, filling boxes

agent = QLearningAgent(state_size, action_size)

# Parameters for tracking progress
num_episodes = 10
reward_log = []
avg_reward_log = []
exploration_rate_log = []
reward_window = 100  # Size of the window for calculating the average reward

def calculate_potential_reward(game):
    potential_scores = game.calculate_potential_scores()
    return max(potential_scores)

def calculate_reward(game):
    return game.get_potential_score()

# Create a summary writer for TensorBoard
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
summary_writer = tf.summary.create_file_writer(log_dir)
print(f"TensorBoard logs will be written to {log_dir}")

# Training loop with TensorBoard logging
for episode in range(num_episodes):
    print(f"Starting episode {episode}")
    game = Game()
    state = agent.get_state(game)
    total_reward = 0
    
    while not game.is_completed():
        valid_actions = agent.get_valid_actions(game)
        if not valid_actions:
            print("No valid actions available, breaking out of the loop.")
            break
        action = agent.choose_action(state, valid_actions)
        action_type, action_details = agent.map_action_to_game(action)
        if action_type == 'roll_dice':
            game.roll_dice(action_details)
        elif action_type == 'fill_box':
            game.fill_box(*action_details)
        elif action_type == 'announce':
            game.announce(action_details)
        
        next_state = agent.get_state(game)
        reward = calculate_reward(game)
        agent.learn(state, action, reward, next_state)
        state = next_state
        
        total_reward += reward
    
    print(f"Finished episode {episode} with total reward {total_reward}")
    reward_log.append(total_reward)
    exploration_rate_log.append(agent.exploration_rate)
    agent.update_exploration_rate()
    
    # Calculate the average reward over the last `reward_window` episodes
    if len(reward_log) >= reward_window:
        avg_reward = np.mean(reward_log[-reward_window:])
        avg_reward_log.append(avg_reward)
    else:
        avg_reward_log.append(np.mean(reward_log))

    # Log metrics to TensorBoard
    with summary_writer.as_default():
        tf.summary.scalar('Total Reward', total_reward, step=episode)
        tf.summary.scalar('Average Reward', avg_reward_log[-1], step=episode)
        tf.summary.scalar('Exploration Rate', agent.exploration_rate, step=episode)

    # Ensure logs are written to disk
    summary_writer.flush()

print(f"Training completed. Logs written to {log_dir}")

# Save the trained Q-table
agent.save_q_table('q_table.json')
