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

class Tournament:
    def __init__(self, url):
        self.url = url
        self.players = []

        self.getHtml()
        self.getTitle()
        self.getLists()

    def getHtml(self):
        response = requests.get(self.url)
        html = response.text
        self.soup = BeautifulSoup(html, 'html.parser')

    def getTitle(self):
        self.title = self.soup.findAll("title")[0].getText().split("RK9 Decklists of ")[1]

    def getLists(self):
        for listHtml in self.soup.findAll("table", {"class": "decklist"}):
            self.players.append(List(listHtml))


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