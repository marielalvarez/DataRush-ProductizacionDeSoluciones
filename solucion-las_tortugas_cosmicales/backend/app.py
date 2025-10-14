import pandas as pd
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes (you can restrict origins later if needed)
CORS(app)

# Helper to load and process data for a given month
def load_and_process_data(month="2023-01"):
    URL = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month}.parquet"
    columns = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "PULocationID",
        "DOLocationID",
        "fare_amount",
        "payment_type"
    ]
    df = pd.read_parquet(URL, columns=columns)
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df_night_solo = df[(df["pickup_hour"] >= 0) & (df["pickup_hour"] < 4) & (df["passenger_count"] == 1)]
    zone_stats = df_night_solo.groupby("PULocationID").agg(
        total_rides=("PULocationID", "size"),
        avg_distance=("trip_distance", "mean"),
        avg_fare=("fare_amount", "mean")
    )
    min_rides = zone_stats["total_rides"].min()
    max_rides = zone_stats["total_rides"].max()
    zone_stats["safety_index"] = (zone_stats["total_rides"] - min_rides) / (max_rides - min_rides)
    # Add zone names/borough
    ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    try:
        lookup = pd.read_csv(ZONE_LOOKUP_URL)
        zone_stats_named = (
            zone_stats.reset_index()
            .merge(lookup[["LocationID", "Borough", "Zone"]], left_on="PULocationID", right_on="LocationID", how="left")
            .rename(columns={"Zone": "zone_name", "Borough": "borough"})
        )
        zone_stats_named = zone_stats_named[[
            "PULocationID", "zone_name", "borough", "total_rides", "avg_distance", "avg_fare", "safety_index"
        ]]
    except Exception as e:
        zone_stats_named = zone_stats.reset_index()
    return df_night_solo, zone_stats_named


@app.route("/")
def home():
    return "Funciona el backend ayyych uwu!"

@app.route("/summary")
def summary():
    month = request.args.get("month", "2023-01")
    df_night_solo, _ = load_and_process_data(month)
    total_rides = int(df_night_solo.shape[0])
    _avg_distance = df_night_solo["trip_distance"].mean()
    _avg_fare = df_night_solo["fare_amount"].mean()
    avg_distance = None if pd.isna(_avg_distance) else float(_avg_distance)
    avg_fare = None if pd.isna(_avg_fare) else float(_avg_fare)
    return jsonify({
        "total_rides": total_rides,
        "avg_distance": avg_distance,
        "avg_fare": avg_fare
    })

@app.route("/zone-stats")
def zone_stats_route():
    month = request.args.get("month", "2023-01")
    _, zone_stats_named = load_and_process_data(month)
    data = json.loads(zone_stats_named.to_json(orient="records"))
    return jsonify(data)

@app.route("/hourly-trends")
def hourly_trends():
    month = request.args.get("month", "2023-01")
    df_night_solo, _ = load_and_process_data(month)
    hourly_counts = df_night_solo["pickup_hour"].value_counts().sort_index()
    return jsonify(hourly_counts.to_dict())

@app.route("/preview")
def preview():
    month = request.args.get("month", "2023-01")
    df_night_solo, _ = load_and_process_data(month)
    preview_data = json.loads(df_night_solo.head(20).to_json(orient="records"))
    return jsonify(preview_data)

if __name__ == "__main__":
    app.run(debug = True)