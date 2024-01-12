import simulator as sim
from select_pokemon import create_team 

teams = []

for i in range(2):
    teams.append(create_team(1))

battle = sim.Battle('single', 'prueba', teams[0],'prueba2', teams[1], debug = True)

print(battle.p1.pokemon)