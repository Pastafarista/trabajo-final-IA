import random, json
import os

# Directorio padre
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directorio de los archivos de los pokemons
POKEMON_DIR = os.path.join(BASE_DIR, 'data/pokemons/')

def create_team_2(num_pokemons):
    pokemons = ['clawitzer' , 'zeraora', 'haxorus', 'aurorus', 'decidueye', 'delphox', 'toxapex', 'volcarona', 'spiritomb', 'hydreigon', 'ambipom', 
               'celesteela', 'togekiss', 'stakataka', 'aegislash', 'ferrothorn', 'audino', 'keldeo', 'excadrill', 'mimikyu', 'bisharp', 
               'garchomp', 'azumarill', 'salazzle', 'salamence', 'raichu', 'gyarados', 'chandelure', 'tapufini', 'blissey']
    
    team = []

    for i in range(num_pokemons):
        selected_pokemon = pokemons[random.randint(0,len(pokemons) - 1)]

        pokemon = {}
        pokemon['species'] = selected_pokemon
        pokemon['name'] = selected_pokemon

        with open(POKEMON_DIR + selected_pokemon + '.json') as pokemon_file:
            general_pokemon = json.load(pokemon_file)

            moves = general_pokemon['moves']
            ivs = general_pokemon['ivs']
            evs = general_pokemon['evs']
            nature = general_pokemon['nature']

            pokemon['moves'] = moves
            pokemon['ivs'] = ivs
            pokemon['evs'] = evs
            pokemon['nature'] = nature

        team.append(pokemon)

    return team

def create_team(pokemons:list[str]) -> list[dict]:
    team = []

    if len(pokemons) > 6:
        raise ValueError('The team must have 6 or less pokemons')

    for pokemon in pokemons:
        selected_pokemon = pokemon

        pokemon = {}
        pokemon['species'] = selected_pokemon
        pokemon['name'] = selected_pokemon

        with open(POKEMON_DIR + selected_pokemon + '.json') as pokemon_file:
            general_pokemon = json.load(pokemon_file)

            moves = general_pokemon['moves']
            ivs = general_pokemon['ivs']
            evs = general_pokemon['evs']
            nature = general_pokemon['nature']

            pokemon['moves'] = moves
            pokemon['ivs'] = ivs
            pokemon['evs'] = evs
            pokemon['nature'] = nature

        team.append(pokemon)

    return team
