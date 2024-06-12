from dice_game import DiceGame
from dice_game_agent import DiceGameQLearningAgent

agent = DiceGameQLearningAgent(box=0, exploration_rate=0.0)
print("Loading Q-table...")
agent.load_q_table()
print("Q-table loaded successfully.")

game = DiceGame()
while not game.is_completed():
    state = agent.get_state(game)
    action = agent.choose_action(state)
    print(f"{action:0b}")
    if action < 32: 
        game.roll_dice(action)
    elif action < 84:
        action -= 32
        game.fill_box(action // 13, action % 13)
    else:
        game.announce(action - 84)
    print(game)
    print(agent.get_score(game))

