import csv
from pathlib import Path
from openpyxl import load_workbook
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

def extract_repetitions(path):
    """Return historic meeting pairs as ``[(address_a, address_b), ...]``.

    The exported XLSX starts with the team/address table.  At its end, each
    ``<course> bei:`` row and the following two rows form the distribution:
    every column is one three-team meeting.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if path.suffix.lower() != ".xlsx":
        raise ValueError("Please select an Excel (.xlsx) export file.")

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        worksheet = workbook.active
        rows = [
            ["" if cell is None else str(cell).strip() for cell in row]
            for row in worksheet.iter_rows(values_only=True)
        ]
    finally:
        workbook.close()

    if not rows:
        return []

    try:
        header = rows[0]
        team_column = header.index("Teamname")
        address_column = header.index("Adresse der Küche")
    except ValueError as error:
        raise ValueError(
            "The Excel export must contain the columns 'Teamname' and 'Adresse der Küche'."
        ) from error

    addresses_by_team = {}
    for row in rows[1:]:
        if not any(row):
            break
        if len(row) <= max(team_column, address_column):
            continue
        team, address = row[team_column], row[address_column]
        if team and address:
            addresses_by_team[team] = address

    course_rows = {"Vorspeise bei:", "Hauptspeise bei:", "Nachspeise bei:"}
    repetitions = []

    for row_index, hosts in enumerate(rows):
        if not hosts or hosts[0] not in course_rows:
            continue
        if row_index + 2 >= len(rows):
            raise ValueError(f"Incomplete distribution after '{hosts[0]}'.")

        first_guests = rows[row_index + 1]
        second_guests = rows[row_index + 2]
        for column in range(1, len(hosts)):
            triplet = [
                hosts[column],
                first_guests[column] if column < len(first_guests) else "",
                second_guests[column] if column < len(second_guests) else "",
            ]
            if not any(triplet):
                continue
            if not all(triplet):
                raise ValueError(
                    f"Incomplete group triplet in '{hosts[0]}' column {column}."
                )

            try:
                triplet_addresses = [addresses_by_team[team].split(",")[0] for team in triplet]
            except KeyError as error:
                raise ValueError(
                    f"Team '{error.args[0]}' appears in the distribution but not in the team table."
                ) from error

            repetitions.extend([
                (triplet_addresses[0], triplet_addresses[1]),
                (triplet_addresses[0], triplet_addresses[2]),
                (triplet_addresses[1], triplet_addresses[2]),
            ])

    return repetitions
