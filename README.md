# Potter Airlines 
## Flight Class, Dataset, Dynamic Pricing & Database

This covers Task 1 (Flight class + flight dataset) and Task 3 (SQLite
database), which will be combined with the rest of the team's sections
into the final project README.

>   Every claim in this README was actually run and checked before
> writing it down -- not just described. See the `main.py` output
> below for proof.

## Files in this part

| File | What it does | Status |
|---|---|---|
| `flight.py` | The `Flight` class -- stores one flight's data and makes sure it's always valid |   tested (validation + `update_seats` both checked) |
| `sample_data.py` | Builds the flight dataset, reads/writes `flights.csv` |   tested (40 flights, no duplicate IDs, no past dates) |
| `flights.csv` | The actual flight data (40 flights), editable in Excel |   generated and verified |
| `database.py` | SQLite: create the table, insert, select, update, delete |   all 4 CRUD operations tested |
| `logging_config.py` | Turns on logging so everything gets written to `potter_airlines.log` |   confirmed DEBUG/INFO/WARNING/ERROR all appear |
| `main.py` | Runs everything: builds the flights, loads them into the database, and shows insert/select/update/delete working |   runs end-to-end with no errors |

## How to run it

```bash
python main.py
```

**Actual output from a real run (copy-pasted, not made up):**
This will:
1. Read `flights.csv` (creating it from the built-in flight list if it
   doesn't exist yet).  confirmed the file is created
2. Create `potter_airlines.db` and insert all the flights into it.
    confirmed 40 rows land in the table
3. Run a select, an update, and a delete against the database and print
   the results, so you can see all four CRUD operations working.
    confirmed seats go from 18 -> 5 and the deleted flight disappears
   (39 remain, was 40)
4. Write everything that happened to `potter_airlines.log`.
    confirmed all 4 log levels (DEBUG/INFO/WARNING/ERROR) show up

## The Flight class

`Flight` is the one "meaningful class" the project needs. It stores a
flight's id, route, dates, seats, and fare, and checks everything when
the object is created.

### Validation rules

- `capacity` must be greater than 0 --  tested: `Flight(..., capacity=0, ...)` raises `ValueError`
- `seats_remaining` must be between 0 and `capacity` --  tested: `seats_remaining=999` on a 100-seat flight raises `ValueError`
- `base_fare` must not be negative --  tested: `base_fare=-10` raises `ValueError`
- `route_popularity` must be between 0 and 1 --  tested: `route_popularity=1.5` raises `ValueError`

If any of these are wrong, it raises a `ValueError` right away instead
of letting bad data into the system.

### Updating seats safely

`update_seats()` is the only place allowed to change `seats_remaining`,
and it re-checks the same rule every time --  tested: trying to oversell
(`update_seats(-999)`) on a flight with only 5 seats correctly raises
`ValueError` instead of going negative.

## The dataset

### Where the data lives

The flight data is a single source of truth: `_RAW_FLIGHTS`, a Python
list in `sample_data.py`. The first time the code runs, it writes that
list out to `flights.csv`. After that, `flights.csv` is what actually
gets read -- so a teammate can edit it directly in Excel and their
changes will stick (the code only *adds* new flights, it never
overwrites existing rows).  tested both directions: a fresh run
creates the CSV from scratch, and editing a row by hand then re-running
`build_sample_flights()` keeps the manual edit.

### Why the data is varied

The 40 flights are deliberately varied so the pricing rules and the
database queries have something real to work with:
- some depart in <=7 days, some in 8-21 days, some much further out --  checked: 6 flights <=7 days, 6 flights in 8-21 days, 28 flights further out
- some are almost full, some are almost empty --  checked, load factors range 0.10-0.92
- route popularity ranges from 0.38 to 0.95 --  checked against the actual CSV values (min 0.38, max 0.95)
- departures spread across every month, including peak season
  (June-August, December) and low season (January, February, November) --  checked: all 12 months are represented, and no departure date is before the project's reference date (2026-09-15) -- the earliest departure is 2 days out

## Dynamic Pricing

`Pricing.py` contains the dynamic pricing logic used to calculate the fare
for each `Flight` object. The model is intentionally simple and explainable:
each fare is adjusted using a set of business-based pricing factors rather
than an advanced optimization model.

The pricing formula is:

`raw_price = base_fare × time_factor × capacity_factor × demand_factor × weekend_factor × seasonal_factor × cabin_factor`

The calculated `raw_price` is then restricted to the minimum and maximum
fare range for the corresponding cabin class to produce the final fare.

### Time factor

`time_factor(days_until_departure)` increases the fare as the departure date
gets closer.

- 7 days or less -> `1.35`
- 8-21 days -> `1.10`
- more than 21 days -> `1.00`

A departure date in the past raises `ValueError`.

This factor represents an urgency premium: passengers booking closer to
departure are assumed to have less flexibility and therefore face a higher
fare multiplier.

### Capacity factor

`capacity_factor(seats_remaining, capacity)` adjusts the fare based on how
full the flight is.

The load factor is calculated as:

`load_factor = 1 - seats_remaining / capacity`

The capacity factor is then:

`capacity_factor = 1 + 0.45 × load_factor`

As fewer seats remain, the flight becomes fuller, the load factor increases,
and the resulting fare becomes higher.

The underlying `Flight` class validates that `capacity > 0` and that
`seats_remaining` remains between 0 and `capacity`.

### Demand factor

`demand_factor(route_popularity)` adjusts the fare based on how popular the
route is.

The demand factor is calculated as:

`demand_factor = 0.9 + 0.3 × route_popularity`

`route_popularity` is restricted to values between 0 and 1.

A less popular route can receive a multiplier slightly below `1.00`, while a
highly popular route receives a higher multiplier.

### Weekend factor

`weekend_factor(departure_date)` applies a higher multiplier to flights
departing on Friday, Saturday, or Sunday.

- Friday-Sunday -> `1.10`
- Monday-Thursday -> `1.00`

This is a simplified business assumption that weekend travel generally has
stronger demand than weekday travel.

### Seasonal factor

`seasonal_factor(departure_date)` adjusts the fare during selected peak travel
periods.

- June-August -> `1.20`
- November-December -> `1.15`
- all other months -> `1.00`

These multipliers are simplified business assumptions used to demonstrate
how seasonal travel demand can affect fares.

### Cabin-class factor

`cabin_factor(cabin_class)` adjusts the fare according to the passenger's
selected cabin class.

| Cabin class | Pricing factor |
|---|---:|
| Economy | `1.00` |
| Business | `1.60` |
| First | `2.20` |

Economy is used as the baseline cabin. Business and First receive higher
multipliers to reflect the additional service, comfort, and amenities
associated with higher cabin classes.

If an invalid cabin class is provided, `cabin_factor()` raises `ValueError`.

### Fare boundaries

`fare_bounds(cabin_class)` provides a separate minimum and maximum fare range
for each cabin class.

| Cabin class | Minimum fare | Maximum fare |
|---|---:|---:|
| Economy | $45 | $800 |
| Business | $200 | $1,800 |
| First | $500 | $3,000 |

These boundaries prevent the combined dynamic pricing multipliers from
producing fares that are unrealistically low or high for the selected cabin
class.

If an invalid cabin class is provided, `fare_bounds()` raises `ValueError`.

### Final price calculation

`calculate_price(flight, reference_date=None)` combines all pricing components
for a single validated `Flight` object.

The function:

1. calculates the number of days until departure
2. calculates the time factor
3. calculates the capacity factor
4. calculates the demand factor
5. calculates the weekend factor
6. calculates the seasonal factor
7. calculates the cabin-class factor
8. multiplies all factors by the flight's `base_fare` to produce `raw_price`
9. retrieves the minimum and maximum fare bounds for the cabin class
10. restricts `raw_price` to those fare boundaries
11. returns the final fare rounded to two decimal places

This keeps the pricing logic modular: each business rule is implemented in a
separate function, while `calculate_price()` combines them into one final fare.

### Pricing tests

The pricing functions are tested in `test.py` using the existing project
flight dataset rather than manually creating separate test flights.

The tests use the fixed project reference date:

`2026-09-15`

This keeps pricing results reproducible even when the code is run on a
different calendar date.

Two pricing tests are included.

#### Simple Pricing Test

The Simple Pricing Test runs every flight through `calculate_price()` and
displays:

- flight ID
- route
- cabin class
- base fare
- final calculated fare

This provides a quick check that all existing flights can be priced
successfully.

#### Full Pricing Breakdown Test

The Full Pricing Breakdown Test shows the complete pricing calculation for
each flight, including:

- flight ID and route
- departure date
- days until departure
- cabin class
- base fare
- seats remaining and capacity
- load factor
- route popularity
- time factor
- capacity factor
- demand factor
- weekend factor
- seasonal factor
- cabin factor
- raw price
- minimum and maximum fare bounds
- final price

The full breakdown makes each pricing decision traceable and allows the effect
of every pricing factor to be checked individually.

All 40 flights in the project dataset were successfully processed by the
pricing functions.

## The database

`database.py` stores flights in a single `flights` table in SQLite. The
schema repeats the same checks as `Flight.__init__` as SQL `CHECK`
constraints, so the database itself also refuses to store invalid data.

### CRUD operations

All four CRUD operations are covered:

| Operation | Function | Status |
|---|---|---|
| Create (insert) | `insert_flight(conn, flight)`, `insert_many(conn, flights)` |  tested: 40 rows inserted, count confirmed with `SELECT COUNT(*)` |
| Read (select) | `get_all_flights(conn)`, `get_flights_by_destination(conn, destination)`, `get_flight(conn, flight_id)` |  tested: destination filter returns only matching flights |
| Update | `update_seats(conn, flight_id, new_seats_remaining)` |  tested: seats_remaining actually changes in the database, not just in memory |
| Delete | `delete_flight(conn, flight_id)` |  tested: row count drops by exactly 1 after deleting |

### SQL injection safety

Every query uses a `?` placeholder for values that come from a
variable -- never an f-string or `.format()` glued into the SQL text.
That's what keeps this safe from SQL injection.  verified by reading
every query in `database.py` -- no string formatting into SQL anywhere.

## Logging

`logging_config.setup_logging()` is called once at the top of `main.py`,
before anything else is imported. From then on, every `logger.debug` /
`logger.info` / `logger.warning` / `logger.error` call anywhere in the
project (in `flight.py`, `database.py`, `sample_data.py`) gets written
to `potter_airlines.log`, with a timestamp and which file it came from.
 confirmed by triggering all four levels (a normal flight, a normal
seat update, a rejected seat update, and an invalid flight) and reading
the resulting log file.

## Known limitations

- The flight data is fictional, made up for this project.
- There's no GUI -- everything runs through `main.py` or a plain Python
  script.
- `update_seats` only changes seat counts; it doesn't track individual
  bookings, cancellations, or refunds.
