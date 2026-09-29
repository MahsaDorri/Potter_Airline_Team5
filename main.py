from logging_config import setup_logging

setup_logging()

import database
from flight import Flight
from sample_data import build_sample_flights
from analysis import (
    load_flights_dataframe,
    add_pricing_factors,
    get_top_priced_flights,
    summarize_by_destination,
)


if __name__ == '__main__':
    f = Flight(
        "PA1001",
        "London",
        "Hogsmeade",
        "2026-09-22",
        135,
        18,
        120,
        0.91
    )

    f.update_seats(-5)
    print(f)
    print("Load factor:", f.load_factor())

    flights = build_sample_flights()

    # ---- CREATE / INSERT ----
    conn = database.connect()
    database.create_table(conn, reset=True)
    database.insert_many(conn, flights)

    print(f"inserted {len(flights)} flights into potter_airlines.db")

    # ---- SELECT * FROM flights ----
    cursor = conn.execute("SELECT * FROM flights")
    all_rows = cursor.fetchall()

    print("total in db:", len(all_rows))

    # ---- SELECT flights by destination ----
    cursor = conn.execute(
        "SELECT flight_id FROM flights WHERE destination = ?",
        ("Hogsmeade",)
    )

    hogsmeade_ids = [row[0] for row in cursor.fetchall()]

    print("flights to Hogsmeade:", hogsmeade_ids)

    # ---- UPDATE seats remaining ----
    conn.execute(
        "UPDATE flights SET seats_remaining = ? WHERE flight_id = ?",
        (5, "PA2001")
    )
    conn.commit()

    cursor = conn.execute(
        "SELECT seats_remaining FROM flights WHERE flight_id = ?",
        ("PA2001",)
    )

    print("PA2001 seats now:", cursor.fetchone()[0])

    # ---- DELETE flight ----
    conn.execute(
        "DELETE FROM flights WHERE flight_id = ?",
        ("PA2040",)
    )
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM flights")

    print("remaining after delete:", cursor.fetchone()[0])

    # ---- PANDAS / NUMPY ANALYSIS ----
    df = load_flights_dataframe(conn)
    df = add_pricing_factors(df)

    print("\nTop 5 highest-priced flights:")

    top_flights = get_top_priced_flights(df)

    print(
        top_flights[
            ["flight_id", "origin", "destination", "final_price"]
        ]
    )

    print("\nDestination summary:")

    destination_summary = summarize_by_destination(df)

    print(destination_summary)

        # ---- ERROR HANDLING DEMONSTRATION ----
    try:
        invalid_flight = Flight(
            "TEST",
            "London",
            "Paris",
            "2026-10-10",
            100,
            150,
            120,
            0.5
        )
    except ValueError as error:
        print("\nValidation handled successfully:")
        print(error)

    conn.close()