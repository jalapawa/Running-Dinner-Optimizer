from pyomo.environ import *
from itertools import permutations, product, combinations

def optimize(totalGroups, distances, besties, haties):

    def distance(a, b):
        return distances[min(a,b), max(a,b)]

    anzahlGruppen = totalGroups
    cutStarter = (anzahlGruppen // 3) + 1 # Hosts Starters
    cutMain = 2 * (anzahlGruppen// 3) + 1 # Hosts Mains
    cutDessert = anzahlGruppen + 1 # Hosts Desserts

    m = ConcreteModel()

    #Maybe improve this to make it more einheitlich?
    m.Groups = Set(initialize=range(1, anzahlGruppen + 1)) #Groups 
    m.X = Var(m.Groups, m.Groups, domain=Binary)  #X[A,B]: A hosts group B
    Pairs = list(permutations(m.Groups, 2)) #Possible mappings (A,B)
    m.Y = Var(Pairs, domain=Binary) #We use this to track which pairs have seen eachother already
    m.Z1 = Var(Pairs, domain=Binary) #This is to keep track of the route (namely starter -> main)
    m.Z2 = Var(Pairs, domain=Binary) #This is to keep track of the route (namely main -> dessert)



    #Objective function:
    #First: sum of distance from people to their respective Starter Places
    #Second: sum of distance from people at Starters to their Main courses
    #Third: sum of distance for people at Mains to Desserts
    #Note: to Party not necessary as everyone has to go anyway
    m.obj = Objective(
        expr=sum(distance(x,y) * m.X[x,y] for x in range(1, cutStarter) for y in range(cutStarter, cutDessert)) #Strecken erstmal zur Vorspeise zu kommen
            + sum(distance(s,y) * m.Z1[s,y] for s,y in ([(x, y) for x, y in product(range(1, cutStarter), range(1, cutDessert)) if x != y])) #Wenn jemand von starter s zu hauptspeise y will, wird m.Z1[s,y] true sein
            + sum(distance(main,y) * m.Z2[main,y] for main,y in ([(x, y) for x, y in product(range(cutStarter, cutMain), range(1, cutDessert)) if x != y]))
        ,
        sense=minimize
    )

    #Used for the distance starter -> main
    m.strecke1 = ConstraintList()
    for s in range(1, cutStarter):
        for x in range(1, cutDessert):
            for y in range(cutStarter, cutMain):
                m.strecke1.add(m.X[s,y] + m.X[x, y] - m.Z1[s,y] <= 1)
            
    #Used for distance main -> dessert
    m.strecke2 = ConstraintList()
    for main in range(cutStarter, cutMain):
        for x in range(1, cutDessert):
            for y in range(cutMain, cutDessert):
                m.strecke2.add(m.Z1[main,y] + m.X[x, y] - m.Z2[main,y] <= 1) #IS THAT NOT FULLY WRONG?!



    #Constraints fr
    #Two guests per group
    def two_guests_per_group(m, g1):
        return sum(m.X[g1, g2] for g2 in m.Groups) == 2

    m.two_guests = Constraint(m.Groups, rule=two_guests_per_group) #Loops through m.groups and adds the constraint for each one (g1)

    #Everyone is a guest twice
    def two_meals_per_group(m, g1):
        return sum(m.X[g2, g1] for g2 in m.Groups) == 2

    m.two_meals = Constraint(m.Groups, rule=two_meals_per_group) #Loops through m.groups and adds the constraint for each one (g1)

    #A starter cant sit with a starter
    def no_double_starter(m, g1):
        return sum(m.X[g1, g2] for g2 in range(1, cutStarter)) == 0

    m.no_double_starter = Constraint(range(1, cutStarter), rule=no_double_starter)

    #A main cant sit with a main
    def no_double_main(m, g1):
        return sum(m.X[g1, g2] for g2 in range(cutStarter, cutMain)) == 0

    m.no_double_main = Constraint(range(cutStarter, cutMain), rule=no_double_main)

    #A dessert cant sit with a dessert
    def no_double_dessert(m, g1):
        return sum(m.X[g1, g2] for g2 in range(cutMain,cutDessert)) == 0

    m.no_double_dessert = Constraint(range(cutMain, cutDessert), rule=no_double_dessert)

    #No self assignment of dishes
    m.no_self = ConstraintList()
    for group in m.Groups:
        m.no_self.add(m.X[group, group] == 0)

    #A starter cant sit with a starter
    def each_starter(m, g1):
        return sum(m.X[g2, g1] for g2 in range(1, cutStarter)) == 1

    m.each_starter = Constraint(range(cutStarter, cutDessert), rule=each_starter)

    #A main cant sit with a main
    def each_main(m, g1):
        return sum(m.X[g2, g1] for g2 in range(cutStarter, cutMain)) == 1

    m.each_main = Constraint(list(range(1, cutStarter)) + list(range(cutMain, cutDessert)), rule=each_main)

    #A dessert cant sit with a dessert
    def each_starter(m, g1):
        return sum(m.X[g2, g1] for g2 in range(cutMain, cutDessert)) == 1

    m.each_starter = Constraint(range(1, cutMain), rule=each_starter)

    #Old linking of Guest1 and Guest2
    #Constraint: Y[guest1, guest2] will be 1 if guest1 and guest2 have been guests together at a host
    # m.seen_eachother = ConstraintList()
    # for host in m.Groups:
    #     for guest1, guest2 in Pairs:
    #         m.seen_eachother.add(m.X[host,guest1] + m.X[host,guest2] - m.Y[guest1,guest2] <= 1)

    # 1. Define the helper variable W
    # W[host, guest1, guest2] is 1 ONLY if BOTH guests are at that specific host
    m.W = Var(m.Groups, Pairs, domain=Binary)

    m.link_W = ConstraintList()
    m.link_Y_lower = ConstraintList()
    m.link_Y_upper = ConstraintList()

    for guest1, guest2 in Pairs:
        for host in m.Groups:
            # Constraints to force W to 0 if either guest is missing from this host
            m.link_W.add(m.W[host, guest1, guest2] <= m.X[host, guest1])
            m.link_W.add(m.W[host, guest1, guest2] <= m.X[host, guest2])
            
            # Force W to 1 if BOTH guests are at this host
            m.link_W.add(m.X[host, guest1] + m.X[host, guest2] - m.W[host, guest1, guest2] <= 1)
            
            # Force Y to 1 if they are together at ANY host
            m.link_Y_lower.add(m.Y[guest1, guest2] >= m.W[host, guest1, guest2])

        # Force Y to 0 if the sum of all their shared hosts is 0
        m.link_Y_upper.add(m.Y[guest1, guest2] <= sum(m.W[h, guest1, guest2] for h in m.Groups))


    #Constraint: Each group can only host another group or be hosted by another group at the same time (m.X[group, guest] + m.X[guest, group])
    #            Also, the group host and group could not have been the two guests at another host earlier (Y[guest, grop])
    m.no_repetitions = ConstraintList()
    for group,guest in permutations(m.Groups, 2):
        m.no_repetitions.add(m.X[group, guest] + m.X[guest, group] + m.Y[guest, group] <= 1)


    #Constraint: Two groups that were guests together cannot be guests together later again
    m.no_repeat = ConstraintList()
    for host1 in m.Groups:
        for host2 in m.Groups:
            if host1 == host2:
                continue
            for guest1, guest2 in combinations(m.Groups, 2):
                m.no_repeat.add(
                    m.X[host1,guest1] + m.X[host1,guest2] <= 2 - (m.X[host2,guest1] + m.X[host2,guest2] - 1)
                )


    ##EXTRAS: Besties und HAties
    m.besties = ConstraintList()
    for team1, team2 in besties:
        m.besties.add(m.X[team1, team2] + m.X[team2, team1] + m.Y[team1, team2] + m.Y[team2, team1] >= 1)

    m.haties = ConstraintList()
    for team1, team2 in haties:
        m.haties.add(m.X[team1, team2] + m.X[team2, team1] + m.Y[team1, team2] + m.Y[team2, team1] == 0)


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


    routes = {}
    for i in range(1, anzahlGruppen + 1):
        guests = []
        for j in range(1, anzahlGruppen + 1):
            if m.X[i,j].value > 0.5:
                guests.append(j)
        routes[i] = (guests[0], guests[1])

    return routes