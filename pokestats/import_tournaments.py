import requests
import os
from bs4 import BeautifulSoup
import json


with open("./json/tournaments.json", "r") as tournamentsIn:
    tournaments = json.load(tournamentsIn)

with open("./json/type_colors.json") as typeColorsIn:
    typeColors = json.load(typeColorsIn)

with open("./json/archetypes/expanded_archetypes.json") as expandedArchetypesIn:
    expandedArchetypes = json.load(expandedArchetypesIn)

with open("./json/archetypes/standard_archetypes_2019_2020.json") as standardArchetypesIn:
    standardArchetypes = json.load(standardArchetypesIn)

# Algorithm idea:
# for each list:
#   for each pokemon:
#       if card matches archetype:
#           return archetype name

def formatName(name):
    n = name.split(" ")[0] + " "
    
    # Exception for double space..?
    if name.split(" ")[1] == "":
        n += name.split(" ")[2][0]
    else:
        n += name.split(" ")[1][0]
    return n.lower()

class Tournament:
    def __init__(self, tournamentObj):
        self.url = tournamentObj["listUrl"]
        self.pairingsUrl = tournamentObj["pairingsUrl"]
        self.dayTwoRounds = tournamentObj["dayTwoRounds"]
        
        if tournamentObj['format'] == "standard":
            self.archetypes = standardArchetypes
        if tournamentObj['format'] == "expanded":
            self.archetypes = expandedArchetypes

        # A dictionary of the form
        self.players = {}

        # A dictionary of the form
        #   "archetypeName": {
        #       "opponentDeck": {
        #           wins = x,
        #           ties = x,
        #           losses = x
        #       }
        #        ...
        #       wins = x,
        #       ties = x,
        #       losses = x
        #   }
        #   ...
        # Basically stores all of a particular archetype's matchups against every other archetype
        # Also stores the total wins/ties/losses against all archetypes
        # Used for displaying subresults in the line graph
        self.deckMatchups = {}

        # A dictionary of the form
        #   "archetypeName": count
        #    ...
        # Used for displaying ratios in the pie chart
        self.deckCounts = {}

        # Parses HTML for the page
        self.getHtml()

        # Gets the name of the tournament
        self.getTitle()

        # Stores all of the lists inside self
        self.getLists()

        # Cleans up a bit (probably not needed)
        self.destruct()

    def getHtml(self):
        # Pulls HTML from self.url and stores the result in self.soup
        response = requests.get(self.url)
        html = response.text
        self.soup = BeautifulSoup(html, 'html.parser')

    def getTitle(self):
        # Gets the tournament name from the soup of RK9
        self.title = self.soup.findAll("title")[0].getText().split("RK9 Decklists of ")[1]

    def getLists(self):
        # Iterate through all decklists on the page
        for listHtml in self.soup.findAll("table", {"class": "decklist"}):
            # Create a list of type List
            # List accepts HTML and parses it for useful information about the player/deck
            l = List(listHtml, self.archetypes)
            self.players[formatName(l.player)] = l.__dict__
            
            # Add whatever the person's playing to the deckCounts variable
            if l.archetype not in self.deckCounts:
                self.deckCounts[l.archetype] = 0
            self.deckCounts[l.archetype] += 1

            print("Got list for", l.player, "...")

        # Sort archetypes by deck count, highest number of decks first
        self.deckCounts = sorted(self.deckCounts.items(), key=lambda x: x[1], reverse=True)

    def fetchMatchups(self):
        # Iterates through day two rounds 10-19
        for r in range(self.dayTwoRounds[0], self.dayTwoRounds[1]):
            print("Getting matchups for round ", str(r), "...")

            # Gets the HTML from the specific round page
            response = requests.get(self.pairingsUrl + str(r))
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # For each match in round r
            for match in soup.findAll("div", {"class": "match"}):
                # For each player in the match
                for i in range(0, 2):
                    # Get the player HTMLs from the page
                    players = match.findAll("div", {"class": "player"})
                    player = players[i]
                    opponent = players[int(not i)]

                    if len(player.findAll("span")) > 0: # disregard invalid players
                        # Gets the player's name from the weird HTML
                        name = str(player.decode_contents()).split('name">')[1].split("<br/>")[0] + " " + str(player.decode_contents()).split('name">')[1].split("<br/>")[1].replace(" ", "").replace("\n", "")
                        
                        if len(opponent.findAll("span")) > 0: # make all invalid opponents byes
                            # Gets the opponent's name from the weird HTML
                            opponentName = str(opponent.decode_contents()).split('name">')[1].split("<br/>")[0] + " " + str(opponent.decode_contents()).split('name">')[1].split("<br/>")[1].replace(" ", "").replace("\n", "")
                        else:
                            # If the opponent has no data, we assume it's a bye.
                            opponentName = "bye"

                        # Update deckMatchups based off of the player's result
                        if "winner" in str(player) and "winner" not in str(opponent):
                            self.updateDeckMatchup(name, opponentName, "wins")
                        elif "loser" in str(player):
                            self.updateDeckMatchup(name, opponentName, "losses")
                        else:
                            self.updateDeckMatchup(name, opponentName, "ties")

    def updateDeckCounts(self):
        for deckName, deckCount in self.deckCounts:
            if deckName not in self.deckMatchups:
                self.deckMatchups[deckName] = {}
            self.deckMatchups[deckName]["count"] = deckCount
                
        
    def updateDeckMatchup(self, name, opponentName, result):
        if formatName(name) in self.players: # if players haven't DROPPED on day two
            # Get the deck that player is playing
            deck = self.players[formatName(name)]["archetype"]

            if opponentName != "bye" and formatName(opponentName) in self.players: # omits byes and invvalid players
                # Sets opponentDeck to whatever the opponent is playing
                opponentDeck = self.players[formatName(opponentName)]["archetype"]
            else:
                opponentDeck = "bye"

            # If player's deck isn't in our matchups list, we initialize it
            if deck not in self.deckMatchups:
                self.deckMatchups[deck] = {}
                self.deckMatchups[deck]["wins"] = 0
                self.deckMatchups[deck]["losses"] = 0
                self.deckMatchups[deck]["ties"] = 0

            # If opponent's deck isn't in our sublist (matchups[deck]), we initialize it
            if opponentDeck not in self.deckMatchups[deck]:
                self.deckMatchups[deck][opponentDeck] = {}
                self.deckMatchups[deck][opponentDeck]["wins"] = 0
                self.deckMatchups[deck][opponentDeck]["ties"] = 0
                self.deckMatchups[deck][opponentDeck]["losses"] = 0

            # Add one to the deck's TOTAL wins/ties/losses
            self.deckMatchups[deck][result] += 1

            # We add one to both the player's deck result and the opponent's deck result
            # This may look like double counting, but it's needed
            # Example: if Zapdos plays against Maalamar and wins, we add one to both Zapdos' wins and Malamar's losses.
            self.deckMatchups[deck][opponentDeck][result] += 1

    def destruct(self):
        del self.soup

    def export(self, filename, data):
        print("Exporting " + filename + "...")
        file = open("./json/tournaments/" + filename, "w")
        file.write(json.dumps(data, indent=4))

class List:
    def __init__(self, listHtml, archetypes):
        self.listHtml = listHtml
        self.archetypes = archetypes

        self.getPlayer()
        self.getStanding()
        self.getDeck()
        self.getArchetype()
        self.destruct()

    def getPlayer(self):
        self.player = self.listHtml.findAll("h4")[0].decode_contents().split(" <span")[0]

    def getStanding(self):
        self.standing = self.listHtml.findAll("span", {"class": "standing"})[0].getText().split("/")[0]

    def getDeck(self):
        self.pokemon = {}
        self.trainers = {}
        self.energies = {}

        for pokemon in self.listHtml.findAll("li", {"class": "pokemon"}):
            self.pokemon[pokemon['data-cardname']] = int(pokemon['data-quantity'])

        for trainer in self.listHtml.findAll("li", {"class": "trainer"}):
            self.trainers[trainer['data-cardname']] = int(trainer['data-quantity'])

        for energy in self.listHtml.findAll("li", {"class": "energy"}):
            self.energies[energy['data-cardname']] = int(energy['data-quantity'])

    def getArchetype(self):
        self.archetype = "none"

        for archetypeName, archetypeData in self.archetypes.items():
            archetypeBool = True
            for card in archetypeData["names"]:
                if type(card) == str:
                    if card not in self.pokemon:
                        archetypeBool = False
                else:
                    for name, count in card.items():
                        if name not in self.pokemon:
                            archetypeBool = False
                        else:
                            if int(self.pokemon[name]) < int(count):
                                archetypeBool = False
                        

            if archetypeBool:
                self.archetype = archetypeName
                break

        if self.archetype == "none":
            raise Exception("Deck not found for:", self.pokemon)

    def destruct(self):
        # Clean up a little ;)
        del self.listHtml
        del self.archetypes

deck_data = {
    "standard": {},
    "expanded": {}
}

def updateDeckData(data, tournament, name, year):
    totalFilename = year + "_" + tournament['format'] + ".json"
    totalFile = open("./json/decks/" + totalFilename, "w+")

    filename = year + "_" + name + ".json"
    file = open("./json/decks/" + filename, "w+")

    temp_deck_data = data

    # Updates ONE TOURNAMENT into the deck_data global
    if not deck_data[tournament['format']]:
        deck_data[tournament['format']] = data
    else:
        for deck in data:
            if deck in deck_data[tournament['format']]:
                # Check specific matchups
                for subDeck in data[deck]:
                    # If sub matchup is already in there and it's a valid deck
                    if subDeck in deck_data[tournament['format']][deck] and subDeck != "wins" and subDeck != "ties" and subDeck != "losses" and subDeck != "count":
                        # Update specific deck matchups
                        deck_data[tournament['format']][deck][subDeck]['losses'] += data[deck][subDeck]['losses']
                        deck_data[tournament['format']][deck][subDeck]['ties'] += data[deck][subDeck]['ties']
                        deck_data[tournament['format']][deck][subDeck]['wins'] += data[deck][subDeck]['wins']

                # Update the sum deck matchups
                deck_data[tournament['format']][deck]['losses'] += data[deck]['losses']
                deck_data[tournament['format']][deck]['ties'] += data[deck]['ties']
                deck_data[tournament['format']][deck]['wins'] += data[deck]['wins']


            # If an archetype isn't in the base struct add it in
            else:
                deck_data[tournament['format']][deck] = data[deck]
                temp_deck_data[tournament['format']][deck] = data[deck]

    # Override the file every time just to be safe!
    file.write(json.dumps(temp_deck_data, indent=4))
    totalFile.write(json.dumps(data, indent=4))

    print(filename, "dumped!")

def main(flags):
    for year, tournamentsInYear in tournaments.items():
        for tournamentName, tournamentData in tournamentsInYear.items():
            filename = year + "_" + tournamentName + ".json"
            if "-o" not in flags and os.path.isfile("./json/tournaments/" + filename):
                print(filename, "already exists! Skipping...")
            else:
                t = Tournament(tournamentData)
                t.fetchMatchups()
                t.updateDeckCounts()
                t.export(filename, t.players)
                updateDeckData(t.deckMatchups, tournamentData, tournamentName, year)
            
    print("done!")

if __name__ == "__main__":
    main("")
