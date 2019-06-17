import json

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

def main():
    with open("rk9/sample_data.json", "r") as f:
        dataIn = json.load(f)

    data = {}

    for deckName, deckCount in dataIn.items():
        if deckCount != 0:
            if parent(deckName) != "":
                if parent(deckName) not in data:
                    data[parent(deckName)] = {}
                data[parent(deckName)][deckName] = deckCount
            else:
                data[deckName] = deckCount

    print("hi!")


if __name__ == "__main__":
    main()