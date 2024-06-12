import time
import numpy as np
from base_agent import BaseQLearningAgent
from constants import BOX_TYPES
from dice_game_agent import DiceGameQLearningAgent
from simple_yamb import SimpleYamb
from util import dice_combination_map, dice_combination_score_map

class SimpleYambQLearningAgent(BaseQLearningAgent):
    def __init__(self, learning_rate=0.01, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.9999995, exploration_min=0.001):
        super().__init__(f"simple_yamb", SimpleYamb(), 13 + 13,  1 + 1 + 1, learning_rate, discount_factor, exploration_rate, exploration_decay, exploration_min)
        self.agents = [DiceGameQLearningAgent(box=i) for i in range(13)]
        for i in range(13):
            self.agents[i].load_q_table()

    def get_state(self):
        state = tuple([dice_combination_map[self.game.dices]])
        state += tuple([self.game.roll_count])
        #binary mask for available boxes as an integer
        for column in range(len(self.game.sheet)):
            mask = 0
            for box in range(13):
                if self.game.sheet[column][box] == -1:
                    mask += 2**box
        state += tuple([mask])
        print(state)
        return tuple(state)
    
    def get_valid_actions(self):
        valid_actions = []
        for i in range(self.action_size):
            if i < 13:
                if self.game.roll_count < 3:
                    valid_actions.append(i)
            else:
                for column in range(len(self.game.sheet)):
                    for box in range(13):
                        if self.game.sheet[column][box] != -1:
                            valid_actions.append(column * 13 + box)
        return valid_actions

    def calculate_reward(self, action):
        if action < 32:
            return np.mean(self.get_potential_scores())
        elif action < 84:
            action -= 32
            return dice_combination_score_map[(self.game.dices, action)]
        
    def get_potential_scores(self):
        potential_scores = []
        for column in range(len(self.game.sheet)):
            for box in range(13):
                if self.game.sheet[column][box] != -1 and dice_combination_score_map[(self.game.dices, box)] > 0:
                    potential_scores.append(dice_combination_score_map[(self.game.dices, box)])
        return potential_scores
    
    def train(self, num_episodes):
        highest_score = 0
        batch_size = round(num_episodes / 100)
        total_scores = []
        reward_log = []
        exploration_rate_log = []

        for episode in range(num_episodes+1):
            if episode == 0 or episode % batch_size == 0:
                start_time = time.time()
            total_reward = 0
            state = self.get_state()
            reward = 0
            while not self.game.is_completed():
                action = self.choose_action()
                if action < 13:
                    
                    self.game.roll_dice(action)
                elif action < 26:
                    action -= 13
                    self.game.fill_box(action // 13, action % 13)
                else:
                    self.game.announce(self.game,  action - 84)
                
                next_state = self.get_state()
                reward = self.calculate_reward(action)
                self.learn(state, action, reward, next_state, self.game.is_completed())
                state = next_state
                total_reward += reward

            self.update_exploration_rate()
            current_score = self.game.get_score()
            
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
            self.game.reset()

if __name__ == "__main__":
    num_episodes = 20000000
    agent = SimpleYambQLearningAgent()
    print(f"Training agent {agent.name}...")
    agent.train(num_episodes)
    print("Training completed!")
    print("Saving Q-table...")
    agent.save_q_table()
    print("Q-table saved!")
