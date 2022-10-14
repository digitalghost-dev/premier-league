from config import a, f
import os

os.environ[a]=f

def stats():
    from src.standings import Standings
    from location import Location
    england = Standings()
    location = Location()

    return england.drop(), england.table()

if __name__ == "__main__":
    stats()