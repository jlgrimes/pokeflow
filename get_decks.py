import requests
from bs4 import BeautifulSoup

# Algorithm idea:
# for each list:
#   for each pokemon:
#       if card matches archetype:
#           return archetype name

tournamentUrls = [
    "http://files.rk9labs.com/decklists/20190223-Collinsville-TCG-Masters-Top-99-PHBRMUQA.html"
]

archetypes = [
    ["Blacephalon GX"],
    ["Buzzwole GX", "Lucario GX"],
    ["Celebi & Venusaur GX"],
    ["Lapras GX", "Quagsire"],

    # Malamar Variants
    ["Ultra Necrozma GX", "Malamar"],
    ["Malamar", "Tapu Koko"],
    ["Malamar"],

    # Lightning Variants
    ["Pikachu & Zekrom GX"],
    ["Zapdos", "Jirachi"],

    ["Sylveon GX"],
    ["Umbreon", "Alolan Ninetales GX"],
    ["Tapu Koko", "Magcargo"],
    ["Vileplume"],

    # Zoroark Variants
    ["Zoroark GX", "Garbodor"],
    ["Zoroark GX", "Lucario GX", "Weavile"],
    ["Zoroark GX", "Lycanroc GX", "Lucario GX"],
    ["Zoroark GX", "Lycanroc GX"],
    ["Zoroark GX", "Alolan Ninetales GX"]
]

def formatName(name):
    n = name.split(" ")[0] + " " + name.split(" ")[1][0]
    return n.lower()

class Tournament:
    def __init__(self, url):
        self.url = url
        self.players = {}
        self.deckMatchups = {}

        self.getHtml()
        self.getTitle()
        self.getLists()
        self.fetchMatchups()
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
            print("Got list for", l.player, "...")

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

    def destruct(self):
        del self.soup


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

        for archetype in archetypes:
            archetypeBool = True
            for name in archetype:
                if name not in self.pokemon:
                    archetypeBool = False

            if archetypeBool:
                self.archetype = " ".join(archetype)
                break

def main():
    t = Tournament(tournamentUrls[0])

if __name__ == "__main__":
    main()