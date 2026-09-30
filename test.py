import os
from datetime import datetime

import database
from sample_data import build_sample_flights, QUOTE_DATE_STR
from Pricing import (
    time_factor,
    capacity_factor,
    demand_factor,
    weekend_factor,
    seasonal_factor,
    calculate_price,
)


# Show the database location.
print("db will be at:", os.path.abspath(database.DB_PATH))


# Use the project's fixed quote date so test results are reproducible.
reference_date = datetime.strptime(
    QUOTE_DATE_STR,
    "%Y-%m-%d"
).date()


# Load all existing project flights.
flights = build_sample_flights()


# ==================================================
# Test 1: Simple Pricing Test
# Shows the base fare and final calculated price
# for every flight in the existing project data.
# ==================================================

print("\n--- Simple Pricing Test ---\n")

for flight in flights:
    final_price = calculate_price(
        flight,
        reference_date=reference_date
    )

    # Display sold-out flights clearly instead of formatting None as a number.
    if final_price is None:
        price_display = "Sold Out"
    else:
        price_display = f"${final_price:.2f}"

    print(
        f"{flight.flight_id}: "
        f"{flight.origin} -> {flight.destination} | "
        f"Base fare: ${flight.base_fare:.2f} | "
        f"Final price: {price_display}"
    )


# ==================================================
# Test 2: Full Pricing Breakdown Test
# Shows every pricing factor used to calculate
# the final fare for each flight.
# ==================================================

print("\n--- Full Pricing Breakdown Test ---\n")

for flight in flights:

    # Calculate days until departure.
    days_until_departure = flight.days_until_departure(
        reference_date
    )

    # Calculate each active pricing factor.
    time_factor_value = time_factor(
        days_until_departure
    )

    capacity_factor_value = capacity_factor(
        flight.seats_remaining,
        flight.capacity
    )

    demand_factor_value = demand_factor(
        flight.route_popularity
    )

    weekend_factor_value = weekend_factor(
        flight.departure_date
    )

    seasonal_factor_value = seasonal_factor(
        flight.departure_date
    )

    # Calculate the raw price before fare boundaries are applied.
    raw_price = (
        flight.base_fare
        * time_factor_value
        * capacity_factor_value
        * demand_factor_value
        * weekend_factor_value
        * seasonal_factor_value
    )

    # Calculate the final bounded price using
    # the main pricing function.
    final_price = calculate_price(
        flight,
        reference_date=reference_date
    )

    # ----------------------------------------------
    # Display flight information.
    # ----------------------------------------------

    print(f"Flight: {flight.flight_id}")

    print(
        f"Route: {flight.origin} -> "
        f"{flight.destination}"
    )

    print(
        f"Departure date: "
        f"{flight.departure_date}"
    )

    print(
        f"Days until departure: "
        f"{days_until_departure}"
    )

    # ----------------------------------------------
    # Display original flight inputs.
    # ----------------------------------------------

    print(
        f"Base fare: "
        f"${flight.base_fare:.2f}"
    )

    print(
        f"Seats remaining: "
        f"{flight.seats_remaining}/"
        f"{flight.capacity}"
    )

    print(
        f"Load factor: "
        f"{flight.load_factor():.2f}"
    )

    print(
        f"Route popularity: "
        f"{flight.route_popularity:.2f}"
    )

    # ----------------------------------------------
    # Display pricing factors.
    # ----------------------------------------------

    print(
        f"Time factor: "
        f"{time_factor_value:.2f}"
    )

    print(
        f"Capacity factor: "
        f"{capacity_factor_value:.2f}"
    )

    print(
        f"Demand factor: "
        f"{demand_factor_value:.2f}"
    )

    print(
        f"Weekend factor: "
        f"{weekend_factor_value:.2f}"
    )

    print(
        f"Seasonal factor: "
        f"{seasonal_factor_value:.2f}"
    )

    # ----------------------------------------------
    # Display pricing results.
    # ----------------------------------------------

    print(
        f"Raw price: "
        f"${raw_price:.2f}"
    )

    if final_price is None:
        print("Final price: Sold Out")
    else:
        print(
            f"Final price: "
            f"${final_price:.2f}"
        )

    print("-" * 50)