import time
import numpy as np
import tensorflow as tf
from base_agent import BaseQLearningAgent
from constants import BOX_TYPES
from util import dice_combination_score_map
from util import dice_combination_map
from dice_game import DiceGame

class DiceGameQLearningAgent(BaseQLearningAgent):
    def __init__(self, name, game, learning_rate=0.01, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.9999995, exploration_min=0.001, box=0):
        super().__init__(name, game, 32,  1 + (1 if box in [0, 1, 2, 3, 4, 5] else 0), learning_rate, discount_factor, exploration_rate, exploration_decay, exploration_min)
        self.box = box

    def get_state(self):
        state = tuple([dice_combination_map[self.game.dices]])
        if self.box in [0, 1, 2, 3, 4, 5]:
            state += tuple([self.game.roll_count])
        return tuple(state)
    
    def get_valid_actions(self):
        return [i for i in range(32)]

    def calculate_reward(self, action):
        return dice_combination_score_map[self.game.dices, self.box]
    
    def train(self, num_episodes):
        highest_score = 0
        batch_size = round(num_episodes / 100)
        total_scores = []
        batch_times = []
        reward_log = []
        exploration_rate_log = []

        log_dir = f"logs/fit/{self.name}"
        summary_writer = tf.summary.create_file_writer(log_dir)
        print(f"TensorBoard logs will be written to {log_dir}")

        for episode in range(num_episodes+1):
            if episode == 0 or episode+1 % batch_size == 0:
                start_time = time.time()
            total_reward = 0
            state = self.get_state()
            reward = 0
            while not self.game.is_completed():
                action = self.choose_action()
                if action < 32: 
                    self.game.roll_dice(action)
                elif action < 84:
                    action -= 32
                    self.game.fill_box(action // 13, action % 13)
                else:
                    self.game.announce(self.game,  action - 84)
                
                next_state = self.get_state()
                new_reward = self.calculate_reward(action)
                diff = new_reward - reward
                if diff < 0:
                    new_reward = -(reward-new_reward)
                self.learn(state, action, new_reward, next_state, self.game.is_completed())
                reward = new_reward
                state = next_state
                
                total_reward += reward

            self.update_exploration_rate()
            current_score = self.game.get_score()
            
            highest_score = max(highest_score, current_score)
            total_scores.append(current_score)

            reward_log.append(total_reward)
            exploration_rate_log.append(self.exploration_rate)

            if episode % batch_size == 0 or episode == num_episodes - 1:
                batch_time = time.time() - start_time
                avg_total_score = np.mean(total_scores[-batch_size:])
                with summary_writer.as_default():
                    tf.summary.scalar(f"Average Total Score", avg_total_score, step=episode)
                    tf.summary.scalar(f"Exploration Rate", self.exploration_rate, step=episode)
                length = 50
                filled_length = int(length * episode // num_episodes)
                percent = ("{0:.1f}").format(100 * (episode / float(num_episodes)))
                bar = '█' * filled_length + '-' * (length - filled_length)
                remaining_batches = (num_episodes - episode)/batch_size
                estimated_time_left = remaining_batches * batch_time
                eta = time.strftime("%H:%M:%S", time.gmtime(estimated_time_left))
                print(f'\rProgress: |{bar}| {percent}% Complete ({episode}/{num_episodes}) | Highest Score: {highest_score} | Average Score: {avg_total_score:.3f} | ETA: {eta}', end='\r')
                if episode == num_episodes:
                    print()  # New line at the end of the progress
            self.game.reset()

if __name__ == "__main__":
    for box in range(13):
        agent = DiceGameQLearningAgent(name=f"{box}_{BOX_TYPES[box]}", game=DiceGame(box), box=box, learning_rate=0.01, discount_factor=0.99, exploration_decay=0.99999995, exploration_min=0.001)
        print(f"Training agent {agent.name}...")
        agent.train(20000000)
        print("Training completed!")
        print("Saving Q-table...")
        agent.save_q_table()
        print("Q-table saved!")
