from config import c, a
import os

os.environ[c]=a

def stats():
    from src.standings import Standings
    from src.location import Location
    standings = Standings()
    location = Location()

    return standings.drop(), standings.load()

if __name__ == "__main__":
    stats()