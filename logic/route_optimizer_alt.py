from pyomo.environ import *

def optimize(totalGroups, distances, besties, haties):

    anzahlGruppen = totalGroups
    cutStarter = (anzahlGruppen // 3) + 1  # Hosts Starters
    cutMain = 2 * (anzahlGruppen // 3) + 1  # Hosts Mains
    cutDessert = anzahlGruppen + 1         # Hosts Desserts

    m = ConcreteModel()

    starters = range(1, cutStarter)
    mains = range(cutStarter, cutMain)
    desserts = range(cutMain, cutDessert)
    all_teams = range(1, cutDessert)

    # Cleanly generate paths without causing UnboundLocalErrors
    starter_paths = [(y, y, main, d) for y in starters for main in mains for d in desserts]
    main_paths = [(y, s, y, d) for y in mains for s in starters for d in desserts]
    dessert_paths = [(y, s, main, y) for y in desserts for s in starters for main in mains]

    valid_combinations = starter_paths + main_paths + dessert_paths
    # Convert to set for lightning-fast lookups in constraints
    valid_set = set(valid_combinations)

    # Define the decision variable
    m.Y = Var(valid_combinations, domain=Binary)

    # Static calculation of path distances
    def get_path_distance(y, s, main, d):
        # Calculates: Home -> Starter -> Main -> Dessert -> Home
        # (If they are hosting, distance automatically calculates as 0 where appropriate)
        return (distances[min(y, s), max(y, s)] + 
                distances[min(s, main), max(s, main)] + 
                distances[min(main, d), max(main, d)] + 
                distances[min(d, y), max(d, y)])

    m.obj = Objective(
        expr=sum(get_path_distance(y, s, main, d) * m.Y[y, s, main, d] for y, s, main, d in valid_combinations),
        sense=minimize
    )

    m.constraints = ConstraintList()

    # Rule A: Every team must have exactly one path for the evening
    for y in all_teams:
        m.constraints.add(sum(m.Y[_y, s, main, d] for _y, s, main, d in valid_combinations if _y == y) == 1)

    # Rule B: Perfect Mixing (No two teams can meet twice)
    for y1 in all_teams:
        for y2 in all_teams:
            if y1 < y2:
                # They can't share a starter AND a main
                for s in starters:
                    for main in mains:
                        # Only add variables if the paths actually exist in our filtered list
                        y1_paths = [m.Y[y1, s, main, d] for d in desserts if (y1, s, main, d) in valid_set]
                        y2_paths = [m.Y[y2, s, main, d] for d in desserts if (y2, s, main, d) in valid_set]
                        if y1_paths and y2_paths:
                            m.constraints.add(sum(y1_paths) + sum(y2_paths) <= 1)

                # They can't share a main AND a dessert
                for main in mains:
                    for d in desserts:
                        y1_paths = [m.Y[y1, s, main, d] for s in starters if (y1, s, main, d) in valid_set]
                        y2_paths = [m.Y[y2, s, main, d] for d in starters if (y2, s, main, d) in valid_set]
                        if y1_paths and y2_paths:
                            m.constraints.add(sum(y1_paths) + sum(y2_paths) <= 1)
                
                for starter in starters:
                    for d in desserts:
                        y1_paths = [m.Y[y1, s, main, d] for s in starters if (y1, s, main, d) in valid_set]
                        y2_paths = [m.Y[y2, s, main, d] for d in starters if (y2, s, main, d) in valid_set]
                        if y1_paths and y2_paths:
                            m.constraints.add(sum(y1_paths) + sum(y2_paths) <= 1)


    #Solver
    solver = SolverFactory('highs')  # or 'gurobi', 'highs', etc.
    results = solver.solve(m, tee=True)

    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        print("Solver found optimal solution")
    elif results.solver.termination_condition == TerminationCondition.infeasible:
        print("Model is infeasible")
        raise RuntimeError("Optimization failed")
    else:
        print("Solver status:", results.solver.status)
    # Output tracking
    routes = {}
    for y, s, main, d in valid_combinations:
        # Check if the variable is defined and evaluated
        if m.Y[y, s, main, d].value is not None and m.Y[y, s, main, d].value > 0.5:
             routes[y] = (s, main) if d == y else ((s, d) if main == y else (main,d)) 
            
    print(routes)