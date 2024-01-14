import torch
from environment import Environment
from local_agent import Agent
from model import Linear_QNet
import numpy as np
import random, json
import os

PATH = os.path.dirname(os.path.abspath(__file__))
POKEMON_DIR = os.path.join(BASE_DIR, 'data/pokemons/')

def showAction(pokemon):
    pokemon_actual = {}
    with open(POKEMON_DIR + pokemon + '.json') as pokemon_file:
    
        general_pokemon = json.load(pokemon_file)

        moves = general_pokemon['moves']
        ivs = general_pokemon['ivs']
        evs = general_pokemon['evs']
        nature = general_pokemon['nature']

        pokemon_actual['moves'] = moves
        pokemon_actual['ivs'] = ivs
        pokemon_actual['evs'] = evs
        pokemon_actual['nature'] = nature

        for move in pokemon_actual['moves']:
             print(move)

def batalla(path_to_model):

    file = path_to_model.split('/')[-1]

    pokemons = file.split('-vs-')
    pokemon1 = pokemons[0]
    pokemon2 = pokemons[1].split('.')[0]

    # load model
    model = Linear_QNet(12, 256, 4) 
    model.load_state_dict(torch.load(path_to_model))

    agent = Agent()
    env = Environment(pokemon1, pokemon2)
    
    episode = 0

    while True:
        # Combat logic

        state = agent.get_state(env)

        #get action
        state0 = torch.tensor(state, dtype=torch.float)
        final_move = np.zeros((4))
        prediction = model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
        action_p1 = np.argmax(final_move)

        showAction(pokemon2)

        action_p2 = 1

        reward, done, winner = env.step(action_p1, action_p2)
        print(f'Done: {done}, reward: {reward}, winner: {winner}')
        if done:
            env = Environment(pokemon1, pokemon2)
        
            print(f'episode: {episode}, winner: {winner}')
                
            episode += 1
        if episode >= 1:
                break
    return winner 

if __name__ == '__main__':
    showAction('raichu')
    winner= batalla('model/raichu-vs-keldeo.pth')
    