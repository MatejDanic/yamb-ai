import time, datetime
import tensorflow as tf
import numpy as np
from agent import QLearningAgent
from game import roll_dice, fill_box, announce, is_completed, get_total_sum
from display import render_game, render_stats

num_episodes = 1000000

log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
summary_writer = tf.summary.create_file_writer(log_dir)
print(f"TensorBoard logs will be written to {log_dir}")

highest_score = 0
batch_size = 100
total_scores = []
episode_times = []
reward_log = []
exploration_rate_log = []

agent = QLearningAgent(32 + 13)  # Rolling dice, announcing, filling boxes
#agent = QLearningAgent(32 + 13 + 52)  # Rolling dice, announcing, filling boxes

state = agent.get_state()

print("Training agent...")
for episode in range(num_episodes):
    start_time = time.time()
    total_reward = 0
    while not is_completed(agent.game):
        valid_actions = agent.get_valid_actions(agent.game)
        if not valid_actions:
            print(agent.game)
            print("No valid actions available, exiting....")
            exit()
        action = agent.choose_action(state, valid_actions)
        if action < 32: 
            roll_dice(agent.game, action)
        elif action < 84:
            action -= 32
            fill_box(agent.game, action // 13, action % 13)
        else:
            announce(agent.game,  action - 84)
        
        if agent.game["roll_count"] > 0:
            next_state = agent.get_state()
            reward = agent.calculate_reward(agent.game, action)
            agent.learn(state, action, reward, next_state, is_completed(agent.game))
            state = next_state
            total_reward += reward
    agent.update_exploration_rate()
    end_time = time.time()
    episode_time = end_time - start_time
    episode_times.append(episode_time)
    avg_episode_time = np.mean(episode_times)

    # Track highest score and average total score
    current_score = get_total_sum(agent.game)
    highest_score = max(highest_score, current_score)
    total_scores.append(current_score)
    avg_total_score = np.mean(total_scores)

    # Log metrics to TensorBoard
    reward_log.append(total_reward)
    exploration_rate_log.append(agent.exploration_rate)

    # with summary_writer.as_default():
    with summary_writer.as_default():
        tf.summary.scalar('Average Total Score', avg_total_score, step=episode)
        tf.summary.scalar('Exploration Rate', agent.exploration_rate, step=episode)

    # Print loading bar with statistics
    if episode % batch_size == 0:
        render_stats(episode + 1, num_episodes, highest_score, avg_episode_time)
    agent.reset()


print(f"\nTraining completed.")

# Save the trained Q-table
print("Saving Q-table...")
agent.save_q_table('q_table.json')
print("Q-table saved successfully.")
