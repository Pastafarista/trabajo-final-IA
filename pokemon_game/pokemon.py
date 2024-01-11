import random
from structs import *

'''
    Estas funciones se pueden modificar si se desea añadir tanto las naturalezas
    como las habilidades y objetos
'''

def get_attack(P:Pokemon) -> float:
    return P.stats.attack

def get_defense(P:Pokemon) -> float:
    return P.stats.defense

def get_specialattack(P:Pokemon) -> float:
    return P.stats.specialattack

def get_specialdefense(P:Pokemon) -> float:
    return P.stats.specialdefense

def get_speed(P:Pokemon, trickroom:bool, tailwind:bool) -> float:
    modifier = dex.boost[P.boosts['spd']]

    if tailwind:
        modifier *=2.0
    if trickroom:
        return 12096 - (P.stats.speed * modifier)
    
    return P.stats.speed * modifier

def get_accuracy(P:Pokemon) -> float:
    return dex.accuracy[P.boosts['accuracy']]

def get_evasion(P:Pokemon) -> float:
    return dex.evasion[P.boosts['evasion']]

def damage(P:Pokemon, dmg:int, flag:str=None) -> int:
    '''
        Calcula el valor de daño que recibe el pokemon además de calcular su vida
    '''

    old_hp = P.hp
    
    if P.fainted:
        return 0

    if flag in {'percentmax', 'percentmaxhp'}:
        dmg *= P.stats.hp
    elif flag == 'percentcurrent':
        dmg *= P.hp

    P.hp -= math.floor(dmg)

    if P.hp > P.stats.hp:
        P.hp = P.stats.hp

    diff_hp = old_hp - P.hp

    if P.hp <= 0:
        faint(P)
    return diff_hp

def faint(P:Pokemon) -> None:
    '''
        Mata al pokemon
    '''
    P.volatile_statuses = set()
    P.status = ''
    P.trapped = False
    P.hp = 0
    P.fainted = True

    if P.debug:
        print(P.name + ' fainted')
    return

def add_status(P:Pokemon, status:str, source:Pokemon=None):
    
    if P.status != '':
        return False
    if status is None:
        return False

    if status == 'brn' and ('Fire' in P.types):
        return False
    if status == 'par' and ('Electric' in P.types):
        return False
    if (status == 'psn' or status == 'tox') and ('Poison' in P.types or 'Steel' in P.types):
        if source is not None and source.ability == 'corrosion':
            pass
        else:
            return False

    if status == 'slp':
        P.sleep_n = random.randint(1, 3)

    P.status = status
    return True

def cure_status(P:Pokemon) -> bool:
    if P.status == '':
        return False
    P.toxic_n = 1
    P.status = ''
    return True

def boost(P:Pokemon, boosts:Dict[str, int]) -> None:
    if boosts is None:
        return
    for stat in boosts:
        P.boosts[stat] += boosts[stat]
        if P.boosts[stat] > 6:
            P.boosts[stat] = 6
        if P.boosts[stat] < -6:
            P.boosts[stat] = -6
    return