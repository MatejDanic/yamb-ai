import numpy as np
import pickle
from collections import defaultdict
from game import Game
from util import dice_combination_score_map

class QLearningAgent:
    def __init__(self, variant="full", learning_rate=0.01, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.99999, exploration_min=0.01):
        self.variant = variant
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_min = exploration_min
        self.exploration_decay = exploration_decay
        self.q_table = defaultdict(lambda: np.zeros(self.action_size))
        self.initialize_game()

    def initialize_game(self):
        n_columns = 0 if self.variant == "dice_only" else (1 if self.variant == "simple" else 4)
        self.game = Game(n_columns)
        self.action_size = 32 + 13 * n_columns + (13 if n_columns == 4 else 0)
        self.state_size = 1 + 5 + 13 * n_columns + (1 if n_columns == 4 else 0)

    def get_state(self):
        return tuple(tuple([self.game.roll_count]) + self.game.dices)
        #return tuple(tuple([self.game.roll_count]) + tuple(list(self.game.dices)) + [1 if box != -1 else 0 for column in self.game.sheet for box in column] + ([self.game.announcement] if len(self.game.sheet) > 1 else []))
    
    def learn(self, state, action, reward, next_state, done):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action] * (1 - done)
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_error

    def calculate_reward(self, action):
        if action < 32:
            counts = [self.game.dices.count(i) for i in range(1, 7)]
            max_count = np.max(counts)
            reward = max_count if max_count > 1 else 0
            return reward
        elif action < 84: 
            action -= 32
            column = action // 13
            box = action % 13
            if box in [0, 6, 7]:
                ones = self.game.sheet[column][0] if self.game.sheet[column][0] != -1 else 3
                max = self.game.sheet[column][6] if self.game.sheet[column][6] != -1 else 22
                min = self.game.sheet[column][7] if self.game.sheet[column][7] != -1 else 8
                return (max - min) * ones
            return self.game.sheet[column][box]
        else:
            action -= 84
            potential_score = dice_combination_score_map[self.game.dices, action]
            return potential_score


    def choose_action(self):
        valid_actions = self.get_valid_actions()
        if not valid_actions:
            print(agent.game)
            print("No valid actions available, exiting....")
            exit()
        if np.random.rand() < self.exploration_rate:
            return np.random.choice(valid_actions)
        else:
            state = self.get_state()
            q_values = self.q_table[state]
            q_values_valid = [q_values[action] for action in valid_actions]
            return valid_actions[np.argmax(q_values_valid)]
        
    def get_valid_actions(self):
        valid_actions = []
        for action in range(self.action_size):
            if action < 32:
                if self.game.validate_roll_dice():
                    valid_actions.append(action)
            elif action < 84:
                column = (action - 32) // 13
                box = (action - 32) % 13
                if self.game.validate_fill_box(column, box):
                    valid_actions.append(action)
            else:
                box = action - 84
                if self.game.validate_announcement(self.game, box):
                    valid_actions.append(action)
        return valid_actions
    
    def update_exploration_rate(self):
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay


    def save_q_table(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(dict(self.q_table), file)

    def load_q_table(self, filename):
        with open(filename, 'rb') as file:
            self.q_table = defaultdict(lambda: np.zeros(self.action_size), pickle.load(file))

    def __repr__(self):
        lines = [f"Learning rate: {self.learning_rate}",
                 f"Discount facotr: {self.discount_factor}",
                 f"Exploration rate: {self.exploration_rate}",
                 f"Exploration decay: {self.exploration_decay}",
                 f"Exploration min: {self.exploration_min}"]
        return '\n'.join(lines)

if __name__ == "__main__":
    agent = QLearningAgent()
    print(agent)