# Authors: Antonio Cabrera, Alejandro Gómez, Alejandro Jiménez, Antonio Perez, Luis Crespo
# Description: El agente se encargará de comunicar el entorno con el modelo de aprendizaje, también se encargará de entrenar al modelo y de realizar las predicciones.

import random
import os
import json
import numpy as np
import torch
from collections import deque
from environment import Environment
from model import Linear_QNet, QTrainer
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, PATH + "/pokemon_game")

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    # devuelve dos diccionarios en los que la clave es el nombre del pokemon/movimiento y el valor es un id
    @classmethod
    def map_data(cls):
        POKEMON_DIR = "data/pokemons/"

        pokemons = []
        moves = []

        for file in os.listdir(POKEMON_DIR):
            if file.endswith(".json"):
                with open(POKEMON_DIR + file) as pokemon_file:  
                    # añadimos el pokemon a la lista de pokemons
                    pokemon_name = file.split(".")[0]
                    pokemons.append(pokemon_name)

                    # añadimos los movimientos del pokemon a la lista de movimientos
                    pokemon = json.load(pokemon_file)
                    pokemon_moves = pokemon["moves"]
                    moves.extend(pokemon_moves)

        # eliminamos los duplicados
        pokemons = list(set(pokemons))
        moves = list(set(moves))
        
        # creamos diccionarios en los que la clave es el nombre del pokemon/movimiento y el valor es un id
        pokemons = {pokemon: i for i, pokemon in enumerate(pokemons)}
        moves = {move: i for i, move in enumerate(moves)}

        return pokemons, moves

    def __init__(self):
        self.numero_partidas = 0
        self.epsilon = 0 # aleatoriedad
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # cola de memoria doble (se puede añadir y quitar por ambos lados)
        self.pokemons, self.moves = Agent.map_data() # diccionarios con los pokemons y los movimientos
        self.model = Linear_QNet(12, 256, 4) # 12 -> tamaño del estado, 256 -> tamaño de la capa oculta, 4 -> numero de movimientos
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    '''
    Funcion que optiene el estado del juego en el que se encuentra el agente:
        [nom_poke_p1, hp_poke_p1, move_1_poke_p1, move_2_poke_p1, move_3_poke_p1, move_4_poke_p1, 
        nom_poke_p2, hp_poke_p2, move_1_poke_p2, move_2_poke_p2, move_3_poke_p2, move_4_poke_p2]
    '''
    def get_state(self, env):

        game = env.battle
        
        state = []
        for player in [game.p1, game.p2]:
            
            pokemon = player.active_pokemon[0]

            state.append(self.pokemons[pokemon.species])
            state.append(pokemon.hp)
                
            for move in pokemon.moves:
                state.append(self.moves[move])

        return np.array(state, dtype = np.int16)

    '''
    Funcion que guarda en la memoria del agente el estado, la accion, la recompensa, el siguiente estado y si el juego ha terminado
    '''
    def remember(self, state, action, reward, next_state, done):    
        pass
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached
    
    '''
    Funcion que entrena al agente cuando a terminado una partida
    '''
    def train_long_memory(self):

        # Cogemos una muestra aleatoria de la memoria (una tupla de 5 elementos)
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        # Descomprimimos la muestra en 5 listas
        states, actions, rewards, next_states, dones = zip(*mini_sample)

        self.trainer.train_step(states, actions, rewards, next_states, dones)

    '''
    Funcion que entrena al agente en cada paso del juego
    '''
    def train_short_memory(self, state, action, reward, next_state, done):
        pass
        self.trainer.train_step(state, action, reward, next_state, done)

    '''
    Funcion que devuelve la accion que el agente va a realizar
    '''
    def get_action(self, state):
        # Epsilon contra la exploracion/exploitacion del agente, cuantas mas partidas lleve menos exploracion y mas exploitacion
        self.epsilon = 80 - self.numero_partidas 
        final_move = -1 

        final_move = np.zeros(4)

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            pass

        return final_move

'''
Funcion con la que entrenamos el modelo de RL
'''
def train(pokemon1:str, pokemon2:str) -> None:
    agent = Agent()
    env = Environment(pokemon1, pokemon2)

    while True:
        # obtener estado antiguo
        state_old = agent.get_state(env)

        # obtener movimiento
        final_move = agent.get_action(state_old)

        enemy_action = random.randint(0, 3)

        # realizar movimiento y obtener nuevo estado     

        # traducir el movimiento [0, 0, 0, 1] -> 3

        reward, done, __  = env.step(np.argmax(final_move), enemy_action)
        state_new = agent.get_state(env)
        
        '''
        print(f"Estado inicial: {state_old} len: {len(state_old)}")
        print(f"Movimiento elegido: {final_move}")
        print(f"Recompensa: {reward}")
        print(f"Estado nuevo: {state_new}")
        '''
        
        # entrenar al agente con el nuevo estado (short memory)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # guardar en la memoria del agente el estado, la accion, la recompensa, el siguiente estado y si el juego ha terminado
        agent.remember(state_old, final_move, reward, state_new, done)
 
        if done:
            # entrenar al agente con todos los estados (long memory), resetear el juego y actualizar el record
            env = Environment(pokemon1, pokemon2)
            agent.numero_partidas += 1
            agent.train_long_memory()
            
            # mostrar resultados
            print('Partida', agent.numero_partidas)

        if agent.numero_partidas == 1000:
            agent.model.save(file_name=f"{pokemon1}-vs-{pokemon2}.pth")
            break 

if __name__ == '__main__':
    train("raichu", "keldeo")
