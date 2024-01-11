import heapq
from player import *
from turn import turn_start, turn_end, run_action, create_move, populate_action_queue

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

    turn_start(B)

    if B.debug:
        print('---Turn ' + str(B.turn) + '---')
        print(B.p1.choice)
        print(B.p2.choice)

    # create and populate action queue
    # elements of queue are in form (priority : int, action : Action)
    q : List[Tuple[float, Action]] = []
    for player in [B.p1,B.p2]:
        for i in range(len(player.active_pokemon)):
            poke = player.active_pokemon[i]
            choice = player.choice
            move = create_move(B, poke, choice)
            populate_action_queue(q, poke, choice, move, player, B)

    # run each each action in the queue
    if B.debug:
        print(q)
        print()
    while q:
        priority, next_action = heapq.heappop(q) 
        run_action(B, next_action)
    
    if not B.pseudo_turn:
        turn_end(B)

    #check for a winner
    if not pokemon_left(B.p1):
        B.ended = True
        B.winner = 'p2'
        if B.debug:
            print('p2 won')
    if not pokemon_left(B.p2):
        B.ended = True
        B.winner = 'p1'
        if B.debug:
            print('p1 won')

    #request the next turns move
    B.pseudo_turn = False
    B.request = 'move'
    B.p1.request = 'move'
    B.p2.request = 'move'

    #check if a pokemon fainted and insert a pseudo turn
    for pokemon in get_active_pokemon(B):
        if pokemon.fainted:
            B.pseudo_turn = True
            
    if B.pseudo_turn:
        # check player 1's pokemon
        for i in range(len(B.p1.active_pokemon)):
            if B.p1.active_pokemon[i].fainted:
                B.p1.request = 'switch'
            else:
                B.p1.request = 'pass'

        # check player 2's pokemon
        for i in range(len(B.p2.active_pokemon)):
            if B.p2.active_pokemon[i].fainted:
                B.p2.request = 'switch'
            else:
                B.p2.request = 'pass'
    
    if B.debug:
        print('---End of Turn ' + str(B.turn) + '---')
    return
    