import requests
from bs4 import BeautifulSoup
import json

# Algorithm idea:
# for each list:
#   for each pokemon:
#       if card matches archetype:
#           return archetype name

tournamentUrls = [
    "http://files.rk9labs.com/decklists/20190223-Collinsville-TCG-Masters-Top-99-PHBRMUQA.html"
]

typeColors = {
    "fire": "rgba(244,67,54,.5)",
    "water": "rgba(3,169,244,.5)",
    "grass": "rgba(76,175,80,.5)",
    "electric": "rgba(255,193,7,.5)",
    "fighting": "rgba(255,87,34,.5)", 
    "psychic": "rgba(103,58,183,.5)", 
    "dark": "rgba(66,66,66,.5)",
    "metal": "rgba(96,125,139,.5)",
    "dragon": "rgba(130,119,23,.5)",
    "fairy": "rgba(233,30,99,.5)",
    "normal": "rgba(158,158,158,.5)"
}

archetypes = {
    "Blacephalon Naganadel": {
        "names": ["Blacephalon GX"],
        "type": "fire"
    },
    "Buzzwole Lucario": {
        "names": ["Buzzwole GX", "Lucario GX"],
        "type": "fighting"
    },
    "Celebi Venusaur": {
        "names": ["Celebi & Venusaur GX"],
        "type": "grass"
    },
    "Lapras Quagsire": {
        "names": ["Lapras GX", "Quagsire"],
        "type": "water"
    },

    # Malamar Variants
    "Ultra Malamar": {
        "names": ["Ultra Necrozma GX", "Malamar"],
        "type": "dragon"
    },
    "Malamar Spread": {
        "names": ["Malamar", "Tapu Koko"],
        "type": "psychic"
    },
    "Psychic Malamar": {
        "names": ["Malamar"],
        "type": "psychic"
    },

    # Lightning Variants
    "Pikachu Zekrom": {
        "names": ["Pikachu & Zekrom GX"],
        "type": "electric"
    },
    "Zapdos Jirachi": {
        "names": ["Zapdos", "Jirachi"],
        "type": "electric"
    },

    "Sylveon": {
        "names": ["Sylveon GX"],
        "type": "fairy"
    },
    "Umbreon Guzzlord": {
        "names": ["Umbreon", "Alolan Ninetales GX", "Guzzlord GX"],
        "type": "dark"
    },
    "Spread": {
        "names": ["Tapu Koko", "Tapu Lele"],
        "type": "electric"
    },
    "Vileplume": {
        "names": ["Vileplume"],
        "type": "grass"
    },

    # Zoroark Variants
    "Zororark Garbodor": {
        "names": ["Zoroark GX", "Garbodor"],
        "type": "dark"
    },
    "Zoroark Lucario Weavile": {
        "names": ["Zoroark GX", "Lucario GX", "Weavile"],
        "type": "dark"
    },
    "Zoroark Lycanroc Lucario": {
        "names": ["Zoroark GX", "Lycanroc GX", "Lucario GX"],
        "type": "dark"
    },
    "Zoroark Lycanroc": {
        "names": ["Zoroark GX", "Lycanroc GX"],
        "type": "dark"
    },
    "Zoroark Alolan Ninetales": {
        "names": ["Zoroark GX", "Alolan Ninetales GX"],
        "type": "dark"
    }
}

def formatName(name):
    n = name.split(" ")[0] + " " + name.split(" ")[1][0]
    return n.lower()

class Tournament:
    def __init__(self, url):
        self.url = url
        self.players = {}
        self.deckMatchups = {}
        self.deckCounts = {}

        self.getHtml()
        self.getTitle()
        self.getLists()
        self.destruct()

    def getHtml(self):
        response = requests.get(self.url)
        html = response.text
        self.soup = BeautifulSoup(html, 'html.parser')

    def getTitle(self):
        self.title = self.soup.findAll("title")[0].getText().split("RK9 Decklists of ")[1]

    def getLists(self):
        for listHtml in self.soup.findAll("table", {"class": "decklist"}):
            l = List(listHtml)
            self.players[formatName(l.player)] = l
            
            # Add a deck counter
            if l.archetype not in self.deckCounts:
                self.deckCounts[l.archetype] = 0
            self.deckCounts[l.archetype] += 1

            print("Got list for", l.player, "...")

        # Sort decks by deck count
        self.deckCounts = sorted(self.deckCounts.items(), key=lambda x: x[1], reverse=True)

    def fetchMatchups(self):
        for r in range(10, 19):
            print("Getting matchups for round ", str(r), "...")

            response = requests.get("https://player.rk9labs.com/pairings/BD96502A?round=" + str(r))
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            for match in soup.findAll("div", {"class": "match"}):
                for i in range(0, 2):
                    players = match.findAll("div", {"class": "player"})
                    player = players[i]
                    opponent = players[int(not i)]

                    if len(player.findAll("span")) > 0: # disregard invalid players
                        name = str(player.decode_contents()).split('name">')[1].split("<br/>")[0] + " " + str(player.decode_contents()).split('name">')[1].split("<br/>")[1].replace(" ", "").replace("\n", "")
                        
                        if len(opponent.findAll("span")) > 0: # make all invalid opponents byes
                            opponentName = str(opponent.decode_contents()).split('name">')[1].split("<br/>")[0] + " " + str(opponent.decode_contents()).split('name">')[1].split("<br/>")[1].replace(" ", "").replace("\n", "")
                        else:
                            opponentName = "bye"

                        if "winner" in str(player):
                            self.updateDeckMatchup(name, opponentName, "wins")
                        elif "loser" in str(player):
                            self.updateDeckMatchup(name, opponentName, "losses")
                        else:
                            self.updateDeckMatchup(name, opponentName, "ties")

        self.tidyUpMatchups()
        self.tidyUpSpecificMatchups()
        
    def updateDeckMatchup(self, name, opponentName, result):
        if formatName(name) in self.players: # if players haven't DROPPED on day two
            deck = self.players[formatName(name)].archetype

            if opponentName != "bye" and formatName(opponentName) in self.players:
                opponentDeck = self.players[formatName(opponentName)].archetype
            else:
                opponentDeck = "bye"

            if deck not in self.deckMatchups:
                self.deckMatchups[deck] = {}
                self.deckMatchups[deck]["wins"] = 0
                self.deckMatchups[deck]["losses"] = 0
                self.deckMatchups[deck]["ties"] = 0

            if opponentDeck not in self.deckMatchups[deck]:
                self.deckMatchups[deck][opponentDeck] = {}
                self.deckMatchups[deck][opponentDeck]["wins"] = 0
                self.deckMatchups[deck][opponentDeck]["ties"] = 0
                self.deckMatchups[deck][opponentDeck]["losses"] = 0

            self.deckMatchups[deck][result] += 1
            self.deckMatchups[deck][opponentDeck][result] += 1

    def tidyUpMatchups(self):
        print("Tidying matchups...")

        self.tidyMatchups = {}
        self.tidyMatchups["labels"] = []
        self.tidyMatchups["datasets"] = []
        self.tidyMatchups["datasets"].append({})
        self.tidyMatchups["datasets"][0]["label"] = self.title
        self.tidyMatchups["datasets"][0]["data"] = []
        self.tidyMatchups["datasets"][0]["backgroundColor"] = []
        for deck in self.deckCounts:
            self.tidyMatchups["labels"].append(deck[0])
            self.tidyMatchups["datasets"][0]["data"].append(deck[1])
            self.tidyMatchups["datasets"][0]["backgroundColor"].append(typeColors[archetypes[deck[0]]["type"]])
            # self.tidyMatchups["datasets"][0].data.append(str(deckStats["wins"]) + "-" + str(deckStats["ties"]) + "-" + str(deckStats["losses"]))
        self.export(self.title + ".json", self.tidyMatchups)

    def tidyUpSpecificMatchups(self):
        print("Tidying up specific matchups...")

        # exports the data template for the second graph
        self.tidySpecificMatchupsBase = {}
        self.tidySpecificMatchupsBase["labels"] = []
        self.tidySpecificMatchupsBase["datasets"] = []
        #self.tidySpecificMatchupsBase["datasets"].append({})
        #self.tidySpecificMatchupsBase["datasets"][0]["data"] = []

        for deck in self.deckCounts:
            self.tidySpecificMatchupsBase["labels"].append(deck[0])
        self.export(self.title + "_detailed.json", self.tidySpecificMatchupsBase)

        # now we work on the specifics
        self.specificTidyMatchups = {}
        self.specificTidyMatchups = {}
        self.specificTidyMatchups
        for deck in self.deckMatchups:
            self.specificTidyMatchups[deck] = {}

            for oppDeck in self.deckMatchups[deck]:
                if oppDeck != "wins" and oppDeck != "ties" and oppDeck != "losses":
                    stats = self.deckMatchups[deck][oppDeck]
                    winRatio = (stats["wins"] + 0.5 * stats["ties"]) / (stats["wins"] + stats["ties"] + stats["losses"])
                    self.specificTidyMatchups[deck][oppDeck] = winRatio
        self.export(self.title + "_detailed_data.json", self.specificTidyMatchups)


    def destruct(self):
        del self.soup

    def export(self, filename, data):
        print("Exporting " + filename + "...")
        file = open(filename, "+w")
        file.write(json.dumps(data, indent=4))


class List:
    def __init__(self, listHtml):
        self.listHtml = listHtml

        self.getPlayer()
        self.getStanding()
        self.getDeck()
        self.getArchetype()

    def getPlayer(self):
        self.player = self.listHtml.findAll("h4")[0].decode_contents().split(" <span")[0]

    def getStanding(self):
        self.standing = self.listHtml.findAll("span", {"class": "standing"})[0].getText().split("/")[0]

    def getDeck(self):
        self.pokemon = []
        self.trainers = []
        self.stadiums = []
        self.energies = []

        for pokemon in self.listHtml.findAll("li", {"class": "pokemon"}):
            self.pokemon.append(pokemon['data-cardname'])

        for trainer in self.listHtml.findAll("li", {"class": "trainer"}):
            self.trainers.append(trainer['data-cardname'])

        for stadium in self.listHtml.findAll("li", {"class": "stadium"}):
            self.stadiums.append(stadium['data-cardname'])

        for energy in self.listHtml.findAll("li", {"class": "energy"}):
            self.energies.append(energy['data-cardname'])

    def getArchetype(self):
        self.archetype = "none"

        for archetypeName, archetypeData in archetypes.items():
            archetypeBool = True
            for name in archetypeData["names"]:
                if name not in self.pokemon:
                    archetypeBool = False

            if archetypeBool:
                self.archetype = archetypeName
                break

def main():
    t = Tournament(tournamentUrls[0])
    t.fetchMatchups()

if __name__ == "__main__":
    main()