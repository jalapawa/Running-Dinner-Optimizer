from typing import List, Dict
from models.group import Group

class GroupManager:
    def __init__(self):
        self.groups: List = []
        self.group_id_map: Dict = {}
        self.keys = []
        self.optimum = {}
        self.haties: List = []
        self.besties: List = []

    def to_dict(self):
        return {
            "groups": [group.to_dict() for group in self.groups],
            "group_id_map": self.group_id_map,
            "keys": self.keys,
            "optimum": self.optimum,
            "haties": self.haties,
            "besties": self.besties
        }
    
    def from_dict(self, data):

        self.groups = [
            Group(**g)
            for g in data["groups"]
        ]

        self.group_id_map = data["group_id_map"]
        self.keys = data["keys"]
        self.optimum = data["optimum"]
        self.haties = data["haties"]
        self.besties = data["besties"]

    def set_groups(self, group_list: List):
        """Replace current rows with new ones."""
        self.groups = group_list

    def set_keys(self, key_list: List):
        self.keys = key_list

    def get_groups(self) -> List:
        """Return all stored rows."""
        return self.groups
    
    def get_map(self) -> List:
        return self.group_id_map
    
    def get_keys(self) -> List:
        return self.keys
    
    def get_optimum(self):
        return self.optimum
    
    def set_optimum(self, optimum):
        self.optimum = optimum
        self.create_route()

    def create_route(self):
        if self.optimum:
            routes = [[k for k, vals in self.optimum.items() if i in vals] for i in range(1,len(self.groups)+1)]
            for i in range(len(self.groups)):
                routes[i].insert(i // 3, i+1)
            for g in self.groups:
                g.route = routes[g.id-1]
            

    def add_group(self, group):
        """Add a single row."""
        self.groups.append(group)

    def add_besties(self, groupA, groupB):
        self.besties.append(
            ((next((p for p in self.groups if p.teamname == groupA), None)),
            (next((p for p in self.groups if p.teamname == groupB), None)))
        )

    def add_haties(self, groupA, groupB):
        self.haties.append(
            ((next((p for p in self.groups if p.teamname == groupA), None)),
            (next((p for p in self.groups if p.teamname == groupB), None)))
        )

    def get_besties(self):
        return self.besties
    
    def get_haties(self):
        return self.haties
    
    def del_besties(self, pairing):
        match = next((p for p in self.besties if p[0].teamname == pairing.split(" : ")[0] and p[1].teamname == pairing.split(" : ")[1]), None)
        self.besties.remove(match)


    def del_haties(self, pairing):
        match = next((p for p in self.besties if p[0].teamname == pairing.split(" : ")[0] and p[1].teamname == pairing.split(" : ")[1]), None)
        self.haties.remove(match)

    def delete_group(self, teamname):
        match = next((p for p in self.groups if p.teamname == teamname), None)
        self.groups.remove(match)


    def change_dish(self, team, newdish):
        match = next((p for p in self.groups if p.teamname == team), None)
        match.dish = newdish

    #Can be made MUCHHH more efficient (only one run, saving indixes of egal, distributing better)
    def distribute(self):
        count_vorspeise = 0
        count_hauptspeise = 0
        count_nachspeise = 0
        count_egal = 0

        for g in self.groups:
            if g.dish == "Vorspeise":
                count_vorspeise += 1
            elif g.dish == "Hauptspeise":
                count_hauptspeise += 1
            elif g.dish == "Nachspeise":
                count_nachspeise += 1
            elif g.dish == "Egal":
                count_egal += 1
        
        if count_egal > 0:
            for g in self.groups:
                if g.dish == "Egal":
                    if count_vorspeise < count_hauptspeise:
                        if count_vorspeise < count_nachspeise:
                            g.dish = "Vorspeise"
                            count_vorspeise += 1
                        else:
                            g.dish = "Nachspeise"
                            count_nachspeise += 1
                    else:
                        if count_hauptspeise < count_nachspeise:
                            g.dish = "Hauptspeise"
                            count_hauptspeise += 1
                        else:
                            g.dish = "Nachspeise"
                            count_nachspeise += 1
    
    def assign_ids(self):
        starter_id = 1
        main_id = (len(self.groups) // 3) + 1 
        dessert_id = 2 * (len(self.groups)// 3) + 1
        for group in self.groups:
            match group.dish:
                case "Vorspeise":
                    group.id = starter_id
                    starter_id += 1
                case "Hauptspeise":
                    group.id = main_id
                    main_id += 1
                case "Nachspeise":
                    group.id = dessert_id
                    dessert_id += 1
            self.group_id_map[group.id] = group.teamname
            self.group_id_map[group.teamname] = group.id