print("------Process starting------")

def stats():
    # Importing classes from src files.
    from src.locations import Locations
    from src.players import Players
    from src.standings import Standings
    from src.teams import Teams

    locations = Locations()
    players = Players()
    standings = Standings()
    teams = Teams()
    
    # Dropping and loading the standings and players dataframes.
    return locations.drop(), locations.load(), players.drop(), players.load(), standings.drop(), standings.load(), teams.drop(), teams.load()

if __name__ == "__main__":
    stats()