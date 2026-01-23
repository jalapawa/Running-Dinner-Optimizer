from typing import List

class GroupManager:
    def __init__(self):
        self.groups: List = [] 

    def set_groups(self, group_list: List):
        """Replace current rows with new ones."""
        self.groups = group_list

    def get_groups(self) -> List:
        """Return all stored rows."""
        print(self.groups)
        return self.groups

    def add_group(self, group):
        """Add a single row."""
        self.groups.append(group)

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