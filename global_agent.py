# Authors: Antonio Cabrera, Alejandro Gómez, Alejandro Jiménez, Antonio Perez, Luis Crespo
# Description: El agente se encargará de comunicar el entorno con el modelo de aprendizaje, también se encargará de entrenar al modelo y de realizar las predicciones. Este es un agente global, enfocado en luchar con distintos pokemons sin reentrenar.

import random
import os
import json
import numpy as np
import torch
from collections import deque
from environment import Environment
from model import Linear_QNet, QTrainer
import sys
from matplotlib import pyplot as plt
import datetime

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
        self.pokemons, self.moves = Agent.map_data() # diccionarios con los pokemons y los movimientos

        # Modelos de los jugadores
        self.model_p1 = Linear_QNet(12, 256, 4) # 12 -> tamaño del estado, 256 -> tamaño de la capa oculta, 4 -> numero de movimientos
        self.model_p2 = Linear_QNet(12, 256, 4)
        
        # Entrenadores de los jugadores
        self.trainer_p1 = QTrainer(self.model_p1, lr=LR, gamma=self.gamma)
        self.trainer_p2 = QTrainer(self.model_p2, lr=LR, gamma=self.gamma)

        # Memoria de los jugadores
        self.memory_p1 = deque(maxlen=MAX_MEMORY)
        self.memory_p2 = deque(maxlen=MAX_MEMORY)
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
    def remember(self, state, actions, rewards, next_state, done):    
        self.memory_p1.append((state, actions[0], rewards[0], next_state, done))
        self.memory_p2.append((state, actions[1], rewards[1], next_state, done))
    
    '''
    Funcion que entrena al agente cuando a terminado una partida
    '''
    def train_long_memory(self):

        trainers = [self.trainer_p1, self.trainer_p2]
        memories = [self.memory_p1, self.memory_p2]

        for i in range(2):
            trainer = trainers[i]
            memory = memories[i]

            # Cogemos una muestra aleatoria de la memoria (una tupla de 5 elementos)
            if len(memory) > BATCH_SIZE:
                mini_sample = random.sample(memory, BATCH_SIZE)
            else:
                mini_sample = memory

            # Descomprimimos la muestra en 5 listas
            states, actions, rewards, next_states, dones = zip(*mini_sample)
            trainer.train_step(states, actions, rewards, next_states, dones)

    '''
    Funcion que entrena al agente en cada paso del juego
    '''
    def train_short_memory(self, state, actions, rewards, next_state, done):
        self.trainer_p1.train_step(state, actions[0], rewards[0], next_state, done)
        self.trainer_p2.train_step(state, actions[1], rewards[1], next_state, done)

    '''
    Funcion que devuelve la accion que el agente va a realizar
    '''
    def get_action(self, state):
        # Epsilon contra la exploracion/exploitacion del agente, cuantas mas partidas lleve menos exploracion y mas exploitacion
        self.epsilon = 800 - self.numero_partidas 

        # Lista con los movimientos de cada jugador
        player_moves = []
        
        for model in [self.model_p1, self.model_p2]:
            final_move = np.zeros(4)

            if random.randint(0, 200) < self.epsilon:
                move = random.randint(0, 3)
                final_move[move] = 1
            else:
                state0 = torch.tensor(state, dtype=torch.float)
                prediction = model(state0)
                move = torch.argmax(prediction).item()
                final_move[move] = 1
                
            player_moves.append(final_move)

        return player_moves

'''
Funcion con la que entrenamos el modelo de RL. En el agente global funciona cambiando al pokemon oponente cada 100 partidas, así el agente aprenderá a luchar contra cualquier pokémon.
''' 

def train(epochs:int) -> None:
    agent = Agent()

    pokemons = list(agent.pokemons.keys())

    pokemon1 = random.choice(pokemons)
    pokemon2 = random.choice(pokemons)

    env = Environment(pokemon1, pokemon2)
    start_time = datetime.datetime.now()
    
    while True:
        # obtener estado antiguo
        state_old = agent.get_state(env)

        # obtener movimiento
        final_moves = agent.get_action(state_old)

        # traducir el movimiento [0, 0, 0, 1] -> 3
        rewards, done, winner  = env.step(np.argmax(final_moves[0]), np.argmax(final_moves[1]))
        state_new = agent.get_state(env)
        
        print(f"Partida: {agent.numero_partidas} - Recompensas P1: {rewards[0]} - Recompensa P2: {rewards[1]} - Ganador: {winner}")
        
        # entrenar al agente con el nuevo estado (short memory)
        agent.train_short_memory(state=state_old, actions=final_moves, rewards=rewards, next_state=state_new, done=done)

        # guardar en la memoria del agente el estado, la accion, la recompensa, el siguiente estado y si el juego ha terminado
        agent.remember(state_old, final_moves, rewards, state_new, done)
 
        if done:
            # entrenar al agente con todos los estados (long memory), resetear el juego y actualizar el record
            agent.numero_partidas += 1
            agent.train_long_memory()

            # cambiar los pokemons 100 partidas
            if(agent.numero_partidas % 100 == 0):
                pokemon1 = random.choice(pokemons)
                pokemon2 = random.choice(pokemons)
           
            # resetear el juego
            env = Environment(pokemon1, pokemon2)

        if agent.numero_partidas == epochs:
            agent.model_p1.save(file_name="global_model_p1.pth")
            agent.model_p2.save(file_name="global_model_p2.pth")
            break 

    # grafico
    time = np.arange(1, agent.numero_partidas/100 + 1)
    end_time = datetime.datetime.now()
    
    print(f"Tiempo de entrenamiento: {end_time - start_time}")

if __name__ == '__main__':
    train(10000)
