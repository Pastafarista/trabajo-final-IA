from typing import List, Set, Dict, Any, Tuple, NewType
from dataclasses import dataclass, field, InitVar
from data import dex
import math

@dataclass
class PokemonSet:
    '''
        Seteamos los valore de los pokemon con los que va a jugar cada uno de 
        los jugadores
    '''

    name: str
    species : str
    moves : List[str] #Importamos la librería list para hacer una lista de movimientos
    evs : Tuple[int, int, int, int, int, int] 
    ivs : Tuple[int, int, int, int, int, int]
    level : int


Team = List[PokemonSet]

@dataclass
class Decision:
    '''
        Con esto lo que conseguimos es saber quien ataca a quien, porque no vamos
        a permitir que cambie de pokemon
    '''
    type : str
    selection : str
    target : str = 'foe0'

    def __repr__(self):
        return self.type + ' ' + str(self.selection)
    
@dataclass
class Stats:
    '''
        Son las stats de los pokemons
    '''
    hp : int
    attack : int
    defense : int
    specialattack : int
    specialdefense : int
    speed : int

@dataclass
class Action:
    '''
        Función que permite saber el proximo movimiento del usuario, al solo
        permitir atacar será un ataque. Pero se puede implementar el cambio
    '''

    action_type : str
    user : Any = field(repr=False, default=None) #Apunta hacía el pokemon
    move : Any = field(repr=False, default=None)
    target : str = 'foe0'

    def __repr__(self):
        return '(' + self.action_type + ' action)'
    
@dataclass
class Pokemon:

    #Valores para setear los jugadores y los pokemons de cada jugador

    player_uid : int
    position : int
    poke : InitVar[PokemonSet] = None 
    packed : InitVar[str] = None
    debug : bool = False

    #Valores base de los pokemons

    id : str = ''
    name: str = ''
    species : str = ''
    moves : List[str] = field(init = False) 
    
    stats : Stats = field(init=False)
    hp : int = field(init=False)
    maxhp : int = field(init=False)

    pp : Dict[str, int] = field(default_factory=dict) #Cantidad de movimientos por ataque

    #Distintos estados en los que puede encontrarse el pokemon

    fainted : bool = False
    status : str = ''
    protect_n : int = 0
    toxic_n : int = 1
    sleep_n : int = 0
    bound_n : int = 0
    encore_n : int = 0
    perishsong_n : int = 0
    taunt_n : int = 0

    substitute : bool = False
    substitute_hp : int = 0

    #Movimientos que realiza el pokemon
    last_damaging_move : str = None
    last_used_move : str = None

    consecutive_move_uses : int = 0

    volatile_statuses : Set[str] = field(default_factory=set)

    active : bool = False
    active_turns : int = 0

    level : int = 100
    types : List[str] = field(init=False)

    def __post_init__(self, poke, packed):
        if poke is None:
            poke = packed_str_to_pokemon_set(packed)
        self.boosts = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'accuracy': 0,
            'evasion': 0
        }
        self.name = poke.name
        self.species = poke.species
        self.id = poke.species
        self.moves = poke.moves

        self.stats = calculate_stats(self, poke.evs, poke.ivs)

        self.hp = self.stats.hp
        self.maxhp = self.stats.hp
        self.types = dex.pokedex[self.species].types

        for move in self.moves:
            self.pp[move] = dex.move_dex[move].pp

        return
    
@dataclass
class Player:
    '''
        Valores para el jugador y que pokemons tiene
    '''
    
    name : str
    uid : int # one indexed
    team : InitVar[List[PokemonSet]] = None
    debug : bool = False

    pokemon : List[Pokemon] = field(repr=False, default_factory=list)
    bench : List[Pokemon] = field(repr=False, default_factory=list)
    active_pokemon : List[Pokemon] = field(repr=False, default_factory=list)

    volatile_statuses : Set[str] = field(default_factory=set)
    side_conditions : Set[str] = field(default_factory=set)

    #Valores de campo, es decir, estados en los que se encuentra el campo
    spikes : int = 0
    toxic_spikes : int = 0
    stealth_rock : bool = False
    sticky_web : bool = False
    tailwind : bool = False
    tailwind_n : int = 0 

    request : str = 'move'
    choice : Decision = None

    def __post_init__(self, team:List[PokemonSet]):
        i = 0
        for poke in team:
            pokemon = Pokemon(self.uid, i, poke, debug=self.debug)
            self.pokemon.append(pokemon) 
            i += 1 
        return
    
@dataclass 
class Battle:
    '''
        Valores de configuración del combate
    '''

    format_str : InitVar[str] = 'single'
    name1 : InitVar[str] = 'Nic'
    name2 : InitVar[str] = 'Sam'
    team1 : InitVar[List[PokemonSet]] = None
    team2 : InitVar[List[PokemonSet]] = None
    debug : bool = False
    turn : int = 0
    pseudo_turn : bool = False
    doubles : bool = False
    rng : bool = True
    winner : str = None
    ended : bool = False
    started : bool = False
    setup_ran : bool = False
    log : List[str] = field(default_factory=list)

    # players
    p1 : Player = field(init=False)
    p2 : Player = field(init=False)

    #Estados del campo de batalla
    weather : str = 'clear'
    weather_n : int = 0
    terrain : str = ''
    trickroom : bool = False
    trickroom_n : int = 0

    def __post_init__(self, format_str, name1, team1, name2, team2,):
        if format_str == 'double':
            self.doubles = True
        self.p1 = Player(name1, 1 , team1, debug=self.debug)
        self.p2 = Player(name2, 2 , team2, debug=self.debug)

        self.set_up()
        return

    def set_up(self):
        self.p1.active_pokemon.append(self.p1.pokemon[0])
        self.p2.active_pokemon.append(self.p2.pokemon[0])
        for i in range(len(self.p1.pokemon)-1):
            self.p1.bench.append(self.p1.pokemon[i+1])

        for i in range(len(self.p2.pokemon)-1):
            self.p2.bench.append(self.p2.pokemon[i+1])

        self.setup_ran = True
        return
    
def get_active_pokemon(B:Battle) -> List[Pokemon]:
    '''
        Saber que pokemons se encuentra activo en el terreno
    '''

    active = []
    for pokemon in B.p1.active_pokemon:
        active.append(pokemon)
    for pokemon in B.p2.active_pokemon:
        active.append(pokemon)
    return active

def dict_to_team_set(in_team : List) -> List[PokemonSet]:
    '''
        Creacion del diccionario de los equipos pokemon
    '''
    team = []
    for in_poke in in_team:
        name = in_poke['species']
        species = in_poke['species']
        moves = in_poke['moves']
        evs = in_poke['evs']
        ivs = in_poke['ivs']
        poke = PokemonSet(name, species, moves, evs, ivs=ivs)
        team.append(poke)
    return team

def calculate_stats(P:Pokemon, evs:List[int], ivs:List[int]) -> Stats:
    base_stats = dex.pokedex[P.species].baseStats
    lvl = P.level
    iv = ivs[0] #hp iv
    ev = evs[0] #hp ev
    hp = math.floor(((iv + (2 * base_stats.hp) + (ev/4)) * (lvl/100)) + 10 + lvl)

    stats = ['attack', 'defense', 'specialattack', 'specialdefense', 'speed']
    cal = []
    i = 1
    for stat in stats:
        base = getattr(base_stats, stat)
        iv = ivs[i]
        ev = evs[i]
        nature_mod = dex.nature_dex[P.nature].values[stat]
        cal.append(math.floor(math.floor((((iv + (2 * base) + (ev/4)) * (lvl/100)) + 5)) * nature_mod))
        i += 1

    return Stats(hp, cal[0], cal[1], cal[2], cal[3], cal[4])

#Comprobar si esto funciona
def packed_str_to_pokemon_set(packed : str) -> PokemonSet:
    a = packed.split('|')
    m = a[4].split(',')
    e = a[6].split(',')
    i = a[8].split(',')
    poke = PokemonSet(a[0], a[1], a[2], a[3], m, a[5], e, a[7], i, a[9], a[10], a[11])