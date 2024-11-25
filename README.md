# Velib Availability Tracker

## Overview
The Velib Availability Tracker is a Python application designed to fetch real-time data about Velib bike-sharing stations in Paris, update a MongoDB database with the latest information, and visualize the data using interactive maps. The application also allows users to find the nearest bike station based on their location and plan routes using the OpenRouteService API.

## Features
- **Real-time Data Fetching**: Automatically retrieves data from the Paris Velib API.
- **Database Management**: Stores and updates station data in a MongoDB database.
- **Map Visualization**: Displays bike stations on an interactive map using Folium.
- **Nearest Station Finder**: Identifies the closest bike station to a given user location.
- **Route Planning**: Plans routes between two points using OpenRouteService and visualizes them on a map.

## Requirements
To run this application, you need the following:
- Python 3.x
- MongoDB
- Required Python packages:
  - `requests`
  - `pymongo`
  - `folium`
  - `geopy`
  - `openrouteservice`
  - `flask`
  - `schedule`

You can install the required packages using pip:

```bash
pip install requests pymongo folium geopy openrouteservice flask schedule
```

## Setup Instructions

1. **Clone the Repository**:
   Clone this repository to your local machine.

2. **Configure MongoDB**:
   Ensure that MongoDB is installed and running on your machine. The application connects to a local MongoDB instance by default. Modify the `MONGO_URI` variable in the code if needed.

3. **Obtain OpenRouteService API Key**:
   Sign up at [OpenRouteService](https://openrouteservice.org/sign-up/) to obtain an API key. Replace `'YOUR_OPENROUTESERVICE_API_KEY'` in the code with your actual API key.

4. **Run the Application**:
   Start the Flask application by executing:

   ```bash
   python app.py
   ```

5. **Access the Application**:
   Open a web browser and navigate to `PROVIDED_HOST` to access the application interface.

## Code Structure

- `app.py`: Main application file containing all functionality.
- `templates/`: Directory containing HTML templates for rendering maps and user interface.
- MongoDB Database: Stores station data with fields such as station name, availability, coordinates, etc.

## Usage

- Upon launching, the application will automatically fetch and update station data every hour.
- Users can send their location via a POST request to `/nearby_stations` to find nearby bike stations.
- The application will display all stations on a map and highlight the nearest one based on user input.

## Data Source

The application fetches real-time Velib availability data from the Paris Open Data API. The relevant dataset includes information about each bike-sharing station, including its availability status, capacity, and geographical coordinates.

## License

This project is licensed under The Unlicense - see the [LICENSE](LICENSE.txt) file for details.

## Acknowledgments

- [OpenRouteService](https://openrouteservice.org/) for routing services.
- [Folium](https://python-visualization.github.io/folium/) for map visualization.
- [Flask](https://flask.palletsprojects.com/) for web framework support.

---

Citations:
[1] https://opendata.paris.fr
