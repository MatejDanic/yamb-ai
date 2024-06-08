import numpy as np
import tensorflow as tf
import random
import datetime

# Exclude action 0 from allowed rolls
ALLOWED_ROLLS = [i for i in range(1, 32)]

log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
summary_writer = tf.summary.create_file_writer(log_dir)
print(f"TensorBoard logs will be written to {log_dir}")

class DiceRollingAgent:
    def __init__(self, n_actions, alpha=0.1, gamma=0.99, epsilon=0.1):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.n_actions = n_actions

    def get_state_key(self, state):
        return str(state)

    def choose_action(self, state):
        state_key = self.get_state_key(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.n_actions)
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(ALLOWED_ROLLS)
        else:
            valid_actions = self.q_table[state_key][1:]  # Exclude the 0th action
            return np.argmax(valid_actions) + 1  # Offset by 1 to match ALLOWED_ROLLS

    def update_q_table(self, state, action, reward, next_state):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.n_actions)

        old_value = self.q_table[state_key][action]
        next_max = np.max(self.q_table[next_state_key])

        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state_key][action] = new_value

class DiceRollingGame:
    def __init__(self):
        self.dice = [0] * 5

    def roll_dice(self, dice_mask=31):
        self.dice = tuple([random.randint(1, 6) if (dice_mask >> i) & 1 else self.dice[i] for i in range(5)])
        return self.dice

    def calculate_reward(self):
        counts = [self.dice.count(i) for i in range(1, 7)]
        return max(counts)

def train_dice_rolling_agent(n_episodes=1000000):
    agent = DiceRollingAgent(n_actions=len(ALLOWED_ROLLS) + 1)  # +1 for the zero-based indexing
    game = DiceRollingGame()

    total_reward_log = []

    for episode in range(n_episodes):
        game.roll_dice()
        total_reward = 0
        for round_num in range(3):
            state = game.dice
            action = agent.choose_action(state)
            next_state = game.roll_dice(action)
            reward = game.calculate_reward()
            agent.update_q_table(state, action, reward, next_state)
            total_reward += reward
        print(f"Episode {episode+1}/{n_episodes}", end="\r")

        total_reward_log.append(total_reward)
        if episode % 1000 == 0:
            with summary_writer.as_default():
                tf.summary.scalar('Reward', np.mean(total_reward_log[-1000:]), step=episode)

    return agent

if __name__ == "__main__":
    trained_dice_agent = train_dice_rolling_agent()
    for _ in range(10):
        game = DiceRollingGame()
        game.roll_dice()
        print("---------------------")
        print(game.dice)
        for round_num in range(3):
            state = game.dice
            action = trained_dice_agent.choose_action(state)
            print(f"{action:05b}")
            next_state = game.roll_dice(action)
            reward = game.calculate_reward()
            print(next_state, reward)
