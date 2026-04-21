from flask import Flask, render_template, request, jsonify
import heapq
import math
import requests
import time
import json
import os

CACHE_FILE = "distance_cache.json"

# Load cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        distance_cache = json.load(f)
else:
    distance_cache = {}

# Save cache
def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(distance_cache, f)

app = Flask(__name__)

# city coordinates
coords = {
    "Bhopal": [23.2599, 77.4126],
    "Indore": [22.7196, 75.8577],
    "Jabalpur": [23.1815, 79.9864],
    "Gwalior": [26.2183, 78.1828],
    "Ujjain": [23.1765, 75.7885],
    "Sagar": [23.8388, 78.7378],
    "Satna": [24.5854, 80.8322],
    "Rewa": [24.5362, 81.3037],
    "Katni": [23.8356, 80.3940],
    "Khandwa": [21.8256, 76.3526],
    "Burhanpur": [21.3080, 76.2304],
    "Ratlam": [23.3342, 75.0378],
    "Neemuch": [24.4730, 74.8720],
    "Mandsaur": [24.0736, 75.0672],
    "Chhindwara": [22.0574, 78.9382],
    "Betul": [21.9030, 77.9030],
    "Hoshangabad": [22.7441, 77.7369],
    "Vidisha": [23.5236, 77.8060],
    "Sehore": [23.2000, 77.0833],
    "Dewas": [22.9676, 76.0534],
    "Shajapur": [23.4264, 76.2778],
    "Rajgarh": [23.8700, 76.7333],
    "Raisen": [23.3315, 77.7811],
    "Seoni": [22.0850, 79.5500],
    "Balaghat": [21.8129, 80.1838],
    "Mandla": [22.5970, 80.3711],
    "Shahdol": [23.2935, 81.3619],
    "Panna": [24.7200, 80.1877],
    "Chhatarpur": [24.9142, 79.5880],
    "Tikamgarh": [24.7450, 78.8300],
    "Datia": [25.6653, 78.4609],
    "Shivpuri": [25.4238, 77.6620],
    "Morena": [26.5000, 78.0000],
    "Bhind": [26.5667, 78.7833],
    "Sheopur": [25.6667, 76.7000],
    "Guna": [24.6500, 77.3167],
    "Ashoknagar": [24.5667, 77.7333],
    "Barwani": [22.0333, 74.9000],
    "Khargone": [21.8333, 75.6167],
    "Dhar": [22.6000, 75.3000],
    "Jhabua": [22.7670, 74.5900],
    "Harda": [22.3500, 77.1000],
    "Itarsi": [22.6167, 77.7500],
    "Narsinghpur": [22.9500, 79.2000],
    "Damoh": [23.8333, 79.4500]
}

# aproxx distance
def approx_distance(c1, c2):
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2) * 111


# osrm distance
def osrm_distance(c1, c2, city1, city2):
    key = f"{city1}-{city2}"
    reverse_key = f"{city2}-{city1}"

    # Check cache first
    if key in distance_cache:
        return distance_cache[key]
    if reverse_key in distance_cache:
        return distance_cache[reverse_key]

    url = f"http://router.project-osrm.org/route/v1/driving/{c1[1]},{c1[0]};{c2[1]},{c2[0]}?overview=false"

    try:
        res = requests.get(url, timeout=5).json()

        if "routes" in res and len(res["routes"]) > 0:
            dist = round(res["routes"][0]["distance"] / 1000)

            # Save to cache
            distance_cache[key] = dist
            save_cache()

            return dist

    except Exception as e:
        print("OSRM error:", e)

    return None


# build graph
graph = {}

print("Building graph...")

for city1 in coords:
    graph[city1] = {}

    for city2 in coords:
        if city1 != city2:
            approx = approx_distance(coords[city1], coords[city2])

            if approx < 120:
                dist = osrm_distance(coords[city1], coords[city2], city1, city2)

                if dist is not None:
                    graph[city1][city2] = dist

                time.sleep(0.1)

print("Graph ready!")


# dijkstra
def dijkstra(graph, start, end):
    queue = [(0, start)]
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    prev = {}

    while queue:
        d, node = heapq.heappop(queue)

        if node == end:
            break

        for neigh, weight in graph[node].items():
            new_d = d + weight

            if new_d < dist[neigh]:
                dist[neigh] = new_d
                prev[neigh] = node
                heapq.heappush(queue, (new_d, neigh))

    path = []
    node = end

    if node not in prev and node != start:
        return [], 0

    while node in prev:
        path.insert(0, node)
        node = prev[node]

    path.insert(0, start)

    return path, dist[end]


# routes
@app.route('/')
def home():
    return render_template('index.html', cities=list(coords.keys()))


@app.route('/route', methods=['POST'])
def route():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')

    if start not in coords or end not in coords:
        return jsonify({"error": "Invalid city"}), 400

    path, total_distance = dijkstra(graph, start, end)

    if not path:
        return jsonify({"error": "No route found"}), 404

    coords_str = ";".join(
        f"{coords[city][1]},{coords[city][0]}" for city in path
    )

    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"

    try:
        res = requests.get(url, timeout=10).json()
        geometry = res["routes"][0]["geometry"]["coordinates"]
        route_coords = [[c[1], c[0]] for c in geometry]
    except Exception as e:
        print("Route fetch error:", e)
        route_coords = [coords[city] for city in path]

    return jsonify({
    "path": path,
    "distance": total_distance,
    "coordinates": route_coords,
    "city_coords": [coords[city] for city in path]   
    })


# run
if __name__ == '__main__':
    app.run(debug=True)