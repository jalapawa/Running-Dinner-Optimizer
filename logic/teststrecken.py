from itertools import combinations
import random


strecken = {(a,b) : random.randint(1, 10) for a,b in combinations(range(1,31), 2)}

print(strecken)