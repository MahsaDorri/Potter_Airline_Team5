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

    # Seasonal factor
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

    # Calculate dynamic price across all flights
    df["raw_price"] = (
        df["base_fare"]
        * df["time_factor"]
        * df["capacity_factor"]
        * df["demand_factor"]
        * df["weekend_factor"]
        * df["seasonal_factor"]
    )

    # Apply minimum and maximum fare bounds
    df["final_price"] = df["raw_price"].clip(
        lower=45,
        upper=1500
    ).round(2)

    return df


def get_top_priced_flights(df, n=5):
    return df.nlargest(n, "final_price")


def summarize_by_destination(df):
    summary = (
        df.groupby("destination")
        .agg(
            number_of_flights=("flight_id", "count"),
            average_price=("final_price", "mean"),
            average_load_factor=("load_factor", "mean")
        )
        .round(2)
        .sort_values("average_price", ascending=False)
    )

    return summary


if __name__ == "__main__":
    import database
    from Pricing import calculate_price
    from datetime import date

    conn = database.connect()

    # Load flight data from SQLite
    df = load_flights_dataframe(conn)

    # Apply vectorized pricing calculations
    df = add_pricing_factors(df)

    # Show sample calculated prices
    print(
        df[
            ["flight_id", "base_fare", "raw_price", "final_price"]
        ].head()
    )

    # Show highest-priced flights
    print("\nTop 5 highest-priced flights:")

    top_flights = get_top_priced_flights(df)

    print(
        top_flights[
            ["flight_id", "origin", "destination", "final_price"]
        ]
    )

    # Show destination-level analysis
    print("\nDestination summary:")

    destination_summary = summarize_by_destination(df)

    print(destination_summary)

    print("\nRows:", len(df))

    # Cross-check vectorized pricing against Pricing.py
    flight = database.get_flight(conn, "PA2001")

    original_price = calculate_price(
        flight,
        reference_date=date(2026, 9, 15)
    )

    vectorized_price = df.loc[
        df["flight_id"] == "PA2001",
        "final_price"
    ].iloc[0]

    print("\nPricing cross-check:")
    print("Pricing.py:", original_price)
    print("analysis.py:", vectorized_price)

    conn.close()