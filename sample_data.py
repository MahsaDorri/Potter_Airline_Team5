"""
This is starter sample data for the project, it lives in the Python code but automatically writes itself out to a CSV too,
So it's easy to read in code and just as easy to edit in Excel, which makes it simpler to plug into the database class down the line.

"""
import csv
import logging
import os

from flight import Flight

logger = logging.getLogger(__name__)

QUOTE_DATE_STR = "2026-09-15"  # "today" for the whole project, keeps things reproducible

CSV_PATH = os.path.join(os.path.dirname(__file__), "flights.csv")
CSV_COLUMNS = [
    "flight_id", "origin", "destination", "departure_date",
    "base_fare", "seats_remaining", "capacity", "route_popularity",
]

_RAW_FLIGHTS = [
    # flight_id, origin,  destination,  departure_date, base_fare, seats, capacity, popularity
    ("PA2001", "London", "Hogsmeade", "2026-09-22", 135.0, 18, 120, 0.91),
    ("PA2002", "London", "Edinburgh", "2026-10-19", 92.0, 70, 120, 0.72),
    ("PA2003", "Manchester", "Diagon Alley", "2026-09-17", 96.0, 8, 90, 0.69),
    ("PA2004", "Toronto", "Hogsmeade", "2026-09-20", 110.0, 60, 100, 0.80),
    ("PA2005", "London", "Paris", "2026-10-05", 150.0, 100, 150, 0.85),
    ("PA2006", "New York", "Hogsmeade", "2026-12-24", 220.0, 15, 180, 0.95),
    ("PA2007", "London", "Diagon Alley", "2027-06-27", 140.0, 30, 130, 0.88),
    ("PA2008", "Toronto", "Paris", "2027-01-14", 175.0, 140, 160, 0.55),
    ("PA2009", "Manchester", "Edinburgh", "2026-11-08", 60.0, 45, 80, 0.40),
    ("PA2010", "London", "Hogsmeade", "2027-02-02", 135.0, 100, 120, 0.60),
    ("PA2011", "London", "Hogsmeade", "2026-09-18", 145.0, 10, 100, 0.88),
    ("PA2012", "London", "Diagon Alley", "2026-09-20", 70.0, 68, 80, 0.55),
    ("PA2013", "London", "Edinburgh", "2026-09-22", 160.0, 56, 140, 0.77),
    ("PA2014", "London", "Paris", "2026-09-24", 95.0, 60, 100, 0.62),
    ("PA2015", "Manchester", "Diagon Alley", "2026-09-27", 130.0, 30, 120, 0.83),
    ("PA2016", "Manchester", "Edinburgh", "2026-09-30", 85.0, 72, 90, 0.45),
    ("PA2017", "Manchester", "Hogsmeade", "2026-10-03", 175.0, 68, 150, 0.70),
    ("PA2018", "Toronto", "Hogsmeade", "2026-10-06", 105.0, 70, 100, 0.50),
    ("PA2019", "Toronto", "Paris", "2026-10-13", 120.0, 42, 120, 0.80),
    ("PA2020", "Toronto", "Diagon Alley", "2026-10-20", 68.0, 72, 80, 0.42),
    ("PA2021", "New York", "Hogsmeade", "2026-10-25", 155.0, 20, 130, 0.91),
    ("PA2022", "New York", "London", "2026-11-14", 100.0, 50, 100, 0.60),
    ("PA2023", "Dublin", "Hogsmeade", "2026-11-29", 90.0, 58, 90, 0.58),
    ("PA2024", "Glasgow", "Diagon Alley", "2026-12-19", 210.0, 144, 180, 0.65),
    ("PA2025", "Bristol", "Paris", "2026-12-24", 125.0, 66, 120, 0.72),
    ("PA2026", "London", "Hogsmeade", "2026-12-20", 230.0, 45, 150, 0.94),
    ("PA2027", "London", "Diagon Alley", "2027-01-18", 60.0, 90, 100, 0.38),
    ("PA2028", "London", "Edinburgh", "2026-11-14", 75.0, 36, 80, 0.50),
    ("PA2029", "London", "Paris", "2027-01-03", 150.0, 52, 130, 0.85),
    ("PA2030", "Manchester", "Diagon Alley", "2027-01-13", 110.0, 60, 100, 0.66),
    ("PA2031", "Manchester", "Edinburgh", "2027-02-12", 82.0, 68, 90, 0.48),
    ("PA2032", "Manchester", "Hogsmeade", "2027-03-14", 170.0, 24, 120, 0.89),
    ("PA2033", "Toronto", "Hogsmeade", "2027-04-03", 95.0, 128, 150, 0.55),
    ("PA2034", "Toronto", "Paris", "2027-05-03", 135.0, 35, 100, 0.75),
    ("PA2035", "Toronto", "Diagon Alley", "2027-06-02", 78.0, 56, 80, 0.60),
    ("PA2036", "New York", "Hogsmeade", "2027-07-02", 140.0, 65, 130, 0.70),
    ("PA2037", "New York", "London", "2027-07-12", 200.0, 10, 100, 0.93),
    ("PA2038", "Dublin", "Hogsmeade", "2027-08-01", 88.0, 72, 90, 0.45),
    ("PA2039", "Glasgow", "Diagon Alley", "2027-08-21", 165.0, 60, 150, 0.80),
    ("PA2040", "Bristol", "Paris", "2027-09-10", 100.0, 65, 100, 0.58),
]


# no csv yet; just write everything out

def _sync_csv_with_raw(csv_path=CSV_PATH):
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
            writer.writerows(_RAW_FLIGHTS)
        logger.info(f"made {csv_path} with {len(_RAW_FLIGHTS)} flights")
        return

    # csv already exists -> only add flights that aren't in it yet,
    # so we don't overwrite anything someone edited by hand
    with open(csv_path, newline="", encoding="utf-8") as f:
        existing_ids = {row["flight_id"] for row in csv.DictReader(f)}

    new_rows = [row for row in _RAW_FLIGHTS if row[0] not in existing_ids]
    if not new_rows:
        logger.debug(f"{csv_path} already has everything, nothing to add")
        return

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)
    logger.info(f"added {len(new_rows)} new flight(s) to {csv_path}")


def build_sample_flights(csv_path=CSV_PATH):
    _sync_csv_with_raw(csv_path)

    flights = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            flights.append(Flight(
                flight_id=row["flight_id"],
                origin=row["origin"],
                destination=row["destination"],
                departure_date=row["departure_date"],
                base_fare=float(row["base_fare"]),
                seats_remaining=int(row["seats_remaining"]),
                capacity=int(row["capacity"]),
                route_popularity=float(row["route_popularity"]),
            ))

    logger.debug(f"loaded {len(flights)} flights from {csv_path}")
    return flights
