from route_optimizer import optimize
import teststrecken
import requests
import time

_last_call = 0

def rate_limited():
    global _last_call
    now = time.time()
    elapsed = now - _last_call
    if elapsed < 1:
        time.sleep(1 - elapsed)
    _last_call = time.time()

def geocode(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "Running Dinner Optimizer (https://github.com/jalapawa/Running-Dinner-Optimizer)"
    }

    rate_limited()
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()

    data = r.json()
    if not data:
        raise ValueError("Address not found")

    print("Geocoding data © OpenStreetMap contributors")
    return float(data[0]["lat"]), float(data[0]["lon"])


def calculate_distances():
    try:
        assignment = optimize(30, teststrecken.strecken)
        print(assignment)
    except Exception as e:
        print("Runtime error! Opt not possible!!")

geocode("Peterstraße 70")