import heapq
from player import *

def new_battle(format_str:str, name1:str, team1:List[PokemonSet],
                name2:str, team2:List[PokemonSet], debug:bool) -> Battle:
    return Battle(format_str, name1, team1, name2, team2, debug)

def choose(B:Battle, player_uid:int, choice:str)-> None:
    choice = choice.split(' ')

    c = Decision(choice[0], int(choice[1]))

    if player_uid == 1:
        B.p1.choice = c

    if player_uid == 2:
        B.p2.choice = c

    return

def run(B:Battle) -> None:

    MAX_TURNS = 500

    while not B.ended:
        default_decide(B.p1)
        default_decide(B.p2)

        do_turn(B)

        if B.turn > MAX_TURNS:
            break

    return

def do_turn(B:Battle) -> None:
    if B.p1.choice is None or B.p2.choice is None:
        sys.exit('BATTLE ERROR: one or more sides has invalid decision')

    