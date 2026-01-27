import random
import math
from api.geocode import geocode
from logic.route_optimizer import optimize

calculated = False

#Todo: Caculate coords for newly added groups
def precalculate_all_coords(manager):
    calculated = False
    groups = manager.get_groups()
    try:
        for group in groups:
            if group.coords == (0,0):
                group.coords = geocode(group.address)
        calculated = True
    except Exception as e:
        print("Coordinate calculation failed")

def is_calculation_done():
    return calculated

def haversine(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        R = 6371.0  # Earth radius in km

        # Convert degrees to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        # Haversine formula
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

def calculate_distances(groups):
    distance = {}
    for team1 in groups:
        for team2 in groups:
            distance[team1.teamname, team2.teamname] = haversine(team1.coords, team2.coords)
    return distance



#Mapping should come from manager (group_id_map)
def calculate_optimum(groups, mapping, randomness_factor = 0):
    if not is_calculation_done(): raise Exception("Precalculation of coordinates has not been finished yet (using soft limits for API calls)")
    distances = calculate_distances(groups)
    totalGroups = len(groups)
    try:
        id_distances = {(mapping[team1],mapping[team2]) : distance for (team1, team2), distance in distances.items()}
        randomized_distances = {(a,b) : (distance + randomness_factor * random.uniform(-1,1)) for (a,b), distance in id_distances.items()}
        assignment = optimize(totalGroups, randomized_distances)
        assignment_transformed = {mapping[host]: (mapping[guest1], mapping[guest2]) for host, (guest1, guest2) in assignment.items()}
        return assignment_transformed
    except Exception as e:
        print("Error! Optimization failed")


