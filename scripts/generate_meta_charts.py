# NOT WORKING

import json
import pokeflow_vars

# Algorithm idea:
# for each list:
#   for each pokemon:
#       if card matches archetype:
#           return archetype name

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

def tidyUpSpecificMatchups(self):
    print("Tidying up specific matchups...")

    # Exports the data template for the expanded graph
    self.tidySpecificMatchupsBase = {}
    self.tidySpecificMatchupsBase["labels"] = []
    self.tidySpecificMatchupsBase["datasets"] = []

    for deck in self.deckCounts:
        self.tidySpecificMatchupsBase["labels"].append(deck[0])

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

def mergeChartHtml(self):
    print("Merging into index.html...")
    file = open("index.html", "+w")
    file.write(
    """<b><span style="font-size: large;"><u>Day 2 Meta Spread</u></span></b><br />
    <br />
    <script type="text/javascript" src="http://code.jquery.com/jquery-2.0.2.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.4.0/Chart.min.js"></script>
    <script type="text/javascript">
    var decks =
    """ + 
    json.dumps(self.specificTidyMatchups, indent=4) +
    """
    var data = """ +
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

def main():
    for yearName, year in pokeflow_vars.tournaments.items():
        for tournament in year.items():
            deckFilename = yearName + "_" + tournament.format + ".json"

            with open("./json/tournaments/" + deckFilename, "r") as tournamentIn:
                tournament = json.load(tournamentIn)
            

    mergeChartHtml()
    print("done!")

if __name__ == "__main__":
    main()
