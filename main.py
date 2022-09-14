def stats():
    from standings.england_standings import engStandings
    from standings.spain_standings import espStandings
    england = engStandings()
    spain = espStandings()

    return england.table()

if __name__ == "__main__":
    stats()