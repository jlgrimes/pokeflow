import json

jsonPath = "rk9/sample_data.json"
htmlOutPath = "rk9/out.html"
chartWidth = 80
chartHeight = 60

htmlHead = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.js"></script>
<div class="chart-container" style="position: relative; height:""" + str(chartHeight) + """vh; width:""" + str(chartWidth) +  """vw">
<canvas id="myChart" width="100" height="100"></canvas>
</div>
<script>
var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: 
"""
htmlMiddle = """
, datasets: [
"""

htmlEnd = """
        ]
    },
    options: {
        scales: {
            xAxes: [{
                stacked: true
            }],
            yAxes: [{
                stacked: true,
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
});
</script>
"""

def parent(deckName):
    if "zoroark gx" in deckName.lower() and "greninja & zoroark gx" not in deckName.lower():
        return "Zoroark GX"
    if "reshiram & charizard" in deckName.lower():
        return "Reshiram & Charizard"
    if "malamar" in deckName.lower():
        return "Malamar"
    if "zapdos" in deckName.lower():
        return "Zapdos"
    if "stall" in deckName.lower():
        return "Stall"
    
    return ""

def init(data):
    with open(jsonPath, "r") as f:
        dataIn = json.load(f)

    for deckName, deckCount in dataIn.items():
        if deckCount != 0:
            if parent(deckName) != "":
                if parent(deckName) not in data:
                    data[parent(deckName)] = {}
                data[parent(deckName)][deckName] = deckCount
            else:
                data[deckName] = deckCount

def returnParentCount(elemValue):
    if type(elemValue) is not dict:
        return elemValue
    sum = 0
    for key, val in elemValue.items():
        sum += val 
    return sum

def createDataSet(parentName):
    return    """
    {
    label: " """ + parentName + """ ",
    data: 
    """

def childData(elemValue, ctr):
    htmlData = [0] * 100
    htmlData[ctr] = elemValue
    return htmlData

def appendToDataSet(dataSet, key, val, ctr):
    dataSet += createDataSet(key)
    dataSet += str(childData(val, ctr))
    dataSet += "},"
    return dataSet

def main():
    data = {}
    init(data)

    parentLabels = []
    parentData = []
    dataSet = ""
    ctr = 0

    for key, val in sorted(data.items(), key=lambda x: returnParentCount(x[1]), reverse=True):
        parentLabels.append(key)

        if type(val) == int:
            dataSet = appendToDataSet(dataSet, key, val, ctr)
        else:
            for childKey, childValue in val.items():
                dataSet = appendToDataSet(dataSet, childKey, childValue, ctr)
        # parentData.append(val)
        ctr += 1
        #break

    dataSet = dataSet[:-1]
    print(parentLabels)
    print(parentData)

    with open(htmlOutPath, "w+") as f:
        f.write(htmlHead + str(parentLabels) + htmlMiddle + dataSet + htmlEnd)


if __name__ == "__main__":
    main()