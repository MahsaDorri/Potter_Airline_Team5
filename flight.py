"""
The Flight class is the first step in defining this project. Using
OOP, we define a constructor that creates Flight objects representing
different flights, each of which is already pre-validated at the
moment it is created -- so no invalid flight can ever exist in the
system.
"""

from datetime import date, datetime  # used to store departure dates as real date objects, not plain strings
import logging

logger = logging.getLogger(__name__)


class Flight:
    # represents one scheduled flight: route, dates, seats, price info.
    # __init__ makes sure these are always true for every Flight:
    #   0 <= seats_remaining <= capacity
    #   capacity > 0
    #   0 <= route_popularity <= 1

    def __init__(self, flight_id, origin, destination, departure_date,
                 base_fare, seats_remaining, capacity, route_popularity):
        # check everything before saving it, so Invalid Flight can never be created.
        if capacity <= 0:
            logger.error(f"capacity has to be > 0, got {capacity} for flight {flight_id}")
            raise ValueError("capacity must be greater than 0")
        if not (0 <= seats_remaining <= capacity):
            logger.error(f"seats_remaining ({seats_remaining}) is outside 0..{capacity} for flight {flight_id}")
            raise ValueError("seats_remaining must be between 0 and capacity")
        if base_fare < 0:
            logger.error(f"base_fare can't be negative, got {base_fare} for flight {flight_id}")
            raise ValueError("base_fare must be nonnegative")
        if not (0 <= route_popularity <= 1):
            logger.error(f"route_popularity ({route_popularity}) should be between 0 and 1, flight {flight_id}")
            raise ValueError("route_popularity must be between 0 and 1")

        self.flight_id = flight_id
        self.origin = origin
        self.destination = destination
        self.departure_date = self._parse_date(departure_date)
        self.base_fare = float(base_fare)
        self.seats_remaining = int(seats_remaining)
        self.capacity = int(capacity)
        self.route_popularity = float(route_popularity)

        logger.debug(f"made flight {self.flight_id}: {self.origin} -> {self.destination},"
                     f" {self.seats_remaining}/{self.capacity} seats left")

    @staticmethod
    def _parse_date(value):
        # turn the date string into an actual date object (or just return it if already one)

        if isinstance(value, date):
            return value
        return datetime.strptime(value, "%Y-%m-%d").date()

    def days_until_departure(self, reference_date=None):
        # how many days from reference_date (default today) until departure
        reference_date = reference_date or date.today()
        return (self.departure_date - reference_date).days

    def load_factor(self):
        # how full the flight is, 0 = empty, 1 = full. just reads data, doesn't change anything
        return 1 - self.seats_remaining / self.capacity

    def update_seats(self, change):
        # sell seats (negative change) or add them back (positive change)
        # only place allowed to touch seats_remaining directly
        new_value = self.seats_remaining + change
        if not (0 <= new_value <= self.capacity):
            logger.warning(f"can't change seats for {self.flight_id} by {change}, "
                           f"that would give {new_value} (capacity is {self.capacity})")
            raise ValueError("seat update is outside 0 capacity")
        logger.info(f"flight {self.flight_id} seats: {self.seats_remaining} -> {new_value}")
        self.seats_remaining = new_value

    def to_dict(self):
        # turn this Flight into a plain dict, so it can be saved to json/sqlite
        d = vars(self).copy()
        d["departure_date"] = self.departure_date.isoformat()  # dates need to be strings for json/sqlite
        return d

    @classmethod
    def from_dict(cls, data):
        # rebuild a Flight from a dict made by to_dict()
        # goes through __init__ again so validation still runs
        return cls(
            flight_id=data["flight_id"],
            origin=data["origin"],
            destination=data["destination"],
            departure_date=data["departure_date"],
            base_fare=data["base_fare"],
            seats_remaining=data["seats_remaining"],
            capacity=data["capacity"],
            route_popularity=data["route_popularity"],
        )

    def __repr__(self):
        # makes print(flight) show something readable instead of a memory address
        return (f"Flight({self.flight_id}, {self.origin}->{self.destination}, "
                f"{self.departure_date.isoformat()})")

