from ortools.sat.python import cp_model
from itertools import permutations, combinations

def optimize(totalGroups, distances, besties, haties, solver_time):
    
    def distance(a, b):
        return distances[min(a, b), max(a, b)]

    anzahlGruppen = totalGroups
    cutStarter = (anzahlGruppen // 3) + 1 
    cutMain = 2 * (anzahlGruppen // 3) + 1 
    cutDessert = anzahlGruppen + 1          

    model = cp_model.CpModel()

    groups = range(1, anzahlGruppen + 1)
    starters = range(1, cutStarter)
    mains = range(cutStarter, cutMain)
    desserts = range(cutMain, cutDessert)

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
    ### REDUNDANT BECAUSE OF THE NEXT CONS?
    # #No starter at starter
    # for host in starters:
    #     for guest in starters:
    #         model.Add(X[host, guest] == 0)
    # #No main at main
    # for host in mains:
    #     for guest in mains:
    #         model.Add(X[host, guest] == 0)
    # #No dessert at dessert
    # for host in desserts:
    #     for guest in desserts:
    #         model.Add(X[host, guest] == 0)
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

            model.AddMultiplicationEquality(
                t,
                [X[h, a], X[h, b]]
            )

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

    #S
    S = {}
    for t in groups:
        for s in starters:
            for m in mains:
                S[t,s,m] = model.NewBoolVar(f"S_{t}_{s}_{m}")

                model.AddMultiplicationEquality(
                    S[t,s,m],
                    [X[s,t], X[m,t]]
                )
    #D
    D = {}
    for t in groups:
        for m in mains:
            for d in desserts:
                D[t,m,d] = model.NewBoolVar(f"D_{t}_{m}_{d}")

                model.AddMultiplicationEquality(
                    D[t,m,d],
                    [X[m,t], X[d,t]]
                )
    objective = []

    # Home -> starter
    for s in starters:
        for t in groups:
            objective.append(
                distance(s,t) * X[s,t]
            )

    # Starter -> main
    for t in groups:
        for s in starters:
            for m in mains:
                objective.append(
                    distance(s,m) * S[t,s,m]
                )

    # Main -> dessert
    for t in groups:
        for m in mains:
            for d in desserts:
                objective.append(
                    distance(m,d) * D[t,m,d]
                )

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
    return routes