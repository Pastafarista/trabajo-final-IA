import torch
from environment import Environment
from agent import Agent
import random
from model import Linear_QNet, QTrainer
import numpy as np

def test(path_to_model, player:int=0, episodes:int=1000):
    wins = 0
    losses = 0

    file = path_to_model.split('/')[-1]

    pokemons = file.split('-vs-')
    pokemon1 = pokemons[0]
    pokemon2 = pokemons[1].split('.')[0].replace('[', '').replace(']', '')

    # load model
    model = Linear_QNet(12, 256, 4) 
    model.load_state_dict(torch.load(path_to_model)) 
    
    agent = Agent()

    env = Environment(pokemon1, pokemon2)

    episode = 0

    while True:
            state = agent.get_state(env)
        
            # get action
            state0 = torch.tensor(state, dtype=torch.float)
            final_move = np.zeros((4))
            prediction = model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

            # obtener las acciones de los dos jugadores
            if player == 0:
                action_p1 = np.argmax(final_move)
                action_p2 = random.randint(0,3)
            elif player == 1:
                action_p1 = random.randint(0,3)
                action_p2 = np.argmax(final_move)
                
            reward, done, winner = env.step(action_p1, action_p2)

            print(f'episode: {episode}, done: {done}, reward: {reward}, winner: {winner}')

            if done:
                env = Environment(pokemon1, pokemon2)
     
                print(f'episode: {episode}, winner: {winner}')

                if winner == 0:
                    wins += 1
                elif winner == 1:
                    losses += 1
                else:
                    wins += 0.5
                    losses += 0.5

                episode += 1

            if episode >= episodes:
                break
                
    return wins, losses            


if __name__ == '__main__':
    p1_wins, p1_losses = test('model/raichu-vs-[raichu].pth', player=1, episodes=1000) # P1: random bot 1, P2: model
    p2_wins, p2_losses = p1_losses, p1_wins
    
    print(f'P1 wins: {p1_wins}, P1 losses: {p1_losses} winrate: {p1_wins/(p1_wins+p1_losses)}')
    print(f'P2 wins: {p2_wins}, P2 losses: {p2_losses} winrate: {p2_wins/(p2_wins+p2_losses)}')
