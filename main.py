def stats():
    from england_standings import Standings
    standings = Standings()

    return standings.table(), standings.graph()

if __name__ == "__main__":
    stats()