from ortools.sat.python import cp_model
from itertools import permutations, combinations

#New changes, see gemini!

def optimize(totalGroups, distances, besties, haties, config):
    
    def distance(a, b):
        raw_dist = distances[min(a, b), max(a, b)]
        # Force the result to be a pure integer after scaling and squaring
        return int((raw_dist * 100) ** 2)

    anzahlGruppen = totalGroups
    cutStarter = (anzahlGruppen // 3) + 1 
    cutMain = 2 * (anzahlGruppen // 3) + 1 
    cutDessert = anzahlGruppen + 1          

    model = cp_model.CpModel()

    groups = range(1, anzahlGruppen + 1)
    starters = range(1, cutStarter)
    mains = range(cutStarter, cutMain)
    desserts = range(cutMain, cutDessert)
    
    solver_time = config["solver_time"]
    no_dessert = config["no_dessert"]

    # ----------------------------------------------------
    # VARIABLES 
    # ----------------------------------------------------
    X = {}
    #Groups
    for h in groups:
        for g in groups:
            X[h,g] = model.NewBoolVar(f"X_{h}_{g}")

    #Every host exactly two groups
    for h in groups:
        model.Add(
            sum(X[h, g] for g in groups) == 2
        )
    #Forbidden selfvisits
    for g in groups:
        model.Add(X[g, g] == 0)
    #Every group at exactly two hosts
    for g in groups:
        model.Add(
            sum(X[h, g] for h in groups) == 2
        )
    #Eat at some starter
    for g in list(mains) + list(desserts):
        model.Add(
            sum(X[h, g] for h in starters) == 1
        )
    #Eat at some main
    for g in list(starters) + list(desserts):
        model.Add(
            sum(X[h, g] for h in mains) == 1
        )
    #Eat at some dessert
    for g in list(starters) + list(mains):
        model.Add(
            sum(X[h, g] for h in desserts) == 1
        )

    #Meeting constraint :O

    meet = {}
    together = {}

    for a, b in combinations(groups, 2):

        # Pair has met somewhere
        meet[a, b] = model.NewBoolVar(f"meet_{a}_{b}")

        meeting_events = [
            X[a, b],  # A hosts B
            X[b, a],  # B hosts A
        ]

        # A and B are co-guests at host h
        for h in groups:
            if h in (a,b):
                continue
            t = model.NewBoolVar(f"together_{h}_{a}_{b}")
            together[h, a, b] = t

            # Replace AddMultiplicationEquality for together
# t is 1 if both X[h,a] and X[h,b] are 1
            model.Add(X[h, a] + X[h, b] - 1 <= t)
            model.Add(t <= X[h, a])
            model.Add(t <= X[h, b])

            meeting_events.append(t)

        #Only one meeting is okey!
        model.Add(
            sum(meeting_events) <= 1
        )

        # meet[a,b] = OR(all meeting events)
        # This is a helper variable for besties and haties: meet[a,b] = 0: they havent met yet, meet[a,b] = 1: they have met already
        model.AddMaxEquality(
            meet[a, b],
            meeting_events
        )
    for a,b in besties:
        a,b = min(a,b), max(a,b)
        model.Add(meet[a,b] == 1)
    for a,b in haties:
        a,b = min(a,b), max(a,b)
        model.Add(meet[a,b] == 0)

    objective = []

    # ----------------------------------------------------
    # 1. Home -> Starter
    # ----------------------------------------------------
    for s in starters:
        for t in groups:
            objective.append(
                distance(s, t) * X[s, t]
            )

    # ----------------------------------------------------
    # 2. Starter -> Main (COMPLETELY FIXED)
    # ----------------------------------------------------
    S = {}
    for t in groups:
        for s in starters:
            for m in mains:
                actual_start_loc = t if t in starters else s
                actual_main_loc = t if t in mains else m
                
                # Correctly evaluate if they are at these locations (either visiting OR hosting)
                is_at_s = 1 if t == s else X[s, t]
                is_at_m = 1 if t == m else X[m, t]

                S[t, s, m] = model.NewBoolVar(f"S_{t}_{s}_{m}")
                
                # Force S to 1 only if they are genuinely at both locations
                model.Add(is_at_s + is_at_m - 1 <= S[t, s, m])
                model.Add(S[t, s, m] <= is_at_s)
                model.Add(S[t, s, m] <= is_at_m)

                # Use the true physical locations for the distance calculation
                objective.append(
                    distance(actual_start_loc, actual_main_loc) * S[t, s, m]
                )

    # ----------------------------------------------------
    # 3. Main -> Dessert (COMPLETELY FIXED)
    # ----------------------------------------------------
    D = {}
    if not no_dessert:
        for t in groups:
            for m in mains:
                for d in desserts:
                    actual_main_loc = t if t in mains else m
                    actual_dessert_loc = t if t in desserts else d
                    
                    # Correctly evaluate if they are at these locations (either visiting OR hosting)
                    is_at_m = 1 if t == m else X[m, t]
                    is_at_d = 1 if t == d else X[d, t]

                    D[t, m, d] = model.NewBoolVar(f"D_{t}_{m}_{d}")
                    
                    model.Add(is_at_m + is_at_d - 1 <= D[t, m, d])
                    model.Add(D[t, m, d] <= is_at_m)
                    model.Add(D[t, m, d] <= is_at_d)

                    # Use the true physical locations for the distance calculation
                    objective.append(
                        distance(actual_main_loc, actual_dessert_loc) * D[t, m, d]
                    )

    # ----------------------------------------------------
    # MINIMIZE
    # ----------------------------------------------------
    model.Minimize(sum(objective))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(solver_time)
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print("Optimal solution found")

    elif status == cp_model.FEASIBLE:
        print("Feasible solution found")

    elif status == cp_model.INFEASIBLE:
        raise RuntimeError("Model is infeasible")

    else:
        print("Status:", solver.StatusName(status))
        raise RuntimeError("No solution found")
    
    routes = {}

    for host in groups:
        guests = []

        for guest in groups:
            if solver.Value(X[host, guest]):
                guests.append(guest)

        routes[host] = tuple(guests)

    print(routes)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("\n" + "="*50)
        print("PERFECT OBJECTIVE VALUE VERIFICATION BREAKDOWN")
        print("="*50)
        
        calculated_total = 0

        # Helper to find where a team ate during a specific round range
        def get_location_for_round(team, round_range):
            # If they are in the host range for this round, they stayed home!
            if team in round_range:
                return team
            # Otherwise, find which host they visited in this round range
            for h in round_range:
                if solver.Value(X[h, team]):
                    return h
            return team

        print("\n--- Round 1: Home -> Starter ---")
        for t in groups:
            start_loc = get_location_for_round(t, starters)
            if start_loc != t: # They traveled to a starter
                weight = distance(t, start_loc)
                calculated_total += weight
                print(f"Team {t:2d}: Home -> Starter Host {start_loc:2d} | Cost: {weight:,}")
            else:
                print(f"Team {t:2d}: Home -> Staying Home to Host Starter | Cost: 0")

        print("\n--- Round 2: Starter -> Main ---")
        for t in groups:
            start_loc = get_location_for_round(t, starters)
            main_loc = get_location_for_round(t, mains)
            
            weight = distance(start_loc, main_loc)
            calculated_total += weight
            
            host_info = "Hosts Main" if main_loc == t else f"Visits Main Host {main_loc}"
            print(f"Team {t:2d}: From Starter {start_loc:2d} -> {host_info:18s} | Cost: {weight:,}")

        if not no_dessert:
            print("\n--- Round 3: Main -> Dessert ---")
            for t in groups:
                main_loc = get_location_for_round(t, mains)
                dessert_loc = get_location_for_round(t, desserts)
                
                weight = distance(main_loc, dessert_loc)
                calculated_total += weight
                
                host_info = "Hosts Dessert" if dessert_loc == t else f"Visits Dessert Host {dessert_loc}"
                print(f"Team {t:2d}: From Main {main_loc:2d} -> {host_info:18s} | Cost: {weight:,}")

        print("\n" + "="*50)
        print(f"Solver Objective Value Reported : {solver.ObjectiveValue():,}")
        print(f"Verified Calculated Total Sum   : {calculated_total:,}")
        print("="*50 + "\n")
    return routes