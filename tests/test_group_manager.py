from logic.group_manager import GroupManager
from models.group import Group


def make_group(teamname, dish):
    # Only teamname and dish matter here; the rest is filler
    return Group("A", "a@x.de", "B", "b@x.de", teamname, "Street 1", dish, "0123")


def test_distribute_assigns_egal_to_missing_dish():
    manager = GroupManager()
    manager.set_groups([
        make_group("Team1", "Vorspeise"),
        make_group("Team2", "Hauptspeise"),
        make_group("Team3", "Egal"),
    ])

    manager.distribute()

    assert manager.get_groups()[2].dish == "Nachspeise"
