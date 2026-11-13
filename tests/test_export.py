from urllib.parse import quote

import matplotlib
import pytest
from openpyxl import load_workbook

matplotlib.use("Agg")  # no window during tests

from logic import export as export_module
from models.group import Group


class FakeManager:
    """Three teams, each visiting the other two (1-based ids)."""

    def __init__(self):
        self.groups = []
        for i, name in enumerate(["T1", "T2", "T3"], start=1):
            g = Group("A", "a@x.de", "B", "", name, f"Street {i}", "Egal", "0123")
            g.id = i
            g.route = [1, 2, 3]
            self.groups.append(g)

    def get_groups(self):
        return self.groups

    def get_optimum(self):
        return {1: (2, 3), 2: (1, 3), 3: (1, 2)}

    def get_map(self):
        return {1: "T1", 2: "T2", 3: "T3"}


def route_link(tmp_path, afterparty):
    config = {"afterpartylocation": afterparty, "city": "Aachen", "no_dessert": False}
    path = tmp_path / "out.xlsx"
    export_module.export(FakeManager(), config, path)
    return load_workbook(path).active["F2"].hyperlink.target


@pytest.fixture(autouse=True)
def no_plot_window(monkeypatch):
    monkeypatch.setattr(export_module.plt, "show", lambda: None)


def test_route_ends_at_afterparty(tmp_path):
    link = route_link(tmp_path, "Trichtergasse 24")

    assert link.endswith(quote("Trichtergasse 24, Aachen"))


@pytest.mark.parametrize("afterparty", ["", "   "])
def test_empty_afterparty_is_left_out_of_route(tmp_path, afterparty):
    link = route_link(tmp_path, afterparty)

    # Own kitchen + three courses, no extra stop
    assert link.count("/") - "https://www.google.com/maps/dir/".count("/") == 3
    assert link.endswith(quote("Street 3, Aachen"))
