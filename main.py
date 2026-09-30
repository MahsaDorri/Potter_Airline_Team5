from logging_config import setup_logging

# Set up logging before importing the rest of the project modules.
setup_logging()

from datetime import datetime

import database
from flight import Flight
from sample_data import build_sample_flights, QUOTE_DATE_STR
from Pricing import calculate_price
from analysis import (
    load_flights_dataframe,
    add_pricing_factors,
    get_top_priced_flights,
    summarize_by_destination,
    plot_average_price_by_destination,
)


if __name__ == "__main__":

    # ==================================================
    # 1. FLIGHT CLASS DEMONSTRATION
    # ==================================================

    print("\n--- Flight Class Demonstration ---\n")

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

    # Demonstrate updating seats through the Flight class.
    f.update_seats(-5)

    print(f)
    print("Load factor:", round(f.load_factor(), 2))


    # ==================================================
    # 2. LOAD SAMPLE FLIGHT DATA
    # ==================================================

    flights = build_sample_flights()

    print(
        f"\nLoaded {len(flights)} flights "
        f"from the project dataset."
    )


    # ==================================================
    # 3. SQLITE DATABASE SETUP
    # ==================================================

    conn = database.connect()

    # Reset the table so every run begins with
    # the same reproducible dataset.
    database.create_table(
        conn,
        reset=True
    )

    database.insert_many(
        conn,
        flights
    )

    print(
        f"Inserted {len(flights)} flights "
        f"into potter_airlines.db"
    )


    # ==================================================
    # 4. DATABASE SELECT
    # ==================================================

    all_flights = database.get_all_flights(conn)

    print(
        "\nTotal flights in database:",
        len(all_flights)
    )

    # Find flights travelling to Hogsmeade.
    hogsmeade_flights = database.get_flights_by_destination(
        conn,
        "Hogsmeade"
    )

    hogsmeade_ids = [
        flight.flight_id
        for flight in hogsmeade_flights
    ]

    print(
        "Flights to Hogsmeade:",
        hogsmeade_ids
    )


    # ==================================================
    # 5. DATABASE UPDATE
    # ==================================================

    database.update_seats(
        conn,
        "PA2001",
        5
    )

    updated_flight = database.get_flight(
        conn,
        "PA2001"
    )

    print(
        "PA2001 seats now:",
        updated_flight.seats_remaining
    )


    # ==================================================
    # 6. DATABASE DELETE
    # ==================================================

    database.delete_flight(
        conn,
        "PA2040"
    )

    remaining_flights = database.get_all_flights(conn)

    print(
        "Remaining after delete:",
        len(remaining_flights)
    )


    # ==================================================
    # 7. DYNAMIC PRICING
    # ==================================================

    print("\n--- Dynamic Pricing ---\n")

    # Use the project's fixed quote date so the pricing
    # results remain reproducible across different runs.
    reference_date = datetime.strptime(
        QUOTE_DATE_STR,
        "%Y-%m-%d"
    ).date()

    # Get the current flights from the database.
    current_flights = database.get_all_flights(conn)

    # Calculate and display a dynamic price
    # for each currently available flight.
    for flight in current_flights:

        final_price = calculate_price(
            flight,
            reference_date=reference_date
        )

        if final_price is None:
            price_display = "Sold Out"
        else:
            price_display = f"${final_price:.2f}"

        print(
            f"{flight.flight_id}: "
            f"{flight.origin} -> "
            f"{flight.destination} | "
            f"Base fare: ${flight.base_fare:.2f} | "
            f"Dynamic price: {price_display}"
        )


    # ==================================================
    # 8. PANDAS / NUMPY ANALYSIS
    # ==================================================

    print("\n--- Pandas / NumPy Analysis ---\n")

    # Load the current SQLite data into a DataFrame.
    df = load_flights_dataframe(conn)

    # Apply vectorized dynamic pricing calculations.
    df = add_pricing_factors(df)


    # --------------------------------------------------
    # Highest-priced available flights
    # --------------------------------------------------

    print("Top 5 highest-priced available flights:")

    top_flights = get_top_priced_flights(
        df
    )

    print(
        top_flights[
            [
                "flight_id",
                "origin",
                "destination",
                "final_price"
            ]
        ]
    )


    # --------------------------------------------------
    # Destination-level summary
    # --------------------------------------------------

    print("\nDestination summary:")

    destination_summary = summarize_by_destination(
        df
    )

    print(destination_summary)


    # --------------------------------------------------
    # Visualization
    # --------------------------------------------------

    print("\nDisplaying average dynamic price by destination graph...")

    plot_average_price_by_destination(
        destination_summary
    )


    # ==================================================
    # 9. ERROR HANDLING DEMONSTRATION
    # ==================================================

    print("\n--- Error Handling Demonstration ---\n")

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

        print(
            "Validation handled successfully:"
        )

        print(error)


    # ==================================================
    # 10. CLOSE DATABASE CONNECTION
    # ==================================================

    conn.close()

    print(
        "\nPotter Airlines workflow completed successfully."
    )