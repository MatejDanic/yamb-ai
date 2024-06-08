from agent import QLearningAgent

variant = "dice_only"
file_name = "dice_only_2.886_0.3_0.99_0.99999_0.01.json"
agent = QLearningAgent(variant)  # rolling dice, announcing, filling boxes
print("Loading Q-table...")
agent.load_q_table(f"{file_name}")
print("Q-table loaded successfully.")

agent.exploration_rate = 0.0

state = agent.get_state()

action = 31
reward = agent.calculate_reward(action)
print(agent.game)

while not agent.game.is_completed():
    action = agent.choose_action()
    if action < 32: 
        agent.game.roll_dice(action)
    elif action < 84:
        action -= 32
        agent.game.fill_box(action // 13, action % 13)
    else:
        agent.game.announce(agent.game,  action - 84)
    print(f"Action: {action:b}, Reward: {reward}")
    print(agent.game)

