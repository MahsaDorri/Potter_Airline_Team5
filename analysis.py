import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_flights_dataframe(conn):
    """Load all flight records from SQLite into a Pandas DataFrame."""
    query = "SELECT * FROM flights"
    return pd.read_sql_query(query, conn)


def add_pricing_factors(df):
    """Calculate dynamic pricing factors across all flights."""
    df = df.copy()

    # Prepare departure dates and use a fixed date for reproducible analysis.
    df["departure_date"] = pd.to_datetime(df["departure_date"])
    reference_date = pd.Timestamp("2026-09-15")

    df["days_until_departure"] = (
        df["departure_date"] - reference_date
    ).dt.days

    # Keep the vectorized pricing logic consistent with Pricing.py.
    if (df["days_until_departure"] < 0).any():
        raise ValueError(
            "Dataset contains departure dates in the past."
        )

    # Calculate time, weekend, and seasonal pricing factors.
    df["time_factor"] = np.select(
        [
            df["days_until_departure"] <= 7,
            df["days_until_departure"] <= 21,
        ],
        [1.35, 1.10],
        default=1.00,
    )

    df["weekend_factor"] = np.where(
        df["departure_date"].dt.weekday >= 4,
        1.10,
        1.00,
    )

    df["seasonal_factor"] = np.select(
        [
            df["departure_date"].dt.month.isin([6, 7, 8]),
            df["departure_date"].dt.month.isin([11, 12]),
        ],
        [1.20, 1.15],
        default=1.00,
    )

    # Calculate capacity and demand-related pricing factors.
    df["load_factor"] = (
        1 - df["seats_remaining"] / df["capacity"]
    )

    df["capacity_factor"] = (
        1 + 0.45 * df["load_factor"]
    )

    df["demand_factor"] = (
        0.9 + 0.3 * df["route_popularity"]
    )

    # Calculate the raw dynamic price.
    df["raw_price"] = (
        df["base_fare"]
        * df["time_factor"]
        * df["capacity_factor"]
        * df["demand_factor"]
        * df["weekend_factor"]
        * df["seasonal_factor"]
    )

    # Apply minimum and maximum fare bounds.
    df["final_price"] = df["raw_price"].clip(
        lower=45,
        upper=1500,
    ).round(2)

    # Mark sold-out flights as unavailable for purchase.
    df["is_sold_out"] = (
        df["seats_remaining"] == 0
    )

    df.loc[
        df["is_sold_out"],
        "final_price"
    ] = np.nan

    return df


def get_top_priced_flights(df, n=5):
    """Return the highest-priced flights that still have available seats."""
    available_flights = df[
        ~df["is_sold_out"]
    ]

    return available_flights.nlargest(
        n,
        "final_price"
    )


def summarize_by_destination(df):
    """Summarize pricing and load factors by destination."""
    return (
        df.groupby("destination")
        .agg(
            number_of_flights=(
                "flight_id",
                "count"
            ),
            average_price=(
                "final_price",
                "mean"
            ),
            average_load_factor=(
                "load_factor",
                "mean"
            ),
        )
        .round(2)
        .sort_values(
            "average_price",
            ascending=False
        )
    )


def plot_average_price_by_destination(summary):
    """Visualize the average dynamic price by destination."""
    average_prices = summary[
        "average_price"
    ].sort_values()

    ax = average_prices.plot(
        kind="barh",
        figsize=(8, 5),
    )

    # Add the average price value beside each bar.
    for i, value in enumerate(average_prices):
        ax.text(
            value,
            i,
            f"${value:.2f}",
            va="center"
        )

    # Add extra horizontal space so the labels remain visible.
    ax.set_xlim(
        0,
        average_prices.max() * 1.15
    )

    plt.title(
        "Average Dynamic Price by Destination"
    )

    plt.xlabel(
        "Average Price ($)"
    )

    plt.ylabel(
        "Destination"
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    from datetime import date

    import database
    from Pricing import calculate_price

    conn = database.connect()

    # Run vectorized pricing analysis.
    df = load_flights_dataframe(conn)
    df = add_pricing_factors(df)

    print(
        df[
            [
                "flight_id",
                "base_fare",
                "raw_price",
                "final_price"
            ]
        ].head()
    )

    # Rank the highest-priced available flights.
    print(
        "\nTop 5 highest-priced flights:"
    )

    top_flights = get_top_priced_flights(
        df
    )

    print(
        top_flights[
            [
                "flight_id",
                "origin",
                "destination",
                "final_price"
            ]
        ]
    )

    # Summarize and visualize pricing by destination.
    print(
        "\nDestination summary:"
    )

    destination_summary = summarize_by_destination(
        df
    )

    print(destination_summary)

    plot_average_price_by_destination(
        destination_summary
    )

    print(
        "\nRows:",
        len(df)
    )

    # Cross-check vectorized prices against
    # the single-flight pricing engine.
    flights = database.get_all_flights(
        conn
    )

    pricing_results = {
        flight.flight_id: calculate_price(
            flight,
            reference_date=date(
                2026,
                9,
                15
            ),
        )
        for flight in flights
    }

    df["pricing_py_price"] = (
        df["flight_id"].map(
            pricing_results
        )
    )

    # Treat matching missing prices as equal
    # for sold-out flights.
    df["price_matches"] = np.isclose(
        df["final_price"],
        df["pricing_py_price"],
        equal_nan=True,
    )

    matches = (
        df["price_matches"].sum()
    )

    print(
        "\nPricing validation:"
    )

    print(
        f"{matches} of "
        f"{len(df)} flights matched Pricing.py"
    )

    conn.close()