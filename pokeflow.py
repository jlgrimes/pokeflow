import sys
from scripts import import_tournaments, generate_meta_charts

def main():
    print("""Welcome to PokeFlow!
    Commands are as follows:
    import - fetch tournaments from RK9 into local .json files
    charts - generate HTML charts for use with pokeflow
    """)
    choice = ""
    if len(sys.argv) == 1:
        choice = input()
    else:
        choice = sys.argv[1]

    if choice == "import":
        import_tournaments.main()
    if choice == "charts":
        generate_meta_charts.main()
        

if __name__ == "__main__":
    main()