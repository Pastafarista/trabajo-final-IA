import torch
from environment import Environment
from global_agent import Agent
from model import Linear_QNet
import numpy as np
import random, json
import time

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
            print("\t"+str(i)+") "+move)
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

def selectNewPokemon(pokemons):
    i = 1
    for name in pokemons:
        print(str(i)+") "+name)
        i += 1

    while True:
        seleccion = int(input('Elige el pokemon que quieres utilizar:\n'))
        if(seleccion > 1 or seleccion < i):
            print("Pokemon elegido: " + pokemons[seleccion-1])
            return(pokemons[seleccion - 1])
        else:
            print("Pokemon no válido, elige de nuevo")
    

def batalla(path_to_model):

    agent = Agent()
    pokemons = list(agent.pokemons.keys())

    pokemon1 = random.choice(pokemons)
    pokemon2 = selectNewPokemon(pokemons)
    print("Combate iniciado>\nIA:\t"+pokemon1+"|Tú:\t"+pokemon2)

    # load model
    model = Linear_QNet(12, 256, 4) 
    model.load_state_dict(torch.load(path_to_model))

    env = Environment(pokemon1, pokemon2)

    print("============\nA luchar!!!\n============")
    
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
        action_p2 = selectMove(pokemon2)


        reward, done, winner = env.step(action_p1, action_p2)
        if done:
            if winner == 0:  #Gana la IA
                print(f'winner: {pokemon1}')
            if winner == 1: #Gana el jugador
                print(f'winner: {pokemon2}')

            time.sleep(5)

            pokemon1 = random.choice(pokemons)
            pokemon2 = selectNewPokemon(pokemons)
            env = Environment(pokemon1, pokemon2)
            print("============\nA luchar!!!\n============")
        if episode > 1:
            break
    return winner 

if __name__ == '__main__':
    winner= batalla('model/global_model_p1.pth')
    