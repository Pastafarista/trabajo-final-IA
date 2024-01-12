# Description: Add the line name to all the JSON files in data/pokemon

import json
import os

PATH = os.path.dirname(os.path.abspath(__file__)) + '/data/pokemons'

for filename in os.listdir(PATH):
    if filename.endswith('.json'):
        with open(PATH + '/' + filename, 'r') as f:
            data = json.load(f)
            data['name'] = filename.split('.')[0]
        with open(PATH + '/' + filename, 'w') as f:
            json.dump(data, f, indent=4)

