# Authors: Antonio Cabrera, Alejandro Gómez, Alejandro Jiménez, Antonio Perez, Luis Crespo
# Description: El agente se encargará de comunicar el entorno con el modelo de aprendizaje, también se encargará de entrenar al modelo y de realizar las predicciones.

import random
import numpy as np
from collections import deque

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.numero_partidas = 0
        self.epsilon = 0 # aleatoriedad
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # cola de memoria doble (se puede añadir y quitar por ambos lados)
        #TODO: Model
        #TODO: Trainer

    '''
    Funcion que optiene el estado del juego en el que se encuentra el agente
    '''
    def get_state(self, game):
        pass
        #TODO: return np.array(state, dtype=int)

    '''
    Funcion que guarda en la memoria del agente el estado, la accion, la recompensa, el siguiente estado y si el juego ha terminado
    '''
    def remember(self, state, action, reward, next_state, done):    
        pass
        #TODO: self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached
    
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

        #TODO: self.trainer.train_step(states, actions, rewards, next_states, dones)

    '''
    Funcion que entrena al agente en cada paso del juego
    '''
    def train_short_memory(self, state, action, reward, next_state, done):
        pass
        #TODO: self.trainer.train_step(state, action, reward, next_state, done)
    

    '''
    Funcion que devuelve la accion que el agente va a realizar
    '''
    def get_action(self, state):
        # Epsilon contra la exploracion/exploitacion del agente, cuantas mas partidas lleve menos exploracion y mas exploitacion
        self.epsilon = 80 - self.numero_partidas 
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            '''TODO:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1'''

        return final_move

'''
Funcion con la que entrenamos el modelo de RL
'''
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    agent = Agent()
    #TODO: game = Game()

    while True:
        pass

        '''TODO:
        # obtener estado antiguo
        state_old = agent.get_state(game)

        # obtener movimiento
        final_move = agent.get_action(state_old)

        # realizar movimiento y obtener nuevo estado     
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # entrenar al agente con el nuevo estado (short memory)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # guardar en la memoria del agente el estado, la accion, la recompensa, el siguiente estado y si el juego ha terminado
        agent.remember(state_old, final_move, reward, state_new, done)

        
        if done:
            # entrenar al agente con todos los estados (long memory), resetear el juego y actualizar el record
            game.reset()
            agent.numero_partidas += 1
            agent.train_long_memory()
            
            # mostrar resultados
            print('Partida', agent.numero_partidas, 'Puntuacion', score)
            
            # mostramos una grafica de la puntuacion
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.numero_partidas
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
        '''
if __name__ == '__main__':
    train()
