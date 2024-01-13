import torch
from environment import Environment
from agent import Agent
import random
from model import Linear_QNet, QTrainer
import numpy as np

def test(path_to_model):

    wins = 0
    losses = 0

    # load model
    model = Linear_QNet(12, 256, 4) 
    model.load_state_dict(torch.load(path_to_model)) 

    TEST_EPISODES = 100
    
    agent = Agent()

    env = Environment(1,1)

    for episode in range(TEST_EPISODES):
         
        state = agent.get_state(env)
    
        # get action
        state0 = torch.tensor(state, dtype=torch.float)
        final_move = np.zeros((4))
        prediction = model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
        action_p1 = np.argmax(final_move)

        action_p2 = random.randint(0,3)

        done, __, winner = env.step(action_p1, action_p2)

        if done:
            env = Environment(1,1)
 
            print(f'episode: {episode}, winner: {winner}')

            if winner == 0:
                wins += 1
            else:
                losses += 1
                
    return wins, losses            


if __name__ == '__main__':
    wins, losses = test('model/model.pth')

    print(f'wins: {wins}, losses: {losses}')
    print(f'win rate: {wins/(wins+losses)}')
        




    
