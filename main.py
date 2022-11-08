from config import c, a
import os

os.environ[c]=a

def stats():
    # Importing classes from src files.
    from src.location import Location
    from src.players import Players
    from src.standings import Standings

    location = Location()
    players = Players()
    standings = Standings()
    
    # Dropping and loading the standings and players dataframes.
    return standings.drop(), standings.load(), players.drop(), players.load()

if __name__ == "__main__":
    stats()