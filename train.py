import tensorflow as tf
import numpy as np
import datetime
import time
from agent import QLearningAgent

num_episodes = 100000
variant = "simple"
agent = QLearningAgent(variant)
highest_score = 0
batch_size = round(num_episodes / 100)
total_scores = []
episode_times = []
reward_log = []
exploration_rate_log = []

log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
summary_writer = tf.summary.create_file_writer(log_dir)
print(f"TensorBoard logs will be written to {log_dir}")

for episode in range(num_episodes+1):
    start_time = time.time()
    total_reward = 0
    state = agent.get_state()
    
    while not agent.game.is_completed():
        action = agent.choose_action()
        if action < 32: 
            agent.game.roll_dice(action)
        elif action < 84:
            action -= 32
            agent.game.fill_box(action // 13, action % 13)
        else:
            agent.game.announce(agent.game,  action - 84)
        
        next_state = agent.get_state()
        reward = agent.calculate_reward(action)
        agent.learn(state, action, reward, next_state, agent.game.is_completed())
        state = next_state
        
        total_reward += reward

    agent.update_exploration_rate()
    end_time = time.time()
    episode_time = end_time - start_time
    episode_times.append(episode_time)

    current_score = agent.calculate_reward(0) if len(agent.game.sheet) == 0 else agent.game.get_total_sum()
    
    highest_score = max(highest_score, current_score)
    if highest_score == current_score:
        print(agent.game)
    total_scores.append(current_score)

    reward_log.append(total_reward)
    exploration_rate_log.append(agent.exploration_rate)

    if episode % batch_size == 0 or episode == num_episodes - 1:
        avg_total_score = np.mean(total_scores[-batch_size:])
        avg_episode_time = np.mean(episode_times[-batch_size:])
        with summary_writer.as_default():
            tf.summary.scalar('Average Total Score', avg_total_score, step=episode)
            tf.summary.scalar('Exploration Rate', agent.exploration_rate, step=episode)
        length = 50
        filled_length = int(length * episode // num_episodes)
        percent = ("{0:.1f}").format(100 * (episode / float(num_episodes)))
        bar = '█' * filled_length + '-' * (length - filled_length)
        remaining_episodes = num_episodes - episode
        estimated_time_left = remaining_episodes * max(0.001666, avg_episode_time)
        eta = time.strftime("%H:%M:%S", time.gmtime(estimated_time_left))
        print(f'\rProgress: |{bar}| {percent}% Complete ({episode}/{num_episodes}) | Highest Score: {highest_score} | Average Score: {avg_total_score:.3f} | ETA: {eta}', end='\r')
        if episode == num_episodes:
            print()  # New line at the end of the progress
    agent.initialize_game()

# load previously saved q table by name and avg total score as wildcard and replace it with current if avg_total_score is larger

print("Saving Q-table...")
agent.save_q_table(f"{variant}_{avg_total_score:.3f}_{agent.learning_rate}_{agent.discount_factor}_{agent.exploration_decay}_{agent.exploration_min}.json")
print("Q-table saved successfully.")