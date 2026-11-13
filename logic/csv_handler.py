import csv
from pathlib import Path
from models.group import Group

# Group field → (keywords that identify its CSV column, label if the column is missing).
# Keywords are matched lower-case as substrings of the header. Order matches the
# Group dataclass, because the groups page pairs keys[i] with the i-th field.
COLUMNS = {
    "personA":   (["vor- und nachname"], "Name"),
    "email":     (["e-mail adresse", "email adresse"], "E-Mail"),
    "personB":   (["kochpartner"], "Kochpartner"),
    "emailB":    (["e-mail vom kochpartner", "email vom kochpartner", "email b", "emailb"], "E-Mail Kochpartner"),
    "teamname":  (["teamname"], "Teamname"),
    "address":   (["adresse der küche"], "Adresse der Küche"),
    "dish":      (["gang"], "Bevorzugter Gang"),
    "phone":     (["notfall", "telefon"], "Telefonnummer"),
    "guestInfo": (["gäste"], "Hinweise an Gäste"),
    "cookInfo":  (["köche"], "Hinweise an Köche"),
    "cleaning":  (["aufräumen"], "Aufräumen helfen?"),
    "further":   (["wünsche", "weiteres", "anmerkungen"], "Weiteres"),
}

# Columns the form may leave out, with the value to use instead.
# Fields not listed here are required.
OPTIONAL = {"emailB": "", "guestInfo": "", "cookInfo": "", "cleaning": "Nein", "further": ""}

# "Kochpartner" is also part of "E-Mail vom Kochpartner", so the partner email
# column has to be claimed before the partner name.
MATCH_ORDER = ["emailB"] + [f for f in COLUMNS if f != "emailB"]


def handleFile(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        groups, keys = row_to_dataclass(reader)
        return groups, keys


def map_columns(headers):
    """Return {field: header or None}, each header used for at most one field."""
    mapping = {}
    claimed = set()
    for field in MATCH_ORDER:
        keywords, _ = COLUMNS[field]
        mapping[field] = None
        for header in headers:
            if header in claimed:
                continue
            name = header.lower()
            if any(keyword in name for keyword in keywords):
                mapping[field] = header
                claimed.add(header)
                break
    return mapping


def row_to_dataclass(reader):
    headers = reader.fieldnames or []
    mapping = map_columns(headers)

    missing = [COLUMNS[f][1] for f, col in mapping.items() if col is None and f not in OPTIONAL]
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))

    # Labels in Group field order: the real header, or a fallback for missing columns
    keys = [mapping[f] or COLUMNS[f][1] for f in COLUMNS]

    groups = []
    for row in reader:
        values = {}
        for field in COLUMNS:
            col = mapping[field]
            values[field] = (row.get(col) or "") if col else OPTIONAL[field]
        groups.append(Group(**values))
    return groups, keys
