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
    def __init__(self, team_p1:int, team_p2:int):
        # cargamos los datos de los pokemons y los movimientos
        self.pokemons, self.moves = Environment.map_data()
        teams = Environment.get_teams()
       
        team_p1 = create_team(teams[team_p1])
        team_p2 = create_team(teams[team_p2])

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

    def step(self, action_p1:int, action_p2:int) -> None:
        # los jugadores eligen los movimientos
        sim.decide(self.battle.p1, action_p1)
        sim.decide(self.battle.p2, action_p2)

        # ejecutamos el turno
        sim.do_turn(self.battle)

    ''' 
    devuelve el estado actual:
        [nom_poke_p1, hp_poke_p1, move_1_poke_p1, move_2_poke_p1, move_3_poke_p1, move_4_poke_p1, 
         nom_poke_p2, hp_poke_p2, move_1_poke_p2, move_2_poke_p2, move_3_poke_p2, move_4_poke_p2, ended, winner]
    '''
    def get_state(self): 
        state = []
        for player in [self.battle.p1, self.battle.p2]:
            for pokemon in player.pokemon:
                state.append(self.pokemons[pokemon.species])
                state.append(pokemon.hp)
                
                for move in pokemon.moves:
                    state.append(self.moves[move])

        state.append(self.battle.ended)

        if self.battle.ended:            
            if self.battle.winner == 'p1':
                state.append(1)
            else:
                state.append(0)

        else:
            state.append(-1)

        return np.array(state, dtype = np.int8)
    
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


