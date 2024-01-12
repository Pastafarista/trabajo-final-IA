import sys
import random
from pokemon import *

def default_decide(T:Player) -> None:
    n = len(T.active_pokemon)

    for i in range(n):
        if len(T.active_pokemon[i].moves) > 0:
            rand_int = random.randint(0, len(T.active_pokemon[i].moves) - 1)
            T.choice = Decision('move', str(rand_int))
        else:
            sys.exit('No movements left')
    
    return

def decide(T:Player, movement:int) -> None:
    n = len(T.active_pokemon)

    for i in range(n):
        if len(T.active_pokemon[i].moves) > 0:
            T.choice = Decision('move', str(movement))
        else:
            sys.exit('No movements left')
    
    return

def pokemon_left(player:Player) -> int:
    left_pokemon = 0

    for p in player.pokemon:
        if p.fainted == False:
            left_pokemon += 1

    return left_pokemon
