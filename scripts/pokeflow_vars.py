import json

with open("./json/tournaments.json", "r") as tournamentsIn:
    tournaments = json.load(tournamentsIn)

with open("./json/type_colors.json") as typeColorsIn:
    typeColors = json.load(typeColorsIn)

with open("./json/expanded_archetypes.json") as expandedArchetypesIn:
    expandedArchetypes = json.load(expandedArchetypesIn)

with open("./json/standard_archetypes.json") as standardArchetypesIn:
    standardArchetypes = json.load(standardArchetypesIn)