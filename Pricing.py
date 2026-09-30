from flight import Flight
from datetime import date


# Calculates a time-based pricing multiplier.
def time_factor(days_until_departure):
    # Increase the fare as the departure date gets closer.
    # Last-minute bookings receive the highest urgency multiplier.
    if days_until_departure < 0:
        raise ValueError("Departure date is in the past.")
    elif days_until_departure <= 7:
        return 1.35
    elif days_until_departure <= 21:
        return 1.10
    else:
        return 1.00


# Calculates a capacity-based pricing multiplier.
def capacity_factor(seats_remaining, capacity):
    # Increase the fare as the flight becomes fuller.
    # Fewer remaining seats indicate greater scarcity and a higher load factor.
    load_factor = 1 - seats_remaining / capacity
    return 1 + 0.45 * load_factor


# Calculates a demand-based pricing multiplier.
def demand_factor(route_popularity):
    # Adjust the fare based on how popular the route is.
    # More popular routes receive a higher demand multiplier.
    return 0.9 + 0.3 * route_popularity


# Calculates a weekend-based pricing multiplier.
def weekend_factor(departure_date):
    # Apply a higher fare for Friday through Sunday travel.
    # Weekend travel is assumed to have higher demand than weekdays.
    if departure_date.weekday() in [4, 5, 6]:
        return 1.10
    else:
        return 1.00


# Calculates a seasonal pricing multiplier.
def seasonal_factor(departure_date):
    # Apply a higher fare during peak travel seasons.
    # Summer and year-end holiday periods are assumed to have stronger demand.
    month = departure_date.month

    if month in [6, 7, 8]:
        return 1.20
    elif month in [11, 12]:
        return 1.15
    else:
        return 1.00


# Calculates the final dynamic fare for a single Flight object.
def calculate_price(flight: Flight, reference_date=None):

    # A sold-out flight has no available fare.
    if flight.seats_remaining == 0:
        return None

    # Use today's date by default to calculate how close the flight is to departure.
    reference_date = reference_date or date.today()

    # Calculate the number of days remaining before departure.
    days_until_departure = flight.days_until_departure(reference_date)

    # Calculate each pricing factor separately so the final fare is easy to explain.
    time_factor_value = time_factor(days_until_departure)

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

    # Combine the base fare with all pricing multipliers.
    raw_price = (
        flight.base_fare
        * time_factor_value
        * capacity_factor_value
        * demand_factor_value
        * weekend_factor_value
        * seasonal_factor_value
    )

    # Keep the final fare within a reasonable price range.
    min_fare = 45
    max_fare = 1500

    final_price = max(
        min_fare,
        min(raw_price, max_fare)
    )

    return round(final_price, 2)