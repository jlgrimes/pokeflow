import sys
from scripts import import_tournaments, generate_meta_charts

def main():
    print("""Welcome to PokeFlow!
    Commands are as follows:
    import - fetch tournaments from RK9 into local .json files
    charts - generate HTML charts for use with pokeflow""")
    choice = ""
    args = []

    if len(sys.argv) == 1:
        inny = input()
        args = inny.split(" ")
        choice = args[0]
    else:
        args = sys.argv
        choice = sys.argv[1]

    if choice == "import":
        import_tournaments.main(args)
    if choice == "charts":
        generate_meta_charts.main()
        

if __name__ == "__main__":
    main()