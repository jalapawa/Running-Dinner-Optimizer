from pyomo.environ import *
from itertools import permutations, product, combinations
import teststrecken


anzahlGruppen = 30
cutStarter = (anzahlGruppen // 3) + 1
cutMain = 2 * (anzahlGruppen// 3) + 1
cutDessert = anzahlGruppen + 1

m = ConcreteModel()


m.Groups = Set(initialize=range(1, anzahlGruppen + 1))  # 1..30
m.X = Var(m.Groups, m.Groups, domain=Binary)  # or NonNegativeReals, depending
Pairs = list(permutations(m.Groups, 2))
m.Y = Var(Pairs, domain=Binary) #We use this to track which pairs have seen eachother already
m.Z1 = Var(Pairs, domain=Binary) #This is to keep track of the route (namely starter -> main)
m.Z2 = Var(Pairs, domain=Binary) #This is to keep track of the route (namely main -> dessert)


#m.X[1, 16] -> ref
#m.X[1, 16].value -> 1/0

def distance(a, b):
    return teststrecken.strecken[min(a,b), max(a,b)]

m.obj = Objective(
    expr=sum(distance(x,y) * m.X[x,y] for x in range(1, cutStarter) for y in range(cutStarter, cutDessert)) #Strecken erstmal zur Vorspeise zu kommen
        + sum(distance(s,y) * m.Z1[s,y] for s,y in ([(x, y) for x, y in product(range(1, cutStarter), range(1, cutDessert)) if x != y])) #Wenn jemand von starter s zu hauptspeise y will, wird m.Z1[s,y] true sein
        + sum(distance(main,y) * m.Z2[main,y] for main,y in ([(x, y) for x, y in product(range(cutStarter, cutMain), range(1, cutDessert)) if x != y]))
    ,
    sense=minimize
)

#Constraints for objective funciton
#x will zu y, ist aber gerade bei Starter s

m.strecke1 = ConstraintList()
for s in range(1, cutStarter):
    for x in range(1, cutDessert):
        for y in range(cutStarter, cutMain):
            m.strecke1.add(m.X[s,y] + m.X[x, y] - m.Z1[s,y] <= 1)
           
m.strecke2 = ConstraintList()
for main in range(cutStarter, cutMain):
    for x in range(1, cutDessert):
        for y in range(cutMain, cutDessert):
            m.strecke2.add(m.Z1[main,y] + m.X[x, y] - m.Z2[s,y] <= 1)



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




#Jede group darf für einen bestimmten Guest genau einmal kochen oder bekocht werden
#Dann fehlen nur noch dreiecksbeziehungen (Y)
m.no_repetitions = ConstraintList()
for group,guest in permutations(m.Groups, 2):
    m.no_repetitions.add(m.X[group, guest] + m.X[guest, group] + m.Y[guest, group] <= 1)

#Dreiecksbeziehungen: Wenn leute mal bekocht wurden von einer anderen Gruppe:
#Dann ist m.Y[guest1, guest2] == 1
#Was dann nicht gehen sollte: dass die wieder zusammen irgendwo anders bekocht werden
#ODER dass die sich hosten/gehostet werden
#Die machen alle kein Sinn, kontradiktieren sich gegenseitig :O
m.seen_eachother = ConstraintList()
for host in m.Groups:
    for guest1, guest2 in Pairs:
        m.seen_eachother.add(m.X[host,guest1] + m.X[host,guest2] - m.Y[guest1,guest2] <= 1)

#Eigentlich sogar noch zu schwacher constraint, checkt nicht ob host und guest sich schonmal gesehen haben
#Einmal sehen muss okey sein (das glaube das provlem aktuell)
#Sorgt dafür, dass die nicht zwei mal die gleichen Gäste irgendwo aufkreuzen
#Für das was es macht ist es MIT ABSTAND AM FETTESTEN von den constraints her,
#Consider removing to speed up

m.no_repeat = ConstraintList()

for A in m.Groups:
    for D in m.Groups:
        if D == A:
            continue
        for B, C in combinations(m.Groups, 2):
            m.no_repeat.add(
                m.X[D,B] + m.X[D,C] <= 2 - (m.X[A,B] + m.X[A,C] - 1)
            )


solver = SolverFactory('highs')  # or 'gurobi', 'highs', etc.
results = solver.solve(m, tee=True)

if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
    print("Solver found optimal solution")
elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Model is infeasible")
else:
    print("Solver status:", results.solver.status)


for h in m.Groups:
    for g in m.Groups:
        print(f"X[{h},{g}] = {m.X[h,g].value}")

print("Vorspeisen: ")
for i in range(1,cutStarter):
    print("#######")
    print(f"{i}:")
    for j in range(1, anzahlGruppen + 1):
        if m.X[i,j].value > 0.5:
            print(j)
    print("########")
print("Hauptspeisen: ")
for i in range(cutStarter,cutMain):
    print("#######")
    print(f"{i}:")
    for j in range(1, anzahlGruppen + 1):
        if m.X[i,j].value > 0.5:
            print(j)
    print("########")
print("Nachspeisen: ")
for i in range(cutMain,cutDessert):
    print("#######")
    print(f"{i}:")
    for j in range(1, anzahlGruppen + 1):
        if m.X[i,j].value > 0.5:
            print(j)
    print("########")

print("Objective value:", m.obj())
