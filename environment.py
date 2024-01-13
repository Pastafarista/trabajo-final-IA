# Authors: Antonio Cabrera, Alejandro Gómez, Alejandro Jiménez, Antonio Perez, Luis Crespo
# Description: El fichero contiene la clase Environment, que representa el entorno en el que se desarrolla el juego.

import os
import json
import sys
import numpy as np

# añadimos el directorio pokemon_game al path para poder importar los modulos
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, PATH + "/pokemon_game")

import pokemon_game.simulator as sim
from pokemon_game.select_pokemon import create_team

# clase que representa el entorno en el que se desarrolla el juego
class Environment():

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

    def __init__(self, pokemon_p1:str, pokemon_p2:str):
        # cargamos los datos de los pokemons y los movimientos
        self.pokemons, self.moves = Environment.map_data()
        teams = Environment.get_teams()
       
        # creamos los equipos de un solo pokemon (el código estaba pensado para equipos de más de un pokemon)
        team_p1 = create_team([pokemon_p1])
        team_p2 = create_team([pokemon_p2])

        # instanciamos la batalla
        self.battle =  sim.Battle('single', 'equipo_1', team_p1, 'equipo_2', team_p2, debug = True)
        
        # creamos el estado inicial
        state = []
        for player in [self.battle.p1, self.battle.p2]:
            for pokemon in player.pokemon:
                state.append(self.pokemons[pokemon.species])
                state.append(pokemon.hp)
                state.append(self.moves[pokemon.moves[0]])

        self.state = np.array(state, dtype = np.int8)

    def reset(self):
        # reseteamos la batalla
        self.battle =  sim.Battle('single', 'equipo_1', teams[team_p1], 'equipo_2', teams[team_p2], debug = True)

    def step(self, action_p1:int, action_p2:int):
        # los jugadores eligen los movimientos
        sim.decide(self.battle.p1, action_p1)
        sim.decide(self.battle.p2, action_p2)

        hp_p1 = self.battle.p1.active_pokemon[0].hp
        hp_p2 = self.battle.p2.active_pokemon[0].hp

        # ejecutamos el turno
        sim.do_turn(self.battle)

        hp_p1_new = self.battle.p1.active_pokemon[0].hp
        hp_p2_new = self.battle.p2.active_pokemon[0].hp

        # calculamos la recompensa
        reward_p1 = (hp_p2 - hp_p2_new) / self.battle.p1.active_pokemon[0].maxhp * 10 - (hp_p1 - hp_p1_new) / self.battle.p1.active_pokemon[0].maxhp * 10 # máximo de 10pts

        reward_p2 = (hp_p1 - hp_p1_new) / self.battle.p2.active_pokemon[0].maxhp * 10 - (hp_p2 - hp_p2_new) / self.battle.p2.active_pokemon[0].maxhp * 10 # máximo de 10pts

        # calculamos si el juego ha terminado
        done = self.battle.ended

        winner = -1

        if done:
            if self.battle.winner == 'p1':
                reward_p1 += 20
                winner = 0
                reward_p2 += -20
            else:
                reward_p1 += -20
                winner = 1
                reward_p2 += 20

        return (reward_p1, reward_p2), done, winner

    # devuelve una lista con los nombres de los pokemons de los equipos
    @classmethod
    def get_teams(cls):
        teams = []

        PATH = os.path.dirname(os.path.abspath(__file__))
        PATH_TEAMS = PATH + "/data/equipos/"

        for filename in os.listdir(PATH_TEAMS):
            if filename.endswith(".json"):
                team = []
                
                with open(PATH_TEAMS + filename) as file:
                    team_data = json.load(file)

                    for pokemon in team_data:
                        team.append(pokemon["species"])

                teams.append(team)

        return teams

