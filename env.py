import gymnasium as gym
import numpy as np
import torch as th
from stable_baselines3 import PPO
from stable_baselines3.common.distributions import CategoricalDistribution
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.torch_layers import MlpExtractor
from game import initialize_game, is_completed, validate_roll_dice, validate_fill_box, validate_announcement
from util import dice_combination_score_map
from display import render_game

STATE_DIM = 1 + 5 + 13 # roll count, dices, sheet
EXTENDED_STATE_DIM = 1 + 5 + 52 + 1 # roll count, dices, boxes, announcement
NUM_ACTIONS = 32 + 13 # roll dice, fill box
EXTENDED_NUM_ACTIONS = 32 + 52 + 13 # roll dice, fill box, announce

class YahtzeeEnv(gym.Env):
    def __init__(self):
        super(YahtzeeEnv, self).__init__()
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(STATE_DIM,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(NUM_ACTIONS)
    
    def reset(self):
        self.game = initialize_game()
        self.state = self._get_state()
        return self.state
    
    def step(self, action):
        self._apply_action(action)
        reward = self._calculate_reward(action)
        done = is_completed(self.game)
        return self.state, reward, done, {}
    
    def _get_state(self):
        return [self.game["roll_count"]] + list(self.game["dices"]) + [box for column in self.game["sheet"] for box in column] + [self.game["announcement"]] if len(self.game["sheet"]) > 1 else []
    
    def _apply_action(self, action):
        if action < 32: 
            self.game.roll_dice(action)
        elif action < 84:
            action -= 32
            self.game.fill_box(action // 13, action % 13)
        else:
            self.game.announce(action - 84)

    def get_valid_actions(self):
        if self.state[0] == 0:
            return [31]
        valid_actions = []
        for action in range(self.action_space.n):
            if action < 32 and validate_roll_dice(self.game):
                valid_actions.append(action)
            elif action < 84:
                column = (action - 32) // 13
                box = (action - 32) % 13
                if validate_fill_box(self.game, column, box):
                    valid_actions.append(action)
            else:
                box = action - 84
                if validate_announcement(self.game, box):
                    valid_actions.append(action)
        return valid_actions
    
    def _calculate_reward(self, action):
        if action < 32:
            dice_counts = np.bincount(self.game["dices"], minlength=7)[1:]
            same_value_bonus = np.max(dice_counts)
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
            score = dice_combination_score_map[self.game["dices"], box]
            if box == 7:
                score = 30 - score
            return score
        else:
            potential_score = dice_combination_score_map[self.game["dices"], (action-84)]
            return potential_score
    
    def _check_done(self):
        return is_completed(self.game)
    
    def render(self):
        if len(self.game["sheet"]) > 1:
            render_game(self.game)

class CustomMaskedPolicy(ActorCriticPolicy):
    def __init__(self, observation_space, action_space, lr_schedule, env=None, **kwargs):
        super(CustomMaskedPolicy, self).__init__(observation_space, action_space, lr_schedule, **kwargs)
        self.action_dist = CategoricalDistribution(action_space.n)
        self.env = env

    def forward(self, obs, deterministic=False):
        features = self.extract_features(obs)
        distribution = self._get_action_dist_from_latent(features)
        if deterministic:
            actions = distribution.mode()
        else:
            actions = distribution.sample()
        valid_actions = self.env.get_valid_actions()
        mask = th.zeros_like(actions, dtype=th.bool)
        mask[valid_actions] = True
        actions = actions[mask]
        return actions, features

    def _get_action_dist_from_latent(self, latent_pi):
        logits = self.action_net(latent_pi)
        valid_actions = self.env.get_valid_actions()
        if not valid_actions:
            self.env.render()
            print("No valid actions available, exiting....")
            exit()
        mask = th.zeros_like(logits, dtype=th.bool)
        mask[:, valid_actions] = True
        logits = logits.masked_fill(~mask, float('-inf'))
        return self.action_dist.proba_distribution(action_logits=logits)

    def evaluate_actions(self, obs, actions):
        features = self.extract_features(obs)
        distribution = self._get_action_dist_from_latent(features)
        log_prob = distribution.log_prob(actions)
        entropy = distribution.entropy()
        values = self.value_net(features)
        return values, log_prob, entropy

# Custom policy factory
def make_custom_masked_policy(observation_space, action_space, lr_schedule, env=None, **kwargs):
    return CustomMaskedPolicy(observation_space.shape[0], action_space, lr_schedule, env=env, **kwargs)

# Initialize the environment
env = YahtzeeEnv()
policy_kwargs = dict(
    features_extractor_class=MlpExtractor,
    features_extractor_kwargs=dict(
        net_arch=dict(pi=[64, 64], vf=[64, 64]),
        activation_fn=th.nn.ReLU,
        features_dim=sum(net_arch['pi'])
    ),
    env=env
)

# Initialize the PPO model with the custom policy factory and environment
model = PPO(
    policy=make_custom_masked_policy,
    env=env,
    policy_kwargs=policy_kwargs,
    verbose=1
)

model.learn(total_timesteps=100000)

# Expand state representation and action space for full game strategy
env.observation_space = gym.spaces.Box(low=0, high=1, shape=(EXTENDED_STATE_DIM,), dtype=np.float32)
env.action_space = gym.spaces.Discrete(EXTENDED_NUM_ACTIONS)

# Retrain the model on the extended state and action space
model.learn(total_timesteps=500000)

# Save the model
model.save("yahtzee_full_model")

# Evaluate the model
obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
