from abc import abstractmethod
import numpy as np
import pickle
from collections import defaultdict

class BaseQLearningAgent:
    def __init__(self, name, game, action_size, state_size, learning_rate=0.01, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.99999, exploration_min=0.01):
        self.name = f"{name}_{learning_rate}_{discount_factor}_{exploration_rate}_{exploration_decay}_{exploration_min}"
        self.game = game
        self.action_size = action_size
        self.state_size = state_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_min = exploration_min
        self.exploration_decay = exploration_decay
        self.q_table = defaultdict(lambda: np.zeros(self.action_size))

    def choose_action(self):
        valid_actions = self.get_valid_actions()
        if not valid_actions:
            print(self.game)
            print("No valid actions available, exiting....")
            exit()
        if np.random.rand() < self.exploration_rate:
            return np.random.choice(valid_actions)
        else:
            state = self.get_state()
            q_values = self.q_table[state]
            q_values_valid = [q_values[action] for action in valid_actions]
            return valid_actions[np.argmax(q_values_valid)]
    
    def learn(self, state, action, reward, next_state, done):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action] * (1 - done)
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_error
            
    def update_exploration_rate(self):
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay

    def save_q_table(self):
        filename = "q_tables/" + self.name + ".json"
        with open(filename, 'wb') as file:
            pickle.dump(dict(self.q_table), file)

    def load_q_table(self):
        filename = "q_tables/" + self.name + ".json"
        with open(filename, 'rb') as file:
            self.q_table = defaultdict(lambda: np.zeros(self.action_size), pickle.load(file))
    
    def __repr__(self):
        lines = [f"Action size: {self.action_size}",
                f"State size: {self.state_size}",
                f"Learning rate: {self.learning_rate}",
                f"Discount facotr: {self.discount_factor}",
                f"Exploration rate: {self.exploration_rate}",
                f"Exploration decay: {self.exploration_decay}",
                f"Exploration min: {self.exploration_min}"]
        return '\n'.join(lines)
    
    @abstractmethod
    def initialize_game(self):
        pass

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def calculate_reward(self, action):
        pass

    @abstractmethod
    def get_valid_actions(self):
        pass