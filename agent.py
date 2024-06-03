import numpy as np
import json
from collections import defaultdict

class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.995, exploration_min=0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay     
        self.exploration_min = exploration_min
        self.q_table = defaultdict(lambda: np.zeros(action_size))
    
    def get_state(self, game):
        simplified_state = game.to_simplified()
        dice_values = tuple(simplified_state['dices'].values())
        sheet_values = tuple(tuple(box for box in column.values()) for column in simplified_state['sheet'].values())
        roll_count = simplified_state['roll_count']
        announcement = simplified_state['announcement']
        return (dice_values, sheet_values, roll_count, announcement)
    
    def choose_action(self, state, valid_actions):
        if np.random.rand() <= self.exploration_rate:
            return np.random.choice(valid_actions)
        state_key = str(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        q_values = self.q_table[state_key]
        return valid_actions[np.argmax([q_values[a] for a in valid_actions])]
    
    def learn(self, state, action, reward, next_state):
        state_key = str(state)
        next_state_key = str(next_state)
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)
        q_update = reward + self.discount_factor * np.max(self.q_table[next_state_key])
        self.q_table[state_key][action] = (1 - self.learning_rate) * self.q_table[state_key][action] + self.learning_rate * q_update
    
    def update_exploration_rate(self):
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay

    def get_valid_actions(self, game):
        if game.roll_count == 0:
            return [31]
        valid_actions = []
        for action in range(self.action_size):
            action_type, action_details = self.map_action_to_game(action)
            if action_type == 'roll_dice' and game.validate_roll_dice():
                valid_actions.append(action)
            elif action_type == 'fill_box' and game.validate_fill_box(*action_details):
                valid_actions.append(action)
            elif action_type == 'announce' and game.validate_announce(action_details):
                valid_actions.append(action)
        return valid_actions
    
    def save_q_table(self, filename):
        serializable_q_table = {k: v.tolist() for k, v in self.q_table.items()}
        with open(filename, 'w') as f:
            json.dump(serializable_q_table, f)

    def load_q_table(self, filename):
        with open(filename, 'r') as f:
            serializable_q_table = json.load(f)
        self.q_table = {k: np.array(v) for k, v in serializable_q_table.items()}

    def map_action_to_game(self, action):
        if action < 32:  # Rolling dice
            dice_to_roll = [i for i in range(5) if action & (1 << i)]
            return 'roll_dice', dice_to_roll
        elif action < 84:  # Filling box
            action -= 32
            column = action // 13
            box = action % 13
            return 'fill_box', (column, box)
        else:  # Announcements
            action -= 84
            announcement = action
            return 'announce', announcement
