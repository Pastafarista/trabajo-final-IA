import simulator as sim
from select_pokemon import create_team
from select_pokemon import create_team_2

teams = []

#Funcion de alex con equipos aleatorios
for i in range(2):
    teams.append(create_team_2(1))

#Funcion de Antonio con pokemons determinados
team_1 = create_team(["aurorus"])
team_2 = create_team(["ambipom"])

battle1 = sim.Battle('single', 'prueba', team_1,'prueba2', team_2, debug = True)
battle2 = sim.Battle('single', 'prueba', teams[0],'prueba2', teams[1], debug = True)

#Simulamos peleas
sim.run(battle1)
print("=============================")
sim.run(battle2)
