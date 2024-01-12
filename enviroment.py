# Authors: Antonio Cabrera, Alejandro Gómez, Alejandro Jiménez, Antonio Perez, Luis Crespo
# Description: El fichero contiene la clase Environment, que representa el entorno en el que se desarrolla el juego.

import os
import json
import sys

# añadimos el directorio pokemon_game al path para poder importar los modulos
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, PATH + "/pokemon_game")

import pokemon_game.simulator as sim
from pokemon_game.select_pokemon import create_team

def map_data():
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

class Enviroment():
    def __init__(self):
        # cargamos los datos de los pokemons y los movimientos
        self.pokemons, self.moves = map_data()

# test
if __name__ == "__main__":
       
    env = Enviroment()

    # creamos los equipos de 6 pokemons
    pokemons = ['clawitzer' , 'zeraora', 'haxorus', 'aurorus', 'decidueye', 'delphox']

    team_1 = create_team(pokemons)
    team_2 = create_team(pokemons)
    
    # creamos la batalla
    battle = sim.Battle('single', 'prueba', team_1, 'prueba2', team_2, debug = True)

    # los jugadores eligen los movimientos
    sim.decide(battle.p1, 1)
    sim.decide(battle.p2, 1)

    # ejecutamos el turno
    sim.do_turn(battle)



