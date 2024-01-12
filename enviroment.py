# Authors: Antonio Cabrera, Alejandro Gómez, Alejandro Jiménez, Antonio Perez, Luis Crespo
# Description: El fichero contiene la clase Environment, que representa el entorno en el que se desarrolla el juego.

import os
import json

class Enviroment():
    def __init__(self):
        pass

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

# testeo
if __name__ == "__main__":
    pokemons, moves = map_data()
    print(pokemons)
    print(moves)
