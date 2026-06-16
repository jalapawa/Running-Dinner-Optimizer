import requests
import time

_last_call = 0
rate = 1

def rate_limited(limit):
    global _last_call
    now = time.time()
    elapsed = now - _last_call
    if elapsed < limit:
        time.sleep(limit - elapsed)
    _last_call = time.time()

def geocode(address, city):
    url = f"https://photon.komoot.io/api/?q={address}, city={city}"

    headers = {
        "User-Agent": "Running Dinner Optimizer (https://github.com/jalapawa/Running-Dinner-Optimizer)"
    }

    rate_limited(rate) #We are using public APIs, so a soft limit to limit usage (We preload anyway so no problem)
    r = requests.get(url, headers=headers)

    data = r.json()
    if not data:
        raise ValueError("Address not found")
    coords = data["features"][0]["geometry"]["coordinates"]
    return coords
