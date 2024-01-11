import json
import time
from collections import namedtuple
import random
import re


#this module is for searching the dex, aka all the game data

#missing statuses, scripts, rulesets(formats), formatsdata( event pokemon and thespeed move_dex), aliases

with open('data/moves.json') as f:
    moves_raw_data = json.load(f)
with open('data/pokedex.json') as f:
    pokemon_raw_data = json.load(f)
with open('data/typechart.json') as f:
    typecharts_raw_data = json.load(f)
with open('data/all.json') as f:
    pokemon_raw_base = json.load(f)

# target can be : 'foe0', 'foe1', 'ally', 'self', 'foes', 'allies', 'adjacent', 'all'
class Decision(namedtuple('Decision', ['type', 'selection', 'target'])):
    def __new__(cls, type, selection, target='foe0'):
        return super(Decision, cls).__new__(cls, type, selection, target)
        
class Action(namedtuple('Action', ['user', 'move', 'target', 'base_move'])):
    def __new__(cls, user, move, target=None, base_move=None):
        return super(Action, cls).__new__(cls, user, move, target, base_move)

index_to_id_pokemon = {}
for poke in pokemon_raw_base:
    index_to_id_pokemon[pokemon_raw_data[poke]['num']] = poke

index_to_id_moves = {}
for move in moves_raw_data:
    index_to_id_moves[moves_raw_data[move]['num']] = move


#-------------
#POKEDEX
#-------------

pokemonAttributes = ['id', 'num', 'species', 'baseSpecies', 'forme', 'formeLetter', 'types', 
                        'genderRatio', 'baseStats', 'abilities', 'heightm', 'weightkg', 'color',
                        'prevo', 'evos', 'evoLevel', 'eggGroups', 'otherFormes', 'tier', 'requiredItem']
pokedex = {}

Pokemon = namedtuple('Pokemon', pokemonAttributes)
GenderRatio = namedtuple('GenderRatio', 'male female')
Stats = namedtuple('Stats', 'hp attack defense specialattack specialdefense speed')
BaseAbilities = namedtuple('BaseAbilities', 'normal0 normal1 hidden')

for i in pokemon_raw_data:
    for a in pokemonAttributes:
        if a not in pokemon_raw_data[i]:
            pokemon_raw_data[i][a] = None
        else:
            if a == 'genderRatio':
                pokemon_raw_data[i][a] = GenderRatio(pokemon_raw_data[i][a]['M'], pokemon_raw_data[i][a]['F'])
            elif a == 'baseStats':
                pokemon_raw_data[i][a] = Stats(pokemon_raw_data[i][a]['hp'], pokemon_raw_data[i][a]['atk'], pokemon_raw_data[i][a]['def'], pokemon_raw_data[i][a]['spa'],  pokemon_raw_data[i][a]['spd'], pokemon_raw_data[i][a]['spe'])
            elif a == 'abilities':
                pokemon_raw_data[i][a] = BaseAbilities(pokemon_raw_data[i][a].get('0'), pokemon_raw_data[i][a].get('1'), pokemon_raw_data[i][a].get('H'))

    pokemon_raw_data[i]['id'] = i

    pokedex[i] = Pokemon._make([pokemon_raw_data[i][j] for j in pokemonAttributes])

#--------
#moves_raw_data
#---------

move_attributes = ['num', 'accuracy', 'category', 'desc', 'id', 'name', 'pp',
                   'priority', 'flags', 'type', 'terrain', 'crit_ratio',
                   'ignore_accuracy', 'weather', 'drain', 'heal', 'recoil',
                   'target_type', 'base_power', 'short_desc', 'ignore_ability',
                   'ignore_defensive', 'ignore_evasion', 'ignore_immunity', 
                   'breaks_protect', 'defensive_category', 'force_switch', 
                   'future_move', 'unreleased', 'viable', 'multi_hit',
                   'no_faint', 'no_pp_boosts', 'no_sketch', 'pseudo_weather',
                   'thaws_target', 'self_switch', 'side_condition', 'sleep_usable',
                   'true_damage', 'primary', 'secondary', 'z_move']
flags = ['pulse', 'bullet', 'sound', 'powder', 'authentic', 'nonsky', 'distance',
         'dance', 'mystery', 'protect', 'snatch', 'recharge', 'gravity', 'mirror',
         'contact', 'punch', 'defrost', 'charge', 'bite', 'reflectable', 'heal']
recoil_attributes = ['damage', 'type', 'condition']
move_dex = {}

Move = namedtuple('Move', move_attributes) #some missing props
Flags = namedtuple('Flags', flags)
Recoil = namedtuple('Recoil', recoil_attributes)
        
for move in moves_raw_data:
    moves_raw_data[move]['flags'] = Flags._make([moves_raw_data[move]['flags'][flag] for flag in flags])
    moves_raw_data[move]['recoil'] = Recoil._make([moves_raw_data[move]['recoil'][attribute] for attribute in recoil_attributes])
    move_dex[move] = Move._make([moves_raw_data[move][attribute] for attribute in move_attributes])


#--------
#TypeChart
#---------

typechartAttributes = ['damage_taken', 'HPivs']
damagetakenAttributes = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']

typechart_dex = {}

TypeChart = namedtuple('TypeChart', typechartAttributes)
DamageTaken = namedtuple('DamageTaken', 'prankster par brn trapped powder sandstorm hail frz psn tox Bug Dark Dragon Electric Fairy Fighting Fire Flying Ghost Grass Ground Ice Normal Poison Psychic Rock Steel Water')

for i in typecharts_raw_data:
    for a in typechartAttributes:
        if a not in typecharts_raw_data[i]:
            typecharts_raw_data[i][a] = None
#        else:
#            if a == 'damage_taken':
#                for y in damagetakenAttributes:
#                    if y not in typecharts_raw_data[i][a]:
#                        typecharts_raw_data[i][a][y] = None
#                typecharts_raw_data[i][a] = DamageTaken._make([typecharts_raw_data[i][a][j] for j in damagetakenAttributes])

    typechart_dex[i] = TypeChart._make([typecharts_raw_data[i][j] for j in typechartAttributes])


#---------------------
#ACCURACY AND BOOSTS
#---------------------

accuracy = {
    -6: 0.333,
    -5: 0.375,
    -4: 0.430,
    -3: 0.500,
    -2: 0.600,
    -1: 0.750,
    0: 1.000,
    1: 1.3333,
    2: 1.6667,
    3: 2.000,
    4: 2.3333,
    5: 2.6667,
    6: 3.000,
}

evasion = {
    6: 0.333,
    5: 0.375,
    4: 0.430,
    3: 0.500,
    2: 0.600,
    1: 0.750,
    0: 1.000,
    -1: 1.3333,
    -2: 1.6667,
    -3: 2.000,
    -4: 2.3333,
    -5: 2.6667,
    -6: 3.000,
}

boosts = {
    -6: 0.25,
    -5: 0.28,
    -4: 0.33,
    -3: 0.40,
    -2: 0.50,
    -1: 0.66,
    0: 1.0,
    1: 1.5,
    2: 2.0,
    3: 2.5,
    4: 3.0,
    5: 3.5,
    6: 4.0,
}

no_metronome = {
    "afteryou",
    "assist",
    "belch",
    "bestow",
    "celebrate",
    "chatter",
    "copycat",
    "counter",
    "covet",
    "craftyshield",
    "destinybond",
    "detect",
    "diamondstorm",
    "dragonascent",
    "endure",
    "feint",
    "focuspunch",
    "followme",
    "freezeshock",
    "happyhour",
    "helpinghand",
    "holdhands",
    "hyperspacefury",
    "hyperspacehole",
    "iceburn",
    "kingsshield",
    "lightofruin",
    "matblock",
    "mefirst",
    "metronome",
    "mimic",
    "mirrorcoat",
    "mirrormove",
    "naturepower",
    "originpulse",
    "precipiceblades",
    "protect",
    "quash",
    "quickguard",
    "ragepowder",
    "relicsong",
    "secretsword",
    "sketch",
    "sleeptalk",
    "snarl",
    "snatch",
    "snore",
    "spikyshield",
    "steameruption",
    "struggle",
    "switcheroo",
    "technoblast",
    "thief",
    "thousandarrows",
    "thousandwaves",
    "transform",
    "trick",
    "vcreate",
    "wideguard"
}

# i shouldn't be using this, instead, i should be using the info in items.json

type_resist_berries = {
    'occaberry': 'Fire',
    'passhoberry': 'Water',
    'wacanberry': 'Electric',
    'rindoberry': 'Grass',
    'yacheberry': 'Ice',
    'chopleberry': 'Fighting',
    'kebiaberry': 'Poison',
    'shucaberry': 'Ground',
    'cobaberry': 'Flying',
    'payapaberry': 'Psychic',
    'tangaberry': 'Bug',
    'chartiberry': 'Rock',
    'kasibberry': 'Ghost',
    'habanberry': 'Dragon',
    'colburberry': 'Dark',
    'babiriberry': 'Steel',
}

magnitude_power = [10, 30, 30, 50, 50, 50, 50, 70, 70, 70, 70, 70, 70, 90, 90, 90, 90, 110, 110, 150]
