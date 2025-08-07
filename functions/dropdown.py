def show_devmode():
    return ["sandbox", "production"]

def show_begdate():
    return [f"{year}-{month:02d}-{day:02d}" for year in range(2020, 2026) for month in range(1, 13) for day in range(1, 32)]

def show_enddate():
    return [f"{year}-{month:02d}-{day:02d}" for year in range(2020, 2026) for month in range(1, 13) for day in range(1, 32)]
