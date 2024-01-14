import torch
from environment import Environment
from local_agent import Agent
import random
from model import Linear_QNet 
import numpy as np

def test(path_to_model, player:int=0, episodes:int=1000):

    wins_p1 = 0
    losses_p1 = 0
    wins_p2 = 0
    losses_p2 = 0

    agent = Agent()

    pokemons = list(agent.pokemons.keys())

    # escoger dos pokemons al azar
    pokemon1 = random.choice(pokemons)
    pokemon2 = random.choice(pokemons)

    # load model
    model = Linear_QNet(12, 256, 4) 
    model.load_state_dict(torch.load(path_to_model)) 
    
    env = Environment(pokemon1, pokemon2)

    episode = 0

    while True:
            state = agent.get_state(env)
        
            # get action
            state0 = torch.tensor(state, dtype=torch.float)
            final_move = np.zeros((4))
            prediction = model(state0)
            move = torch.argmax(prediction).item()


            # obtener las acciones de los dos jugadores
            if player == 0:
                action_p1 = move
                action_p2 = random.randint(0,3)
            elif player == 1:
                action_p1 = random.randint(0,3)
                action_p2 = move
                
            reward, done, winner = env.step(action_p1, action_p2)

            print(f'episode: {episode}, done: {done}, reward: {reward}, winner: {winner}')

            if done:
                env = Environment(pokemon1, pokemon2)
     
                if winner == 0:
                    wins_p1 += 1
                    losses_p2 += 1
                elif winner == 1:
                    wins_p2 += 1
                    losses_p1 += 1
                elif winner == -1:
                    wins_p1 += 0.5
                    wins_p2 += 0.5

                # cambiar los pokemons
                pokemon1 = random.choice(pokemons)
                pokemon2 = random.choice(pokemons)
                env = Environment(pokemon1, pokemon2)

                episode += 1

            if episode >= episodes:
                break
                
    return wins_p1, losses_p1, wins_p2, losses_p2

if __name__ == '__main__':
    p1_wins, p1_losses, p2_wins, p2_losses = test('model/global_model_p1.pth', player=1, episodes=100000)
    
    print(f'P1 wins: {p1_wins}, P1 losses: {p1_losses} winrate: {p1_wins/(p1_wins+p1_losses)}')
    print(f'P2 wins: {p2_wins}, P2 losses: {p2_losses} winrate: {p2_wins/(p2_wins+p2_losses)}')


