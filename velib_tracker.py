import requests
import pymongo
import folium
import schedule
from datetime import datetime
from geopy.distance import geodesic
import openrouteservice
from openrouteservice.directions import directions
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# API and Database configuration
API_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "velib_db"
COLLECTION_NAME = "stations"
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def fetch_velib_data():
    params = {
        "limit": -1,
        "timezone": "Europe/Paris"
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def update_database(data):
    for station in data:
        collection.update_one(
            {"stationcode": station['stationcode']},
            {"$set": station},
            upsert=True
        )
    print(f"Updated {len(data)} stations in the database.")

def display_map(user_location=None):
    map_paris = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

    stations = collection.find()
    for station in stations:
        if station['is_installed'] == 'OUI':
            popup_text = f"""
            Station: {station['name']}<br>
            Available bikes: {station['numbikesavailable']}<br>
            Mechanical: {station['mechanical']}<br>
            Electric: {station['ebike']}<br>
            Capacity: {station['capacity']}
            """
            folium.Marker(
                location=[station['coordonnees_geo']['lat'], station['coordonnees_geo']['lon']],
                popup=popup_text,
                tooltip=station['name']
            ).add_to(map_paris)

    if user_location:
        folium.Marker(user_location, popup="Your Location", icon=folium.Icon(color='red')).add_to(map_paris)

    map_file = "templates/velib_map.html"
    map_paris.save(map_file)
    print(f"Map saved as {map_file}")

def find_nearest_station(user_location):
    nearest_station = None
    min_distance = float('inf')

    stations = collection.find()
    for station in stations:
        station_location = (station['coordonnees_geo']['lat'], station['coordonnees_geo']['lon'])
        distance = geodesic(user_location, station_location).kilometers
        if distance < min_distance:
            min_distance = distance
            nearest_station = station

    return nearest_station

def plan_route(start, end):
    # Initialize OpenRouteService client
    client = openrouteservice.Client(key='5b3ce3597851110001cf62482f039e819ea3427093ceafcf422ce592')

    # Prepare coordinates in (longitude, latitude) format
    coords = [[start[1], start[0]], [end[1], end[0]]]

    try:
        # Request route directions
        route = client.directions(
            profile='driving-car',  # Specify the profile (e.g., driving-car, cycling-regular)
            format='geojson',
            coordinates=coords
        )

        # Create a map to display the route
        route_map = folium.Map(location=start, zoom_start=13)

        # Add route line to map
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']]).add_to(route_map)

        # Add start and end markers
        folium.Marker(start, popup='Start').add_to(route_map)
        folium.Marker(end, popup='End').add_to(route_map)

        # Save the map to a file
        map_file = "templates/route_map.html"
        route_map.save(map_file)
        print(f"Route map saved as {map_file}")

    except Exception as e:
        print(f"Error planning route: {e}")

def update_and_display():
    print(f"Updating data at {datetime.now()}")
    data = fetch_velib_data()
    if data:
        update_database(data)
        display_map()  # Display all stations on the map.
    else:
        print("Failed to update data.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nearby_stations', methods=['POST'])
def nearby_stations():
    data = request.json
    user_location = (data.get('latitude', 48.8566), data.get('longitude', 2.3522))  # Default to Paris if no location provided

    # Display all stations on the map regardless of location access
    display_map(user_location)

    # Find the nearest station and plan route if location was provided
    if data.get('latitude') and data.get('longitude'):
        nearest_station = find_nearest_station(user_location)

        if nearest_station:
            plan_route(user_location, (nearest_station['coordonnees_geo']['lat'], nearest_station['coordonnees_geo']['lon']))
            return jsonify({"status": "success", "nearest_station": nearest_station['name']})

    return jsonify({"status": "success", "message": "Map with all stations displayed."})

if __name__ == "__main__":
    update_and_display()
    schedule.every(1).hour.do(update_and_display)
    app.run(debug=True)