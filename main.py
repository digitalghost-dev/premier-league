from config import a, f
import os

os.environ[a]=f

def stats():
    from src.standings import Standings
    england = Standings()

    return england.drop(), england.table()

if __name__ == "__main__":
    stats()