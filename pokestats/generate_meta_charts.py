import os
import json

# Algorithm idea:
# for each list:
#   for each pokemon:
#       if card matches archetype:
#           return archetype name

with open("./json/tournaments.json", "r") as tournamentsIn:
    tournaments = json.load(tournamentsIn)

with open("./json/type_colors.json") as typeColorsIn:
    typeColors = json.load(typeColorsIn)

with open("./json/archetypes/expanded_archetypes.json") as expandedArchetypesIn:
    expandedArchetypes = json.load(expandedArchetypesIn)

with open("./json/archetypes/standard_archetypes_2019_2020.json") as standardArchetypesIn:
    standardArchetypes = json.load(standardArchetypesIn)


tidyMatchups = {}
tidySpecificMatchupsBase = {}
specificTidyMatchups = {}

def count(deck):
    return deck["count"]

def tidyUpMatchups(tournament, decks):
    print("Tidying matchups...")

    # Get archetypes
    archetypes = {}
    if tournament["format"] == "standard":
        archetypes = standardArchetypes
    if tournament["format"] == "expanded":
        archetypes = expandedArchetypes

    # Initialize the data structure, per chart.js's standards :)
    tidyMatchups["labels"] = []
    tidyMatchups["datasets"] = []
    tidyMatchups["datasets"].append({})
    tidyMatchups["datasets"][0]["label"] = ""
    tidyMatchups["datasets"][0]["data"] = []
    tidyMatchups["datasets"][0]["backgroundColor"] = []

    # Iterate through all decks
    # Here we're adding all of the deck counts to the pie chart json
    for deckName, deck in sorted(decks.items(), key=lambda x: x[1]["count"], reverse=True):
        # Add deck to pie chart label
        tidyMatchups["labels"].append(deckName)

        # Add each deck's count to the data
        tidyMatchups["datasets"][0]["data"].append(count(deck))

        # Get the color for each deck and add it to backgroundColor array
        tidyMatchups["datasets"][0]["backgroundColor"].append(typeColors[archetypes[deckName]["type"]])

def tidyUpSpecificMatchups(decks):
    print("Tidying up specific matchups...")

    # Exports the data template for the expanded graph
    tidySpecificMatchupsBase["labels"] = []
    tidySpecificMatchupsBase["datasets"] = []

    for deckName, deck in decks.items():
        tidySpecificMatchupsBase["labels"].append(deckName)

    # now we work on the specifics
    for deck in decks:
        specificTidyMatchups[deck] = {}

        for oppDeck in decks[deck]:
            if oppDeck != "wins" and oppDeck != "ties" and oppDeck != "losses" and oppDeck != "count":
                stats = decks[deck][oppDeck]
                winRatio = (stats["wins"] + 0.5 * stats["ties"]) / (stats["wins"] + stats["ties"] + stats["losses"])
                specificTidyMatchups[deck][oppDeck] = winRatio

def mergeChartHtml(tournament, year, filename):
    print("Merging into index.html...")
    file = open("./charts/" + filename, "+w")
    file.write(
    """<b><span style="font-size: large;"><u>Day 2 Meta Spread</u></span></b><br />
    <br />
    <script type="text/javascript" src="http://code.jquery.com/jquery-2.0.2.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.4.0/Chart.min.js"></script>
    <script type="text/javascript">
    var decks =
    """ + 
    json.dumps(specificTidyMatchups, indent=4) +
    """
    var data = """ +
    json.dumps(tidyMatchups) +
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
    json.dumps(tidySpecificMatchupsBase) +
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
    for yearName, year in tournaments.items():
        for tournamentName, tournamentData in year.items():
            filename = yearName + "_" + tournamentName + ".html"

            if os.path.isfile("./charts/" + filename):
                print(filename, "already exists! Skipping...")
            else:
                deckFilename = yearName + "_" + tournamentData["format"] + ".json"
                with open("./json/decks/" + deckFilename, "r") as tournamentDecksIn:
                    tournamentDecks = json.load(tournamentDecksIn)

                tidyUpMatchups(tournamentData, tournamentDecks)
                tidyUpSpecificMatchups(tournamentDecks)
                mergeChartHtml(tournamentName, yearName, filename)
    print("done!")

if __name__ == "__main__":
    main()
