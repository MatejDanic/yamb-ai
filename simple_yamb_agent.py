import time
import numpy as np
from base_agent import BaseQLearningAgent
from dice_game_agent import DiceGameQLearningAgent
from simple_yamb import SimpleYamb
from util import dice_combination_map, binary_array_to_int

class SimpleYambQLearningAgent(BaseQLearningAgent):
    def __init__(self, learning_rate=0.9, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.9995, exploration_min=0.01):
        super().__init__(f"simple_yamb", 13 + 13, learning_rate, discount_factor, exploration_rate, exploration_decay, exploration_min)
        self.agents = [DiceGameQLearningAgent(box) for box in range(13)]
        for box in range(13):
            self.agents[box].load_q_table()

    def get_state(self, game: SimpleYamb):
        state = tuple([dice_combination_map[game.dices]])
        state += tuple([game.roll_count])
        # add to the state the integer which is a binary representation of the mask of all boxes in the sheet which are not equal to -1
        available_boxes = [1 if box != -1 else 0 for column in game.sheet for box in column]
        state += tuple([binary_array_to_int(available_boxes)])
        return state
    
    def get_valid_actions(self, game: SimpleYamb):
        valid_actions = []
        for i in range(self.action_size):
            if i < 13:
                if game.validate_roll_dice():
                    valid_actions.append(i)
            else:
                for column in range(len(game.sheet)):
                    box = i - 13
                    if game.is_box_available(column, box):
                        valid_actions.append(i)
        return valid_actions

    def calculate_reward(self, game: SimpleYamb, action):
        if action < 13:
            return self.agents[action].get_score(game.dices)
        else:
            action -= 13
            return game.sheet[action // 13][action % 13]
        
    def get_potential_scores(self, game: SimpleYamb):
        potential_scores = []
        for column in range(len(game.sheet)):
            for box in range(13):
                if game.is_box_available(column, box):
                    potential_scores.append(self.agents[box].get_score(game.dices))
        return potential_scores
    
    def train(self, num_episodes):
        highest_score = 0
        batch_size = round(num_episodes / 100)
        total_scores = []
        exploration_rate_log = []

        for episode in range(num_episodes+1):
            game = SimpleYamb()
            if episode == 0 or episode % batch_size == 0:
                start_time = time.time()
            state = self.get_state(game)
            while not game.is_completed():
                action = self.choose_action(game)
                if action < 13:
                    roll_dice_action = self.agents[action].choose_action(game)
                    game.roll_dice(roll_dice_action)
                else:
                    action -= 13
                    game.fill_box(action // 13, action % 13)
                
                next_state = self.get_state(game)
                reward = self.calculate_reward(game, action)
                self.learn(state, action, reward, next_state, game.is_completed())
                state = next_state

            self.update_exploration_rate()
            current_score = game.get_total_sum()
            
            highest_score = max(highest_score, current_score)
            total_scores.append(current_score)

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
                self.average = avg_total_score

if __name__ == "__main__":
    num_episodes = 20000
    highest_average = 0
    for learning_rate in [0.1, 0.25, 0.5, 0.75, 0.9]:
        for discount_factor in [0.1, 0.25, 0.5, 0.75, 0.9]:
            for exploration_rate in [0.995, 0.9995, 0.99995, 0.999995]:
                for exploration_min in [0.1, 0.01, 0.001]:
                    agent = SimpleYambQLearningAgent(learning_rate=learning_rate, discount_factor=discount_factor, exploration_rate=exploration_rate, exploration_min=exploration_min)
                    print(f"Training agent {agent.name} (learning_rate={learning_rate}, discount_factor={discount_factor}, exploration_rate={exploration_rate}, exploration_min={exploration_min})")
                    agent.train(num_episodes)
                    print("Training completed!")
                    if (agent.average > highest_average):
                        print("Saving Q-table...")
                        agent.save_q_table()
                        print("Q-table saved!")
                        highest_average = agent.average
