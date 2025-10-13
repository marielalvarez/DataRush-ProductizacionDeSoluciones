import pandas as pd
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes (you can restrict origins later if needed)
CORS(app)


@app.route("/")
def home():
    return "Funciona el backend ayyych uwu!"

@app.route("/summary")
def summary():
    #Calcula los stats
    total_rides = int(df_night_solo.shape[0])
    _avg_distance = df_night_solo["trip_distance"].mean()
    _avg_fare = df_night_solo["fare_amount"].mean()
    # Convert NaN to None so JSON is valid
    avg_distance = None if pd.isna(_avg_distance) else float(_avg_distance)
    avg_fare = None if pd.isna(_avg_fare) else float(_avg_fare)
    return jsonify({
        "total_rides": total_rides,
        "avg_distance": avg_distance,
        "avg_fare": avg_fare
    })

@app.route("/zone-stats")
def zone_stats_route():
    # Return per-zone stats with zone name/borough
    # Use to_json -> json.loads to convert NaN to null and ensure valid JSON
    data = json.loads(zone_stats_named.to_json(orient="records"))
    return jsonify(data)

@app.route("/hourly-trends")
def hourly_trends():
    # Count rides per hour for late-night solo rides
    hourly_counts = df_night_solo["pickup_hour"].value_counts().sort_index()
    # Convert to dict: {hour: count}
    return jsonify(hourly_counts.to_dict())

@app.route("/preview")
def preview():
    # Return first 20 rows of filtered DataFrame
    preview_data = json.loads(df_night_solo.head(20).to_json(orient="records"))
    return jsonify(preview_data)

# Cargue la data directamente de AWS, solo es la de un mes, pero ya que tengamos algo bien lo puedo agrandar para tener un analisis mas chingon.
URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"

# Estas son las columnas relevantes de la data para nuestro proyecto
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

print("Loading data from AWS...")
df = pd.read_parquet(URL, columns=columns)
print(f"Total rows loaded: {len(df):,}")

# Convert pickup time to datetime and add pickup_hour
df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour

# Filtramos para solo ver los de la noche (00:00-03:59, 1 passenger)
df_night_solo = df[(df["pickup_hour"] >= 0) & (df["pickup_hour"] < 4) & (df["passenger_count"] == 1)]
print(f"Late-night solo rides: {len(df_night_solo):,}")

# Group by pickup location (PULocationID) and calculate stats
zone_stats = df_night_solo.groupby("PULocationID").agg(
    total_rides=("PULocationID", "size"),
    avg_distance=("trip_distance", "mean"),
    avg_fare=("fare_amount", "mean")
)

# Normalize ride counts to create a Safety Index (0=least active, 1=most active)
min_rides = zone_stats["total_rides"].min()
max_rides = zone_stats["total_rides"].max()
zone_stats["safety_index"] = (zone_stats["total_rides"] - min_rides) / (max_rides - min_rides)

# Add zone names/borough by joining with NYC taxi zone lookup
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
try:
    lookup = pd.read_csv(ZONE_LOOKUP_URL)
    zone_stats_named = (
        zone_stats.reset_index()
        .merge(lookup[["LocationID", "Borough", "Zone"]], left_on="PULocationID", right_on="LocationID", how="left")
        .rename(columns={"Zone": "zone_name", "Borough": "borough"})
    )
    # Keep a tidy set of columns
    zone_stats_named = zone_stats_named[[
        "PULocationID", "zone_name", "borough", "total_rides", "avg_distance", "avg_fare", "safety_index"
    ]]
except Exception as e:
    # Fallback without names if lookup fails
    print("[WARN] Failed to load taxi zone lookup:", e)
    zone_stats_named = zone_stats.reset_index()

print("\nPer-zone stats (first 5 rows):")
print(zone_stats_named.head())

# Lo guardo todo en un csv para poder usarlo en el front
zone_stats_named.to_csv("zone_stats.csv", index=False)
print("\nSaved per-zone stats to zone_stats.csv")



if __name__ == "__main__":
    app.run(debug = True)