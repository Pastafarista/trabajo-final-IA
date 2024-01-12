import random, json

def create_team(num_pokemons):
    pokemons = ['clawitzer' , 'zeraora', 'haxorus', 'aurorus', 'decidueye', 'delphox', 'toxapex', 'volcarona', 'spiritomb', 'hydreigon', 'ambipom', 
               'celesteela', 'togekiss', 'stakataka', 'aegislash', 'ferrothorn', 'audino', 'keldeo', 'excadrill', 'mimikyu', 'bisharp', 
               'garchomp', 'azumarill', 'salazzle', 'salamence', 'raichu', 'gyarados', 'chandelure', 'tapufini', 'blissey']
    
    team = []

    for i in range(num_pokemons):
        selected_pokemon = pokemons[random.ranint(len(pokemons) - 1)]

        pokemon = {}
        pokemon['species'] = selected_pokemon

        with open(selected_pokemon + '.json') as pokemon_file:
            general_pokemon = json.load(pokemon_file)

            moves = general_pokemon['moves']
            ivs = general_pokemon['ivs']
            evs = general_pokemon['evs']

            pokemon['moves'] = moves
            pokemon['ivs'] = ivs
            pokemon['evs'] = evs

        team.append(pokemon)

           