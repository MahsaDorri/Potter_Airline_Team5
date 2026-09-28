import numpy as np
import pandas as pd


def load_flights_dataframe(conn):
    query = "SELECT * FROM flights"
    df = pd.read_sql_query(query, conn)
    return df


def add_pricing_factors(df):
    df = df.copy()

    # Convert departure dates to Pandas datetime format
    df["departure_date"] = pd.to_datetime(df["departure_date"])

    # Fixed reference date for reproducible analysis
    reference_date = pd.Timestamp("2026-09-15")

    # Calculate days until departure for all flights
    df["days_until_departure"] = (
        df["departure_date"] - reference_date
    ).dt.days

    # Time factor
    df["time_factor"] = np.select(
        [
            df["days_until_departure"] <= 7,
            df["days_until_departure"] <= 21
        ],
        [
            1.35,
            1.10
        ],
        default=1.00
    )

    # Weekend factor
    df["weekend_factor"] = np.where(
        df["departure_date"].dt.weekday >= 4,
        1.10,
        1.00
    )

    df["seasonal_factor"] = np.select(
    [
        df["departure_date"].dt.month.isin([6, 7, 8]),
        df["departure_date"].dt.month.isin([11, 12])
    ],
    [
        1.20,
        1.15
    ],
    default=1.00
)

    # Load factor
    df["load_factor"] = (
        1 - df["seats_remaining"] / df["capacity"]
    )

    # Capacity factor
    df["capacity_factor"] = (
        1 + 0.45 * df["load_factor"]
    )

    # Demand factor
    df["demand_factor"] = (
        0.9 + 0.3 * df["route_popularity"]
    )

    df["raw_price"] = (
    df["base_fare"]
    * df["time_factor"]
    * df["capacity_factor"]
    * df["demand_factor"]
    * df["weekend_factor"]
    * df["seasonal_factor"]
)

    df["final_price"] = df["raw_price"].clip(
    lower=45,
    upper=1500
).round(2)

    return df


if __name__ == "__main__":
    import database

    conn = database.connect()

    df = load_flights_dataframe(conn)
    df = add_pricing_factors(df)

    print(
        df[
            ["flight_id", "base_fare", "raw_price", "final_price"]
        ].head()
    )

    print("\nTop 5 highest-priced flights:")

    top_flights = df.nlargest(5, "final_price")

    print(
        top_flights[
            ["flight_id", "origin", "destination", "final_price"]
        ]
    )

    print("Rows:", len(df))

    conn.close()