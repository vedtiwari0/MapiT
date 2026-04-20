from flask import Flask, render_template, request, jsonify
import heapq
import math

app = Flask(__name__)

coords = {
"Bhopal":[23.2599,77.4126],"Indore":[22.7196,75.8577],"Jabalpur":[23.1815,79.9864],
"Gwalior":[26.2183,78.1828],"Ujjain":[23.1765,75.7885],"Sagar":[23.8388,78.7378],
"Satna":[24.5854,80.8322],"Rewa":[24.5362,81.3037],"Katni":[23.8356,80.3940],
"Khandwa":[21.8256,76.3526],"Burhanpur":[21.3080,76.2304],"Ratlam":[23.3342,75.0378],
"Neemuch":[24.4730,74.8720],"Mandsaur":[24.0736,75.0672],"Chhindwara":[22.0574,78.9382],
"Betul":[21.9030,77.9030],"Hoshangabad":[22.7441,77.7369],"Narmadapuram":[22.7441,77.7369],
"Vidisha":[23.5236,77.8060],"Sehore":[23.2000,77.0833],"Dewas":[22.9676,76.0534],
"Shajapur":[23.4264,76.2778],"Agar":[23.7118,76.0157],"Rajgarh":[23.8700,76.7333],
"Raisen":[23.3315,77.7811],"Seoni":[22.0850,79.5500],"Balaghat":[21.8129,80.1838],
"Mandla":[22.5970,80.3711],"Dindori":[22.9414,81.0788],"Shahdol":[23.2935,81.3619],
"Umaria":[23.5245,80.8374],"Anuppur":[23.1000,81.6833],"Singrauli":[24.1990,82.6640],
"Panna":[24.7200,80.1877],"Chhatarpur":[24.9142,79.5880],"Tikamgarh":[24.7450,78.8300],
"Datia":[25.6653,78.4609],"Shivpuri":[25.4238,77.6620],"Morena":[26.5000,78.0000],
"Bhind":[26.5667,78.7833],"Sheopur":[25.6667,76.7000],"Guna":[24.6500,77.3167],
"Ashoknagar":[24.5667,77.7333],"Barwani":[22.0333,74.9000],"Khargone":[21.8333,75.6167],
"Dhar":[22.6000,75.3000],"Alirajpur":[22.3000,74.3500],"Jhabua":[22.7670,74.5900],
"Badwani":[22.0333,74.9000],"Harda":[22.3500,77.1000],"Itarsi":[22.6167,77.7500],
"Pipariya":[22.7500,78.3500],"Multai":[21.7667,78.2500],"Amla":[21.9333,78.1333],
"Saunsar":[21.6500,78.7833],"Waraseoni":[21.7667,80.0500],"Baihar":[22.1000,80.5500],
"Lakhnadon":[22.6000,79.6000],"Narsinghpur":[22.9500,79.2000],"Gotegaon":[23.0000,79.5000],
"Kareli":[22.9167,79.0667],"Damoh":[23.8333,79.4500],"Patharia":[23.9000,79.2000],
"Hatta":[24.1333,79.6000],"Maihar":[24.2667,80.7500],"Nagod":[24.5667,80.6000],
"Amarpatan":[24.3167,80.9833],"Sohagpur":[22.7000,78.2000],"Gadarwara":[22.9167,78.7833],
"SeoniMalwa":[22.4500,77.4667],"Obedullaganj":[23.0500,77.5667],"Mandideep":[23.0833,77.5333],
"Nasrullaganj":[22.6833,77.2667],"Budhni":[22.7833,77.6833],"Ashta":[23.0167,76.7167],
"Ichhawar":[23.0167,77.0167],"Kannod":[22.6667,76.7333],"Bagli":[22.6500,76.3500],
"Sonkatch":[22.9500,76.0500],"Tarana":[23.3333,76.0167],"Mahidpur":[23.4833,75.6500],
"Badnagar":[23.0833,75.2167],"Depalpur":[22.8500,75.5500],"Sanwer":[22.9833,75.8333],
"Manawar":[22.2333,75.0833],"Kukshi":[22.2000,74.7500],"Sardarpur":[22.6833,74.9500],
"Jobat":[22.4167,74.5667],"Thandla":[23.0000,74.5667],"Petlawad":[23.0167,74.8000],
"Jaora":[23.6333,75.1333],"Alot":[23.7500,75.5500],"Garoth":[24.1667,75.6500],
"Sitamarhi":[24.5000,75.3000]
}
def distance(c1, c2):
    return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)

graph = {}

for city1 in coords:
    graph[city1] = {}
    for city2 in coords:
        if city1 != city2:
            dist = distance(coords[city1], coords[city2])
            if dist < 1.5:  # threshold (adjust)
                graph[city1][city2] = round(dist * 111)  # approx km
                
# Dijkstra Algorithm
def dijkstra(graph, start, end):
    queue = [(0, start)]
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    prev = {}

    while queue:
        d, node = heapq.heappop(queue)

        for neigh, weight in graph[node].items():
            new_d = d + weight
            if new_d < dist[neigh]:
                dist[neigh] = new_d
                prev[neigh] = node
                heapq.heappush(queue, (new_d, neigh))

    path = []
    node = end
    while node in prev:
        path.insert(0, node)
        node = prev[node]
    path.insert(0, start)

    return path, dist[end]

@app.route('/')
def home():
    return render_template('index.html', cities=graph.keys())

@app.route('/route', methods=['POST'])
def route():
    data = request.json
    start = data['start']
    end = data['end']

    path, distance = dijkstra(graph, start, end)

    # Convert to coordinates for map drawing
    path_coords = [coords[city] for city in path]

    return jsonify({
        "path": path,
        "distance": distance,
        "coordinates": path_coords
    })

if __name__ == '__main__':
    app.run(debug=True)