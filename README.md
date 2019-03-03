# PokeFlow

A radical new framework for how tournament results are managed.

## Data Structures

The main difference from PokeFlow and any statistics compiling site is the use of these data structures. All data will be compressed into JSON files, which is easily accessible from both Python and Javascript. This allows for code to take over the job of a person, and to compile deck lists via functions.

### Raw Tournament Structure

This is what will be generated for each tournament. PokeFlow pulls from RK9labs to extract data for tournaments.

```
{
    "tournament":{
        "metadata": {
            "location": "location",
            "date": "date",
        }
        "day-two": {
            "players": {
                "player name": {
                    "player": {
                        "name": "player name",
                        "id": "player id"
                    }
                    "deck": {
                        "name": "name of deck",
                        "list-url": "deck list url"
                    }
                    "record": {
                        "wins": 15,
                        "ties": 0,
                        "losses": 0
                    }
                    "cp-earned": 500
                }
                ...
            }
        }
    }
    ...
}
```

### Extracted Deck Structure

```
{
    "deck name": {
        "total-stats": {
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "cp-earned": 0
        }
        "tournaments" {
            "tournament name": {
                "day-two": {
                    "stats": {
                        "wins": 0,
                        "ties": 0,
                        "losses": 0,
                        "cp-earned": 0
                    }
                    "players": [
                        "someone",
                        "someone else"
                    ]
                }
            }
            ...
        }
    }
    ...
}
```

## Current Issues
* Counts dropped players as byes. Since players' decks are grabbed from RK9 final standings, dropped players aren't accounted for.