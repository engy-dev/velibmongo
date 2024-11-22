import requests
import pymongo
import folium
import time
import schedule
from datetime import datetime
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

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

def display_map():
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

    map_file = "velib_map.html"
    map_paris.save(map_file)
    print(f"Map saved as {map_file}")

def run_update():
    print(f"Updating data at {datetime.now()}")
    data = fetch_velib_data()
    if data:
        update_database(data)
        display_map()
    else:
        print("Failed to update data.")

def update_and_display():
    print(f"Updating data at {datetime.now()}")
    data = fetch_velib_data()
    if data:
        update_database(data)
        display_map()
    else:
        print("Failed to update data.")

def run_scheduler():
    schedule.every(1).hour.do(update_and_display)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    update_and_display()
    run_scheduler()