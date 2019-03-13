import requests
from bs4 import BeautifulSoup
import json
import pokeflow

# Algorithm idea:
# for each list:
#   for each pokemon:
#       if card matches archetype:
#           return archetype name

def formatName(name):
    n = name.split(" ")[0] + " " + name.split(" ")[1][0]
    return n.lower()

class Tournament:
    def __init__(self, tournamentObj):
        self.url = tournamentObj["listUrl"]
        self.pairingsUrl = tournamentObj["pairingsUrl"]
        self.dayTwoRounds = tournamentObj["dayTwoRounds"]
        
        if tournamentObj["format"] == "standard":
            self.archetypes = pokeflow.standardArchetypes
        if tournamentObj["format"] == "expanded":
            self.archetypes = pokeflow.expandedArchetypes

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
            self.players[formatName(l.player)] = l
            
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

        # Renders an output for chart.js of the matchup data
        self.tidyUpMatchups()

        # Renders an output for chart.js of the matchup vs matchup data
        self.tidyUpSpecificMatchups()
        
    def updateDeckMatchup(self, name, opponentName, result):
        if formatName(name) in self.players: # if players haven't DROPPED on day two
            # Get the deck that player is playing
            deck = self.players[formatName(name)].archetype

            if opponentName != "bye" and formatName(opponentName) in self.players: # omits byes and invvalid players
                # Sets opponentDeck to whatever the opponent is playing
                opponentDeck = self.players[formatName(opponentName)].archetype
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

    def tidyUpMatchups(self):
        print("Tidying matchups...")

        # Initialize the data structure, per chart.js's standards :)
        self.tidyMatchups = {}
        self.tidyMatchups["labels"] = []
        self.tidyMatchups["datasets"] = []
        self.tidyMatchups["datasets"].append({})
        self.tidyMatchups["datasets"][0]["label"] = self.title
        self.tidyMatchups["datasets"][0]["data"] = []
        self.tidyMatchups["datasets"][0]["backgroundColor"] = []

        # Iterate through all decks
        # Here we're adding all of the deck counts to the pie chart json
        for deck in self.deckCounts:
            # Add deck to pie chart label
            self.tidyMatchups["labels"].append(deck[0])

            # Add each deck's card count to the data
            self.tidyMatchups["datasets"][0]["data"].append(deck[1])

            # Get the color for each deck and add it to backgroundColor array
            self.tidyMatchups["datasets"][0]["backgroundColor"].append(pokeflow.typeColors[self.archetypes[deck[0]]["type"]])
            # self.tidyMatchups["datasets"][0].data.append(str(deckStats["wins"]) + "-" + str(deckStats["ties"]) + "-" + str(deckStats["losses"]))
        # self.export(self.title + ".json", self.tidyMatchups)

    def tidyUpSpecificMatchups(self):
        print("Tidying up specific matchups...")

        # Exports the data template for the expanded graph
        self.tidySpecificMatchupsBase = {}
        self.tidySpecificMatchupsBase["labels"] = []
        self.tidySpecificMatchupsBase["datasets"] = []
        #self.tidySpecificMatchupsBase["datasets"].append({})
        #self.tidySpecificMatchupsBase["datasets"][0]["data"] = []

        for deck in self.deckCounts:
            self.tidySpecificMatchupsBase["labels"].append(deck[0])
        # self.export(self.title + " labels line chart.json", self.tidySpecificMatchupsBase)

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
        # self.export(self.title + " matchups line chart.json", self.specificTidyMatchups)


    def destruct(self):
        del self.soup

    def export(self, filename, data):
        print("Exporting " + filename + "...")
        file = open(filename, "+w")
        file.write(json.dumps(data, indent=4))

    def mergeChartHtml(self):
        print("Merging into index.html...")
        file = open("index.html", "+w")
        file.write("""
        <b><span style="font-size: large;"><u>Day 2 Meta Spread</u></span></b><br />
        <br />
        <script type="text/javascript" src="http://code.jquery.com/jquery-2.0.2.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.4.0/Chart.min.js"></script>
        <script type="text/javascript">
        var decks =
        """ + 
        json.dumps(self.specificTidyMatchups, indent=4) +
        """
        var data =""" +
        json.dumps(self.tidyMatchups) +
        """
        $(document).ready( 
            function () {
                var ctx = $("#deckDistribution");
                var myNewChart = new Chart(ctx,{
                        type: 'pie',
                        data: data
                    });  
                    
                var ctx2 = $("#detailedMatchups");
                var detailed = new Chart(ctx2, {
                    type: 'line',
                    data: 
        """ +
        json.dumps(self.tidySpecificMatchupsBase) +
        """
                            ,
                    options: {
                        scales: {
                            xAxes: [{
                                ticks: {
                                    maxTicksLimit: 100,
                                    autoSkip: false
                                }
                            }]
                        }
                    }
                    })

                    $("#deckDistribution").click( 
                        function(evt){
                            var activeElement = myNewChart.getElementsAtEvent(evt);
                            var clickedData = data.datasets[activeElement[0]._datasetIndex].data[activeElement[0]._index];
                            var clickedLabel = data.labels[activeElement[0]._index];
                            var clickedColor = data.datasets[activeElement[0]._datasetIndex].backgroundColor[activeElement[0]._index];
                            //alert(clickedLabel);

                            var repeat = false;
                            var i = 0;
                            
                            for(var d = 0; d < detailed.data.datasets.length; d++) {
                                if (detailed.data.datasets[d]["label"] == clickedLabel){
                                    repeat = true;
                                    i = d;
                                }
                            }

                            if (repeat) {
                                detailed.data.datasets.splice(i, 1);
                                detailed.update();
                            }
                            else {
                                var temp_dataset = {};
                                temp_dataset["data"] = [];
                                temp_dataset["label"] = clickedLabel;
                                temp_dataset["backgroundColor"] = clickedColor;

                                for (var d in decks[clickedLabel]) {
                                    // iterate through labels
                                    for (var i = 0; i < detailed.data.labels.length; i++) {
                                        temp_dataset["data"].push(decks[clickedLabel][detailed.data.labels[i]])
                                    }
                                }

                                detailed.data.datasets.push(temp_dataset)
                                detailed.update();
                            }
                            
                            //detailed.data.labels.push("four");
                            //detailed.data.datasets[0]["data"].push(3);
                            //detailed.update();
                        }
                    );    
                }
            );
        </script>
        <div class="chart-container" style="height:500; width:500">
            <canvas id="deckDistribution"></canvas>
        </div>
        <div class="chart-container" style="height:500; width:1000">
            <canvas id="detailedMatchups"></canvas>
        </div>
        """
        )

class List:
    def __init__(self, listHtml, archetypes):
        self.listHtml = listHtml
        self.archetypes = archetypes

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

        for archetypeName, archetypeData in self.archetypes.items():
            archetypeBool = True
            for name in archetypeData["names"]:
                if name not in self.pokemon:
                    archetypeBool = False

            if archetypeBool:
                self.archetype = archetypeName
                break

def main():
    t = Tournament(pokeflow.tournaments["2019"]["Toronto"])
    t.fetchMatchups()
    t.mergeChartHtml()
    print("done!")

if __name__ == "__main__":
    main()
