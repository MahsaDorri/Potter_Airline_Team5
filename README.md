# Potter Airlines

## Flight Class, Dataset, Dynamic Pricing, Analysis & Database

This project implements an end-to-end dynamic revenue management workflow
for Potter Airlines -- flight data validation, SQLite persistence, dynamic
pricing, Pandas/NumPy analysis, visualization, and error handling.

> Everything below was actually run and checked before writing it down,
> it's not just a description.

## Files in this project

| File | What it does |
|---|---|
| `flight.py` | The `Flight` class -- stores one flight's data and makes sure it's always valid |
| `sample_data.py` | Builds the flight dataset, reads/writes `flights.csv` |
| `flights.csv` | The actual flight data (40 flights), can be opened/edited in Excel |
| `Pricing.py` | Dynamic pricing engine -- calculates fares using time urgency, occupancy, route popularity, weekend travel, and seasonal effects, with fare limits |
| `database.py` | SQLite -- create the table, insert, select, update, delete |
| `analysis.py` | Uses Pandas and NumPy to calculate dynamic prices across flights, rank them, summarize by destination, and visualize results |
| `logging_config.py` | Turns on logging so project activity gets written to `potter_airlines.log` |
| `main.py` | Runs the whole workflow end to end |
| `test.py` | Pricing checks and edge-case validation tests |

## How to run it

Install the required packages:

```bash
pip install pandas numpy matplotlib
```

Then run the project:

```bash
python main.py
```

Running `main.py` will:

1. Read `flights.csv` and build the flight dataset.
2. Create `potter_airlines.db` and insert all the flights into it.
3. Demonstrate database CRUD operations -- select, update, delete.
4. Apply the dynamic pricing model to the current flights.
5. Load the updated data into a Pandas DataFrame and run vectorized pricing calculations.
6. Rank the highest-priced available flights and summarize results by destination.
7. Show a graph of average dynamic price by destination.
8. Demonstrate error handling and validation.
9. Write project activity to `potter_airlines.log`.

## The Flight class

`Flight` is the main object-oriented piece of the project. It stores a
flight's id, route, departure date, base fare, seat info, and route
popularity, and checks the data is valid as soon as the object is created.

A few things it checks:
- `capacity` has to be more than 0 -- tried `capacity=0`, it correctly throws an error
- `seats_remaining` can't be more than `capacity` -- tried `seats_remaining=999` on a 100-seat flight, errors out
- `base_fare` can't be negative -- tried -10, errors out
- `route_popularity` has to be between 0 and 1 -- tried 1.5, errors out

`update_seats()` is the only place that changes `seats_remaining`, and it
checks the same rules, so a flight can't get oversold by accident.

## The dataset

Data start as a Python list in `sample_data.py`, get saved to
`flights.csv` on first run (and never overwritten after that), and the 40
flights are made deliberately varied so pricing and analysis have
different conditions to work with.

## Dynamic Pricing

`Pricing.py` calculates a dynamic fare for each `Flight` using several
simple and explainable business rules.

The pricing formula is:

`raw_price = base_fare × time_factor × capacity_factor × demand_factor × weekend_factor × seasonal_factor`

The calculated price is then limited to a minimum fare of `$45` and a
maximum fare of `$1500`.

### Time factor

The fare increases as the departure date gets closer:

- 7 days or less → `1.35`
- 8-21 days → `1.10`
- More than 21 days → `1.00`

A departure date in the past raises `ValueError`.

### Capacity factor

The capacity factor increases the fare as the flight becomes fuller.

`load_factor = 1 - seats_remaining / capacity`

`capacity_factor = 1 + 0.45 × load_factor`

A higher load factor means fewer seats remain and therefore a higher fare.

### Demand factor

Route popularity is used as a simple demand signal:

`demand_factor = 0.9 + 0.3 × route_popularity`

More popular routes receive a higher pricing multiplier.

### Weekend factor

Flights departing on Friday, Saturday, or Sunday receive a higher multiplier:

- Friday-Sunday → `1.10`
- Monday-Thursday → `1.00`

### Seasonal factor

Selected higher-demand travel periods receive an additional multiplier:

- June-August → `1.20`
- November-December → `1.15`
- All other months → `1.00`

### Final price

`calculate_price()` combines all pricing factors with the flight's
`base_fare` and restricts the result to the `$45-$1500` fare range.

If `seats_remaining` is `0`, the flight is treated as sold out and no
purchasable fare is returned.

The final available fare is rounded to two decimal places.

## Pandas and NumPy Analysis

`analysis.py` uses vectorized Pandas and NumPy operations to apply the
dynamic pricing logic across multiple flights.

The analysis:

- calculates dynamic prices across the dataset
- handles sold-out flights
- ranks the highest-priced available flights
- summarizes average price and load factor by destination
- visualizes average dynamic price by destination using Matplotlib
- cross-checks the vectorized pricing results against `Pricing.py`

The same fixed reference date (`2026-09-15`) is used so the pricing results
remain reproducible.

## The database

`database.py` stores flights in a single `flights` table in SQLite.

The schema includes SQL `CHECK` constraints that reinforce the same core
validation rules used by the `Flight` class.

### CRUD operations

All four CRUD operations are included:

| Operation | Function | Status |
|---|---|---|
| Create | `insert_flight(conn, flight)`, `insert_many(conn, flights)` | tested |
| Read | `get_all_flights(conn)`, `get_flights_by_destination(conn, destination)`, `get_flight(conn, flight_id)` | tested |
| Update | `update_seats(conn, flight_id, new_seats_remaining)` | tested |
| Delete | `delete_flight(conn, flight_id)` | tested |

### SQL injection safety

Queries that use variable input use `?` placeholders rather than directly
inserting values into SQL strings.

For example:

```python
conn.execute(
    "SELECT * FROM flights WHERE destination = ?",
    (destination,)
)
```

This keeps variable values separate from the SQL command itself.

## Logging

`logging_config.setup_logging()` is called at the beginning of `main.py`.

Project logging from `flight.py`, `database.py`, and `sample_data.py` is
written to:

`potter_airlines.log`

The log includes timestamps, log levels, module names, and messages.

## Testing and validation

`test.py` includes pricing checks and edge-case validation.

The edge cases include:

- zero capacity
- seats remaining greater than capacity
- negative base fare
- invalid route popularity
- departure date in the past
- sold-out flights
- overselling seats through `update_seats()`

These checks confirm that invalid states are rejected and sold-out flights are
handled correctly.

## Known limitations

- The flight data is fictional and was created for this project.
- There is no graphical user interface; the project runs through Python scripts.
- `update_seats()` only changes seat counts and does not track individual bookings, cancellations, or refunds.
- The pricing model uses simplified business rules rather than an advanced revenue optimization model.
