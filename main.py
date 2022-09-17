def stats():
    from standings import Standings
    england = Standings()

    return england.drop(), england.table()

if __name__ == "__main__":
    stats()