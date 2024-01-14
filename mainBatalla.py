import torch
from environment import Environment
from local_agent import Agent
from model import Linear_QNet
import numpy as np
import random, json
import os

POKEMON_DIR = 'data/pokemons/'

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

        i = 1
        print("Movimientos de: "+ pokemon)
        for move in pokemon_actual['moves']:
            print(str(i)+") "+move)
            i += 1

def selectMove(pokemon):
    
    while True:
        showAction(pokemon)
        seleccion = input('¿Qué movimiento deseas realizar?\n')
        seleccion = int(seleccion)
        if(seleccion > 1 or seleccion < 4):
            print("Movimiento: " + str(seleccion))
            return(seleccion - 1)
        else:
            print("Movimiento no válido, elige de nuevo")

def batalla(path_to_model):

    file = path_to_model.split('/')[-1]

    pokemons = file.split('-vs-')
    pokemon1 = pokemons[0]
    pokemon2 = pokemons[1].split('.')[0]

    print("Combate iniciado>\nIA:\t"+pokemon1+"\Tú:\t"+pokemon2)

    # load model
    model = Linear_QNet(12, 256, 4) 
    model.load_state_dict(torch.load(path_to_model))

    agent = Agent()
    env = Environment(pokemon1, pokemon2)

    print("A luchar!!!")
    
    episode = 0
    

    while True:
        # Combat logic
        selectedAction = False
        state = agent.get_state(env)

        #get action
        state0 = torch.tensor(state, dtype=torch.float)
        final_move = np.zeros((4))
        prediction = model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
        action_p1 = np.argmax(final_move)
        action_p2 = selectMove(pokemon2)


        reward, done, winner = env.step(action_p1, action_p2)
        if done:
            env = Environment(pokemon1, pokemon2)
            if winner == 0:
                print(f'winner: {pokemon1}')
            if winner == 1:
                print(f'winner: {pokemon2}')
            break
    return winner 

if __name__ == '__main__':
    winner= batalla('model/raichu-vs-keldeo.pth')
    