import random
import math
from api.geocode import geocode
from logic.route_optimizer import optimize
from statistics import median


#Todo: Calculate coords for newly added groups
def precalculate_all_coords(manager, statusBar, config):
    groups = manager.get_groups().copy() #Shallow copy in case a group gets removed!
    total = len(groups)
    try:
        for index, group in enumerate(groups):
            if group.coords == (0,0):
                #group.coords = geocode(group.address, config.city)
                group.coords = geocode(group.address, "Aachen")
            statusBar.emit(f"Precalculating coords: {index}/{total}")
        statusBar.emit("Coords precalculated, saving recommended!")
    except Exception as e:
        print(f"Coordinate calculation failed : {e}")

def is_calculation_done(groups):
    return not (groups[-1].coords == (0,0)) #CHECK LAST GROUP FOR 00 COORDS

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

def randomized_distance(d, all_distances, level):
    return d
    alpha = (level - 1) / 4  # 0..1

    random_dist = random.choice(all_distances)

    return (1 - alpha) * d + alpha * random_dist

def calculate_optimum(groups, mapping, randomness_factor, besties, haties):
    if not is_calculation_done(groups): raise Exception("Precalculation of coordinates has not been finished yet (using soft limits for API calls)")
    distances = calculate_distances(groups)
    totalGroups = len(groups)
    try:
        id_distances = {(mapping[team1],mapping[team2]) : distance for (team1, team2), distance in distances.items()}
        randomized_distances = {(a,b) : (randomized_distance(distance, list(distances.values()), randomness_factor)) for (a,b), distance in id_distances.items()}
        besties_to_id = [(mapping[team1.teamname],mapping[team2.teamname]) for (team1, team2) in besties]
        haties_to_id = [(mapping[team1.teamname],mapping[team2.teamname]) for (team1, team2) in haties]
        assignment = optimize(totalGroups, randomized_distances, besties_to_id, haties_to_id)
        #assignment_transformed = {mapping[host]: (mapping[guest1], mapping[guest2]) for host, (guest1, guest2) in assignment.items()}
        return assignment
    except Exception as e:
        print(f"Error! Optimization failed: {e}")

