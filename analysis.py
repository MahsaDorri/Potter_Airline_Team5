import numpy as np
import pandas as pd

from flight import Flight
from Pricing import calculate_price


REFERENCE_DATE = pd.Timestamp("2026-09-15").date()


def load_flights_dataframe(conn):
    """Load all flight records from SQLite into a Pandas DataFrame."""
    query = "SELECT * FROM flights"
    return pd.read_sql_query(query, conn)


def add_analysis_columns(df):
    """Add prices and vectorized analysis columns to the flight data."""
    df = df.copy()

    # Use Pricing.py as the single source of truth for dynamic pricing.
    def get_price(row):
        flight = Flight.from_dict(row.to_dict())
        return calculate_price(
            flight,
            reference_date=REFERENCE_DATE,
        )

    df["final_price"] = df.apply(
        get_price,
        axis=1,
    )

    # Calculate analysis metrics across all flights using vectorized operations.
    df["load_factor"] = 1 - np.divide(
        df["seats_remaining"],
        df["capacity"],
)

    df["is_sold_out"] = (
        df["seats_remaining"] == 0
    )

    # Convert unavailable sold-out fares to NaN for Pandas analysis.
    df["final_price"] = pd.to_numeric(
        df["final_price"],
        errors="coerce",
    )

    return df


def get_top_priced_flights(df, n=5):
    """Return the highest-priced flights that still have available seats."""
    available_flights = df[
        ~df["is_sold_out"]
    ]

    return available_flights.nlargest(
        n,
        "final_price",
    )


def summarize_by_destination(df):
    """Summarize pricing and load factors by destination."""
    return (
        df.groupby("destination")
        .agg(
            number_of_flights=("flight_id", "count"),
            average_price=("final_price", "mean"),
            average_load_factor=("load_factor", "mean"),
        )
        .round(2)
        .sort_values(
            "average_price",
            ascending=False,
        )
    )





if __name__ == "__main__":
    import database

    conn = database.connect()

    # Load flight data and calculate analysis metrics.
    df = load_flights_dataframe(conn)
    df = add_analysis_columns(df)

    # Rank the highest-priced available flights.
    print("\nTop 5 highest-priced flights:")
    top_flights = get_top_priced_flights(df)

    print(
        top_flights[
            [
                "flight_id",
                "origin",
                "destination",
                "final_price",
            ]
        ]
    )

    # Summarize pricing by destination.
    print("\nDestination summary:")
    destination_summary = summarize_by_destination(df)

    print(destination_summary)


    print("\nRows:", len(df))

    conn.close()