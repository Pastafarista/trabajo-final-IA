import heapq
from player import *

def turn_start(B:Battle) -> None:

    B.turn += 1
    B.turn = math.floor(B.turn)

    if B.pseudo_turn:
        B.turn -= 0.5
        return
    for pokemon in get_active_pokemon(B):
        pokemon.active_turns += 1
        pokemon.pokemon_hit_this_turn = 0

        #Elimina los valores que duran solo un turno

        one_turn_statuses = {None, 'flinch', 'endure', 'protect', 'banefulbunker', 'spikyshield'}
        pokemon.volatile_statuses -= one_turn_statuses

def turn_end(B:Battle) -> None:
    
    '''
        Termine un turno
    '''

    if B.pseudo_turn:
        sys.exit('ERROR: turn_end() called on pseudo turn')

    # tick weather counter down
    if B.weather in ['sunlight', 'rain', 'sandstorm', 'hail']:
        B.weather_n -= 1
        if B.weather_n == 0:
            B.weather = 'clear'

    # weather damage
    for pokemon in get_active_pokemon(B):
        if B.weather == 'sandstorm': 
            if {'Steel','Rock','Ground'}.isdisjoint(pokemon.types):
                damage(pokemon, 1/16, flag='percentmaxhp')
        if B.weather == 'hail': 
            if 'Ice' not in pokemon.types:
                damage(pokemon, 1/16, flag='percentmaxhp')


    # volatile statuses
    for pokemon in get_active_pokemon(B):
        # bound
        if 'partiallytrapped' in pokemon.volatile_statuses:
            damage(pokemon, pokemon.bound_damage, flag='percentmaxhp')
            pokemon.bound_n -= 1
            if pokemon.bound_n == 0:
                pokemon.volatile_statuses -= {'partiallytrapped'}
        # aqua ring
        if pokemon.aqua_ring:
            dmg = -1/16
            if pokemon.item == 'bigroot':
                dmg *= 1.3
            damage(pokemon, dmg, 'percentmaxhp')
        # nightmare
        if 'nightmare' in pokemon.volatile_statuses:
            if pokemon.status == 'slp':
                damage(pokemon, 1/4, 'percentmaxhp')
        # perish song
        if 'perishsong' in pokemon.volatile_statuses:
            pokemon.perishsong_n -= 1
            if pokemon.perishsong_n == 0:
                faint(pokemon)
        # encore 
        if 'encore' in pokemon.volatile_statuses:
            pokemon.encore_n -= 1
            if pokemon.encore_n == 0:
                pokemon.volatile_statuses -= {'encore'}
        # taunt
        if 'taunt' in pokemon.volatile_statuses:
            pokemon.taunt_n -= 1
            if pokemon.taunt_n == 0:
                pokemon.volatile_statuses.remove('taunt')
        # curse
        if 'curse' in pokemon.volatile_statuses:
            if 'Ghost' in pokemon.types:
                damage(pokemon, 1/4, flag='percentmaxhp')

    # do major status checks
    for pokemon in get_active_pokemon(B):
        if pokemon.status == 'brn':
            damage(pokemon, 1/16, flag='percentmax')
        elif pokemon.status == 'psn':
            damage(pokemon, 1/8, flag='percentmax')
        elif pokemon.status == 'tox':
            dmg = 1/16*pokemon.toxic_n
            damage(pokemon, dmg, flag='percentmax')
            pokemon.toxic_n += 1
        elif pokemon.status == 'frz':
            #twenty percent chance to be thawed
            if random.random() < 0.20:
                cure_status(pokemon)
            if B.weather == 'sunlight':
                cure_status(pokemon)
        elif pokemon.status == 'slp':
            pokemon.sleep_n -= 1
            if pokemon.sleep_n == 0:
                cure_status(pokemon)
    return

def run_action(B, a : Action) -> None:
    if not B.doubles and a.target[0:3] == 'foe':
        p = a.user.player_uid
        if p == 1:
            run_move(B, a.user, a.move, B.p2.active_pokemon[0])
        if p == 2:
            run_move(B, a.user, a.move, B.p1.active_pokemon[0])
        return

    if a.target == 'all': 
        move = move._replace(base_power = move.base_power * 0.75)
        for pokemon in get_active_pokemon(B):
            B.run_move(a.user, move, pokemon)
        return

    return

def run_move(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> None:

    '''
        Realiza el movimiento que se ha decidido
    '''
    if user.fainted:
        return
    
    if move.id != 'struggle':
        if move.id in user.pp:
            user.pp[move.id] -= 1

    user.last_used_move = move.id

    #Se actualiza el movimiento que se realiza 
    move = update_move_before_running(B, user, move, target)

    #Hay que revisar si el movimiento elegido acierta o no
    if not accuracy_check(B, user, move, target):
        if B.debug:
            print(user.name + ' used ' + move.id + ' and missed')
        return
    
    '''
        Hay movimientos que pueden atacar varias veces al mismo usuario, por lo que se comprueba
        si puede realizar varios golpes
    '''
    number_hits = 1
    if move.multi_hit is not None:
        number_hits = random.choice(move.multi_hit)

    #Se vuelve a comprobar el acierto del ataque
    for i in range(number_hits):
        if i != 1 and move.id == 'triplekick':
            if not accuracy_check(B, user, move, target):
                return

        dmg = calc_damage(B, user, move, target)
        dmg = damage(target, dmg)

    if dmg > 0:
        target.last_damaging_move = move.id

    unique_moves_after_damage(B, user, move, target, dmg)

    #Algunos ataques suben estadísticas de los pokemon después de atacar
    boosts_statuses(B, user, move, target)
    if B.debug:
        print(user.name + ' used ' + move.id + '')

    return

def calc_damage(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> int:
    '''
        Calcular el daño que inflige cada ataque
    '''   
    dmg = 0
    modifier = 1
    type_modifier = 1

    if move.category == 'Status':
        return 0

    power = move.base_power
    if move.category == 'Special':
        attack = get_specialattack(user)
        defense = get_specialdefense(target)
    elif move.category == 'Physical':
        attack = get_attack(user)
        defense = get_defense(target)

    #Formula para calcular el daño 
    dmg = (math.floor(math.floor(math.floor(((2 * user.level) / 5) + 2) * attack * power / defense) / 50) + 2) 

    if move.type in user.type:
        modifier *= 1.5

    for each in target.types:
        type_effect = dex.typechart_dex[each].damage_taken[move.type]
        type_modifier *= type_effect
        modifier *= type_effect

    # WEATHER
    if B.weather in ['rain', 'heavy_rain']:
        if move.type == 'Water':
            modifier *= 1.5
        elif move.type == 'Fire':
            modifier *= 0.5
    elif B.weather in ['sunlight', 'heavy_sunlight']:
        if move.type == 'Water':
            modifier *= 0.5
        elif move.type == 'Fire':
            modifier *= 1.5

    # burn
    if user.status == 'brn' and move.category == 'Physical' and user.ability != 'guts':
        modifier *= 0.5
    
    dmg = math.floor(dmg)
    dmg *= modifier
    dmg = math.floor(dmg)
    return dmg


def accuracy_check(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> bool:
    '''
        Comprobar el acierto del movimiento
    '''

    # full paralyze
    if user.status == 'par' and random.random() < 0.25:
        return False
    # asleep pokemon miss unless they use snore or sleeptalk
    elif user.status == 'slp' and not move.sleep_usable:
        return False

    # Is the target protected?
    if 'protect' in target.volatile_statuses and move.flags.protect:
        return False
    if 'banefulbunker' in target.volatile_statuses and move.flags.protect:
        return False
    if 'spikyshield' in target.volatile_statuses and move.flags.protect:
        return False
    if 'kingsshield' in target.volatile_statuses and move.flags.protect and move.category != 'Status':
        return False

    # protect moves accuracy
    if move.id in ['protect', 'detect', 'endure', 'wide guard', 'quick guard', 'spikyshield', 'kingsshield', 'banefulbunker']:
        rand_float = random.random()
        n = user.protect_n
        user.protect_n += 3
        if not B.rng and n > 0:
            return False
        if n == 0 or rand_float < (1.0 / n):
            return True
        return False
    else:
        # if the move is not a protect move, reset the counter
        user.protect_n = 0

    # flinched
    if 'flinch' in user.volatile_statuses:
        return False

    # fake out fails after 1 turn active
    if move.id == 'fakeout' and user.active_turns > 1:
        return False

    # if user is taunted, status moves fail
    if move.category == 'Status' and 'taunt' in user.volatile_statuses:
        return False

    # these moves dont check accuracy in certain weather
    if move.id == 'thunder' and B.weather == 'rain':
        return True
    if move.id == 'hurricane' and B.weather == 'rain':
        return True
    if move.id == 'blizzard' and B.weather == 'hail':
        return True

    # some moves don't check accuracy
    if move.accuracy is True:
        return True
    
    temp = random.randint(0, 99)
    accuracy = get_accuracy(user)
    evasion = get_evasion(target)
    check = 100

    if B.rng:
        check = (move.accuracy * accuracy * evasion)

    return temp < check 

def boosts_statuses(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> None:
    # stat changing moves 
    user_volatile_status = ''
    target_volatile_status = ''
    # primary effects
    if move.primary['boosts'] is not None:
        boost(target, move.primary['boosts'])
    if move.primary['volatile_status'] is not None:
        target_volatile_status = move.primary['volatile_status']
        target.volatile_statuses.add(target_volatile_status)

    if move.primary['self'] is not None:
        if 'boosts' in move.primary['self']:
            boost(user, move.primary['self']['boosts'])
        if 'volatile_status' in move.primary['self']:
            user_volatile_status = move.primary['self']['volatile_status']
            user.volatile_statuses.add(user_volatile_status)

    if move.primary['status'] is not None:
        add_status(target, move.primary['status'])

      # secondary effects
    for effect in move.secondary:
        if not target.fainted:
            temp = random.randint(0, 99)
            check = effect['chance']
            if check != 100 and not B.rng:
                check = 0
            if temp < check:
                if 'boosts' in effect:
                    boost(target, effect['boosts'])
                if 'status' in effect:
                    add_status(target, effect['status'], user)
                if 'volatile_status' in effect:
                    target_volatile_status = effect['volatile_status']
                    target.volatile_statuses.add(target_volatile_status)

    if target_volatile_status == 'partiallytrapped':
        target.bound_n = 4 if random.random() < 0.5 else 5
        target.bound_damage = 1/16

    if target_volatile_status == 'taunt':
        target.taunt_n = 3

    if target_volatile_status == 'encore':
        target.encore_n = 3
    
    return


def update_move_before_running(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> dex.Move:

    if move.id == 'beatup':
        power = 0
        #for pokemon in user.side.pokemon:
        #    power += (dex.pokedex[pokemon.id].baseStats.attack / 10) + 5
        move = move._replace(base_power = power)
    
    elif move.id == 'crushgrip' or move.id == 'wringout':
        power = math.floor(120 * (target.hp / target.maxhp))
        if power < 1:
            power = 1
        move = move._replace(base_power = power)

    elif move.id == 'electroball':
        power = 1
        speed = target.stats.speed / user.stats.speed
        if speed <= 0.25:
            power = 150
        if speed > 0.25:
            power = 120
        if speed > .3333:
            power = 80
        if speed > 0.5:
            power = 60
        if speed > 1:
            power = 40
        move = move._replace(base_power = power)

    elif move.id == 'eruption' or move.id == 'waterspout':
        power = math.floor(150 * (user.hp / user.maxhp))
        if power < 1:
            power = 1
        move = move._replace(base_power = power)

    elif move.id == 'flail' or move.id == 'reversal':
        power = 1
        hp = user.hp / user.maxhp
        if hp < 0.0417:
            power = 200
        if hp >= 0.0417:
            power = 150
        if hp > 0.1042:
            power = 100
        if hp > 0.2083:
            power = 80
        if hp > 0.3542:
            power = 40
        if hp >= 0.6875:
            power = 20
        move = move._replace(base_power = power)

    elif move.id == 'frustration' or move.id == 'return':
        move = move._replace(base_power = 102)

    elif move.id == 'grassknot':
        power = 1
        weight = dex.pokedex[target.species].weightkg
        if weight >= 200:
            power = 120
        if weight < 200:
            power = 100
        if weight < 100:
            power = 80
        if weight < 50:
            power = 60
        if weight < 25:
            power = 40
        if weight < 10:
            power = 20
        move = move._replace(base_power = power)

    elif move.id == 'heatcrash' or move.id == 'heavyslam':
        power = 1
        weight = dex.pokedex[target.id].weightkg / dex.pokedex[user.id].weightkg
        if weight > 0.5:
            power = 40
        if weight < 0.5:
            power = 60
        if weight < 0.333:
            power = 80
        if weight < 0.25:
            power = 100
        if weight < 0.20:
            power = 120
        move = move._replace(base_power = power)

    elif move.id == 'gyroball':
        target_player = (B.p1 if target.player_uid == 1 else B.p2)
        user_player = (B.p1 if user.player_uid == 1 else B.p2)
        power = math.floor(25 * (get_speed(target, B.weather, B.terrain, B.trickroom, target_player.tailwind) / get_speed(user, B.weather, B.terrain, B.trickroom, user_player.tailwind)))
        if power < 1:
            power = 1
        move = move._replace(base_power = power)

    elif move.id == 'magnitude':
        power = random.choice(dex.magnitude_power)
        move = move._replace(base_power = power)

    elif move.id == 'naturalgift':
        item = dex.item_dex[user.item]
        if item.isBerry:
            move = move._replace(base_power = item.naturalGift['basePower'])
            move = move._replace(type = item.naturalGift['type'])
    
    elif move.id == 'powertrip' or move.id == 'storedpower':
        power = 20
        for stat in user.boosts:
            if user.boosts[stat] > 0:
                power += (user.boosts[stat] * 20)
        move = move._replace(base_power = power)

    elif move.id == 'present':
        power = random.choice([0, 0, 120, 80, 80, 80, 40, 40, 40, 40])
        move = move._replace(base_power = power)

    elif move.id == 'punishment':
        power = 60
        for stat in target.boosts:
            if target.boosts[stat] > 0:
                power += (target.boosts[stat] * 20)
        if power > 200:
            power = 200
        move = move._replace(base_power = power)

    elif move.id == 'spitup':
        power = 100 * user.stockpile
        move = move._replace(base_power = power)
        user.stockpile = 0

    elif move.id == 'metronome':
        while move.id in dex.no_metronome:
            move = dex.move_dex[random.choice(list(dex.move_dex.keys()))]

    elif move.id == 'mimic' or move.id == 'assist':
        pass

    # copycat
    elif move.id == 'copycat':
        if target.last_used_move is not None:
            move = dex.move_dex[target.last_used_move]

    elif move.id == 'naturepower':
        move = dex.move_dex['triattack']

    # mirror move
    elif move.id == 'mirror move':
        if target.last_used_move is not None:
            move = dex.move_dex[target.last_used_move]

    # check non unique stuff
    # baneful bunker
    if 'banefulbunker' in target.volatile_statuses:
        if move.flags.contact:
            add_status(user, 'psn')

    # spiky shield
    if 'spikeyshield' in target.volatile_statuses:
        damage(user, 0.125, flag='percentmaxhp')

    # RECOIL DAMAGE
    if move.recoil.damage != 0:
        if move.recoil.condition == 'always':
            if move.recoil.type == 'maxhp':
                damage(user, move.recoil.damage, flag='percentmaxhp')
    return move


def unique_moves_after_damage(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon, dmg:int):

    #heal moves
    if move.heal > 0:
        damage(user, -(move.heal), flag='percentmaxhp')

    #heal moves that depend on weather
    if move.id in ['moonlight', 'morningsun', 'synthesis']:
        if B.weather == 'clear':
            damage(user, -(0.5), flag='percentmaxhp')
        elif B.weather == 'sunlight':
            damage(user, -(0.66), flag='percentmaxhp')
        else:
            damage(user, -(0.25), flag='percentmaxhp')
    if move.id == 'shoreup':
        if B.weather == 'sandstorm':
            damage(user, -(0.66), flag='percentmaxhp')
        else:
            damage(user, -(0.50), flag='percentmaxhp')

    #recoil moves
    if move.recoil.damage != 0:
        if move.recoil.condition == 'hit':
            if move.recoil.type == 'maxhp':
                damage(user, move.recoil.damage, flag='percentmaxhp')
            if move.recoil.type == 'damage':
                damage(user, dmg* move.recoil.damage)
    
    # terrain moves 
    if move.terrain is not None:
        B.terrain = move.terrain

    # weather moves
    if move.weather is not None and B.weather != move.weather:
        B.weather = move.weather
        B.weather_n = 5

    # accupressure
    if move.id == 'acupressure':
        possible_stats = [stat for stat in user.boosts if user.boosts[stat] < 6]
        if len(possible_stats) > 0:
            rand_int = random.randint(0, len(possible_stats)-1)
            boost_stat = possible_stats[rand_int]
            user.boosts[boost_stat] += 2
            if user.boosts[boost_stat] > 6:
                user.boosts[boost_stat] = 6

    # aqua ring
    if move.id == 'aquaring':
        user.aqua_ring = True

    # ingrain
    if move.id == 'ingrain':
        user.aqua_ring = True
        user.trapped = True

    # belly drum
    if move.id == 'bellydrum' and user.hp > (0.5 * user.maxhp):
        boost(user, {'atk': 6})
        damage(user, 0.5, flag='percentmax')

    # camouflage
    if move.id == 'camouflage':
        user.types = ['Normal']

    # conversion
    move_types = []
    if move.id == 'conversion':
        for user_move in user.moves:
            if dex.move_dex[user_move].type not in user.types:
                move_types.append(dex.move_dex[user_move].type)
        if len(move_types) > 0:
            user.types = [move_types[random.randint(0, len(move_types)-1)]]
