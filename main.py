from logging_config import setup_logging

setup_logging()
import database
from flight import Flight
from sample_data import build_sample_flights

if __name__ == '__main__':
    f = Flight("PA1001", "London", "Hogsmeade", "2026-09-22", 135, 18, 120, 0.91)
    f.update_seats(-5)
    print(f)
    print("Load factor:", f.load_factor())
    flights = build_sample_flights()
    # Flights object

    conn = database.connect()
    database.create_table(conn, reset=True)
    database.insert_many(conn, flights)
    print(f"inserted {len(flights)} flights into potter_airlines.db")

    # ---- SELECT * FROM flights ----
    cursor = conn.execute("SELECT * FROM flights")
    all_rows = cursor.fetchall()
    print("total in db:", len(all_rows))

    # ---- SELECT * FROM flights WHERE destination = ? ----
    cursor = conn.execute("SELECT flight_id FROM flights WHERE destination = ?", ("Hogsmeade",))
    hogsmeade_ids = [row[0] for row in cursor.fetchall()]
    print("flights to Hogsmeade:", hogsmeade_ids)

    # ---- UPDATE flights SET seats_remaining = ? WHERE flight_id = ? ----
    conn.execute("UPDATE flights SET seats_remaining = ? WHERE flight_id = ?", (5, "PA2001"))
    conn.commit()

    cursor = conn.execute("SELECT seats_remaining FROM flights WHERE flight_id = ?", ("PA2001",))
    print("PA2001 seats now:", cursor.fetchone()[0])

    # ---- DELETE FROM flights WHERE flight_id = ? ----
    conn.execute("DELETE FROM flights WHERE flight_id = ?", ("PA2040",))
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM flights")
    print("remaining after delete:", cursor.fetchone()[0])

    conn.close()
