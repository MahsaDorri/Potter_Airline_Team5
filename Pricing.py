from flight import Flight
from datetime import date

def time_factor(days_until_departure):
    if days_until_departure < 0:
        raise ValueError("departure date is in the past")
    elif days_until_departure <= 7:
        time_factor = 1.35
    elif 8 <= days_until_departure <= 21:
        time_factor = 1.10
    else:
        time_factor = 1.00
    return time_factor

def capacity_factor(seats_remaining, capacity):
    load_factor = 1 - seats_remaining / capacity
    return 1 + 0.45 * load_factor

def demand_factor(route_popularity):
    return 0.9 + 0.3 * route_popularity

def weekend_factor(departure_date):
    if departure_date.weekday() in [4, 5]:  # Friday or Saturday
        return 1.1
    else:
        return 1.00
    
def seasonal_factor(departure_date):
    month = departure_date.month
    if month in [6, 7, 8]:  # Summer
        return 1.2
    elif month in [11, 12]:  # Holiday season
        return 1.15
    else:
        return 1.0
    
def calculate_price(flight: Flight, reference_date=None):
    reference_date = reference_date or date.today()
    days_until_departure = flight.days_until_departure(reference_date)
    time_factor_value = time_factor(days_until_departure)
    capacity_factor_value = capacity_factor(flight.seats_remaining, flight.capacity)
    demand_factor_value = demand_factor(flight.route_popularity)
    weekend_factor_value = weekend_factor(flight.departure_date)
    seasonal_factor_value = seasonal_factor(flight.departure_date)

    price = (flight.base_fare *
             time_factor_value *
             capacity_factor_value *
             demand_factor_value *
             weekend_factor_value *
             seasonal_factor_value)

# set a min and max price bondary to avoid extreme values for different class types

    
    print(f"Calculated price for flight {flight.flight_id}: {round(price, 2)} (base fare: {flight.base_fare}, "
          f"time factor: {time_factor_value}, capacity factor: {capacity_factor_value}, "
          f"demand factor: {demand_factor_value}, weekend factor: {weekend_factor_value}, "
          f"seasonal factor: {seasonal_factor_value})")

#Test the price calculation with a sample flight
flight = Flight(
        flight_id="PA101",
        origin="Toronto",
        destination="Vancouver",
        departure_date="2026-07-10",
        base_fare=200,
        seats_remaining=20,
        capacity=100,
        route_popularity=0.8
    )

