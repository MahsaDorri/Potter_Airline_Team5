import os
from datetime import datetime

import database
from flight import Flight
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

    # Display sold-out flights clearly.
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


# ==================================================
# Test 3: Edge Case Tests
# Checks important validation and boundary cases.
# ==================================================

print("\n--- Edge Case Tests ---\n")


# --------------------------------------------------
# Edge Case 1: Capacity cannot be zero.
# --------------------------------------------------

try:
    Flight(
        "TEST001",
        "Toronto",
        "Paris",
        "2026-10-10",
        100,
        50,
        0,
        0.7
    )

    print("FAIL: capacity = 0 was accepted")

except ValueError:
    print("PASS: capacity = 0 correctly raises ValueError")


# --------------------------------------------------
# Edge Case 2: Seats remaining cannot exceed capacity.
# --------------------------------------------------

try:
    Flight(
        "TEST002",
        "Toronto",
        "Paris",
        "2026-10-10",
        100,
        150,
        120,
        0.7
    )

    print("FAIL: seats_remaining > capacity was accepted")

except ValueError:
    print(
        "PASS: seats_remaining > capacity "
        "correctly raises ValueError"
    )


# --------------------------------------------------
# Edge Case 3: Base fare cannot be negative.
# --------------------------------------------------

try:
    Flight(
        "TEST003",
        "Toronto",
        "Paris",
        "2026-10-10",
        -100,
        50,
        120,
        0.7
    )

    print("FAIL: negative base fare was accepted")

except ValueError:
    print(
        "PASS: negative base fare "
        "correctly raises ValueError"
    )


# --------------------------------------------------
# Edge Case 4: Route popularity must be between 0 and 1.
# --------------------------------------------------

try:
    Flight(
        "TEST004",
        "Toronto",
        "Paris",
        "2026-10-10",
        100,
        50,
        120,
        1.5
    )

    print("FAIL: invalid route popularity was accepted")

except ValueError:
    print(
        "PASS: invalid route popularity "
        "correctly raises ValueError"
    )


# --------------------------------------------------
# Edge Case 5: Departure date cannot be in the past.
# --------------------------------------------------

past_flight = Flight(
    "TEST005",
    "Toronto",
    "Paris",
    "2026-09-10",
    100,
    50,
    120,
    0.7
)

try:
    calculate_price(
        past_flight,
        reference_date=reference_date
    )

    print("FAIL: past departure date was accepted")

except ValueError:
    print(
        "PASS: past departure date "
        "correctly raises ValueError"
    )


# --------------------------------------------------
# Edge Case 6: Sold-out flight should not return a fare.
# --------------------------------------------------

sold_out_flight = Flight(
    "TEST006",
    "Toronto",
    "Paris",
    "2026-10-10",
    100,
    0,
    120,
    0.7
)

sold_out_price = calculate_price(
    sold_out_flight,
    reference_date=reference_date
)

if sold_out_price is None:
    print(
        "PASS: sold-out flight correctly "
        "returns no purchasable fare"
    )
else:
    print(
        "FAIL: sold-out flight returned "
        f"${sold_out_price:.2f}"
    )


# --------------------------------------------------
# Edge Case 7: Seat update cannot oversell a flight.
# --------------------------------------------------

seat_test_flight = Flight(
    "TEST007",
    "Toronto",
    "Paris",
    "2026-10-10",
    100,
    5,
    120,
    0.7
)

try:
    seat_test_flight.update_seats(-10)

    print("FAIL: overselling seats was accepted")

except ValueError:
    print(
        "PASS: overselling seats "
        "correctly raises ValueError"
    )