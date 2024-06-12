import time
import numpy as np
from base_agent import BaseQLearningAgent
from constants import BOX_TYPES
from util import dice_combination_map, dice_combination_score_map, get_count_of_dice_values_score, get_recurring_values_score, get_consecutive_values_score
from dice_game import DiceGame

class DiceGameQLearningAgent(BaseQLearningAgent):
    def __init__(self, learning_rate=0.075, discount_factor=0.33, exploration_rate=1.0, exploration_decay=0.9999995, exploration_min=0.0001, box=0):
        super().__init__(f"{box}_{BOX_TYPES[box]}", 32, 252 + (2 if box in [0, 1, 2, 3, 4, 5] else 0), learning_rate, discount_factor, exploration_rate, exploration_decay, exploration_min)
        self.box = box

    def get_state(self, game):
        state = tuple([dice_combination_map[game.dices]])
        if self.box in [0, 1, 2, 3, 4, 5]:
            state += tuple([game.roll_count])
        return state
    
    def get_valid_actions(self, state):
        return [i for i in range(32)]

    def calculate_reward(self, previous_dices, current_dices):
        previous_score = self.get_score(previous_dices)
        current_score = self.get_score(current_dices)
        return current_score - previous_score
    
    def get_score(self, dices):
        if self.box in [0, 1, 2, 3, 4, 5]:
            return get_count_of_dice_values_score(dices, self.box)            
        elif self.box == 6:
            return sum(dices)
        elif self.box == 7:
            return 30 - sum(dices)
        elif self.box in [8, 10, 11, 12]:
            return get_recurring_values_score(dices, self.box)
        elif self.box == 9:
            return get_consecutive_values_score(dices, self.box)
        else:
            exit()
    
    def train(self, num_episodes):
        highest_score = 0
        batch_size = round(num_episodes / 100)
        total_scores = []
        reward_log = []
        exploration_rate_log = []

        for episode in range(num_episodes+1):
            game = DiceGame()
            if episode == 0 or episode % batch_size == 0:
                start_time = time.time()
            total_reward = 0
            state = self.get_state(game)
            reward = 0
            while not game.is_completed():
                previous_dices = game.dices
                action = self.choose_action(self.get_state(game))
                if action < 32: 
                    game.roll_dice(action)
                elif action < 84:
                    action -= 32
                    game.fill_box(action // 13, action % 13)
                else:
                    game.announce(action - 84)
                
                next_state = self.get_state(game)
                reward = self.calculate_reward(previous_dices, game.dices)
                self.learn(state, action, reward, next_state, game.is_completed())
                state = next_state
                total_reward += reward

            self.update_exploration_rate()
            current_score = dice_combination_score_map[game.dices, self.box]
            
            highest_score = max(highest_score, current_score)
            total_scores.append(current_score)

            reward_log.append(total_reward)
            exploration_rate_log.append(self.exploration_rate)

            if episode % batch_size == batch_size - 1 or episode == num_episodes:
                batch_time = time.time() - start_time
                avg_total_score = np.mean(total_scores[-batch_size:])
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
                self.average_score = avg_total_score

if __name__ == "__main__":
    num_episodes = 20000000
    for box in range(13):
        agent = DiceGameQLearningAgent(box=box)#learning_rate=0.075, discount_factor=0.8, exploration_decay=0.999995, exploration_min=0.0001, box=box)
        print(f"Training agent {agent.name}...")
        agent.train(num_episodes)
        print("Training completed!")
        print("Saving Q-table...")
        agent.save_q_table()
        print("Q-table saved!")