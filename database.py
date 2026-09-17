# database.py
# Task 3 - SQLite database, owners: Fouzan & Mahsa
#
# stores flights in a sqlite database and does insert, select, update, delete
# always use ? placeholders in the SQL, never put values directly in the string

import logging
import sqlite3

from flight import Flight

logger = logging.getLogger(__name__)

DB_PATH = "potter_airlines.db"

CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS flights (
        flight_id TEXT PRIMARY KEY,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_date TEXT NOT NULL,
        base_fare REAL NOT NULL CHECK (base_fare >= 0),
        seats_remaining INTEGER NOT NULL,
        capacity INTEGER NOT NULL CHECK (capacity > 0),
        route_popularity REAL NOT NULL CHECK (route_popularity BETWEEN 0 AND 1),
        CHECK (seats_remaining BETWEEN 0 AND capacity)
    )
"""


def connect(db_path=DB_PATH):
    # opens (or creates) the sqlite file and gives back the connection
    return sqlite3.connect(db_path)


def create_table(conn, reset=False):
    if reset:
        conn.execute("DROP TABLE IF EXISTS flights")
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    logger.debug(f"table ready (reset={reset})")


def insert_flight(conn, flight):
    d = flight.to_dict()
    conn.execute(
        "INSERT OR REPLACE INTO flights VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (d["flight_id"], d["origin"], d["destination"], d["departure_date"],
         d["base_fare"], d["seats_remaining"], d["capacity"], d["route_popularity"]),
    )
    conn.commit()
    logger.info(f"added flight {flight.flight_id} to db")


def insert_many(conn, flights):
    for f in flights:
        insert_flight(conn, f)


def get_all_flights(conn):
    cursor = conn.execute("SELECT * FROM flights")
    rows = cursor.fetchall()

    flights = []
    for row in rows:
        flight_id, origin, destination, departure_date, base_fare, seats_remaining, capacity, route_popularity = row
        flights.append(Flight(flight_id, origin, destination, departure_date,
                               base_fare, seats_remaining, capacity, route_popularity))
    return flights


def get_flights_by_destination(conn, destination):
    # using ? here instead of putting destination straight in the string
    cursor = conn.execute("SELECT * FROM flights WHERE destination = ?", (destination,))
    rows = cursor.fetchall()

    flights = []
    for row in rows:
        flight_id, origin, destination, departure_date, base_fare, seats_remaining, capacity, route_popularity = row
        flights.append(Flight(flight_id, origin, destination, departure_date,
                               base_fare, seats_remaining, capacity, route_popularity))
    return flights


def get_flight(conn, flight_id):
    cursor = conn.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,))
    row = cursor.fetchone()
    if row is None:
        return None

    flight_id, origin, destination, departure_date, base_fare, seats_remaining, capacity, route_popularity = row
    return Flight(flight_id, origin, destination, departure_date,
                  base_fare, seats_remaining, capacity, route_popularity)


def update_seats(conn, flight_id, new_seats_remaining):
    cursor = conn.execute(
        "UPDATE flights SET seats_remaining = ? WHERE flight_id = ?",
        (new_seats_remaining, flight_id),
    )
    conn.commit()
    logger.info(f"updated seats for {flight_id} to {new_seats_remaining} (rows changed: {cursor.rowcount})")
    return cursor.rowcount


def delete_flight(conn, flight_id):
    cursor = conn.execute("DELETE FROM flights WHERE flight_id = ?", (flight_id,))
    conn.commit()
    logger.info(f"deleted flight {flight_id} (rows removed: {cursor.rowcount})")
    return cursor.rowcount
