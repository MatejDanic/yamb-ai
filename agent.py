import numpy as np
import pickle
from collections import defaultdict
from game import initialize_game, validate_roll_dice, validate_fill_box, validate_announcement, is_box_available, get_potential_scores
from util import dice_combination_score_map

class QLearningAgent:
    def __init__(self, action_size, learning_rate=0.005, discount_factor=0.98, exploration_rate=1.0, exploration_decay=0.99998, exploration_min=0.05):
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_min = exploration_min
        self.exploration_decay = exploration_decay
        self.q_table = defaultdict(lambda: np.zeros(action_size))
        self.game = initialize_game()

    def reset(self):
        self.game = initialize_game()

    def get_state(self):
        return tuple([self.game["roll_count"]] + list(self.game["dices"]) + [1 if box != -1 else 0 for column in self.game["sheet"] for box in column ] + ([self.game["announcement"]] if len(self.game["sheet"]) > 1 else []))
    
    def learn(self, state, action, reward, next_state, done=0):        
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action] * (1 - done)
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_error  
    
    def calculate_reward(self, game, action):
        if action < 32:
            # Count occurrences of each dice value
            dice_counts = np.bincount(game["dices"], minlength=7)[1:]
            # Favor rolling multiple dice of the same value
            same_value_bonus = np.max(dice_counts)
            
            # Check for consecutive sequences for straights
            consecutive_bonus = 0
            if 1 in dice_counts and 2 in dice_counts and 3 in dice_counts and 4 in dice_counts:
                consecutive_bonus = 1
            if 2 in dice_counts and 3 in dice_counts and 4 in dice_counts and 5 in dice_counts:
                consecutive_bonus = 1
            if 3 in dice_counts and 4 in dice_counts and 5 in dice_counts and 6 in dice_counts:
                consecutive_bonus = 1
            if 1 in dice_counts and 2 in dice_counts and 3 in dice_counts and 4 in dice_counts and 5 in dice_counts:
                consecutive_bonus = 2
            if 2 in dice_counts and 3 in dice_counts and 4 in dice_counts and 5 in dice_counts and 6 in dice_counts:
                consecutive_bonus = 2
            
            return (same_value_bonus + consecutive_bonus) * 10
        elif action < 84: 
            box = (action - 32) % 13
            score = dice_combination_score_map[game["dices"], box]
            if box == 7:
                score = 30 - score
            elif score == 0:
                score -= 20
            return score
        else:
            # Potential score from the announced box based on current dice values
            potential_score = dice_combination_score_map[game["dices"], (action-84)]
            return potential_score


    def choose_action(self, state, valid_actions):
        if np.random.rand() < self.exploration_rate:
            return np.random.choice(valid_actions)
        else:
            return valid_actions[np.argmax(self.q_table[state][action] for action in valid_actions)]
        
    def get_valid_actions(self, game):
        if game["roll_count"] == 0:
            return [31]
        valid_actions = []
        for action in range(self.action_size):
            if action == 0:
                continue
            if action < 32:
                if validate_roll_dice(game):
                    valid_actions.append(action)
            elif action < 84:
                column = (action - 32) // 13
                box = (action - 32) % 13
                if validate_fill_box(game, column, box):
                    valid_actions.append(action)
            else:
                box = action - 84
                if validate_announcement(game, box):
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

if __name__ == "__main__":
    agent = QLearningAgent(32 + 13 + 52)
    game = initialize_game()
    print(game)
    print(agent.get_state())