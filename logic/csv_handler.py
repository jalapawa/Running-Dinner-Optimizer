import csv
from pathlib import Path
from models.group import Group

def handleFile(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        groups, keys = row_to_dataclass(reader)
        return groups, keys
    

def row_to_dataclass(reader):
    groups = []
    init = True
    keys = []
    for row in reader:
        if init:
            keys = list(row.keys())[1:]
            init = False
        group = Group(*[row[h] for h in keys])
        groups.append(group)
    return groups, keys