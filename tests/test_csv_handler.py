import pytest

from logic.csv_handler import handleFile

HEADER_WITH_EMAIL_B = (
    "Zeitstempel,Vor- und Nachname,E-Mail Adresse,Kochpartner,E-Mail vom Kochpartner,"
    "Teamname,Adresse der Küche,Bevorzugter Gang,Wie erreicht man euch im Notfall?,"
    "Hinweise an die Gäste,Hinweis an die Köche,Aufräumen helfen?,Wünsche"
)
ROW_WITH_EMAIL_B = (
    "1/1/2026,Anna A,anna@x.de,Ben B,ben@x.de,"
    "Team Pasta,Hauptstr. 1,Vorspeise,0123,2. Stock,vegan,Ja,"
)

HEADER_WITHOUT_EMAIL_B = (
    "Zeitstempel,Vor- und Nachname,E-Mail Adresse,Kochpartner,"
    "Teamname,Adresse der Küche,Bevorzugter Gang,Wie erreicht man euch im Notfall?,"
    "Hinweise an die Gäste,Hinweis an die Köche,Aufräumen helfen?,Wünsche"
)
ROW_WITHOUT_EMAIL_B = (
    "1/1/2026,Anna A,anna@x.de,Ben B,"
    "Team Pasta,Hauptstr. 1,Vorspeise,0123,2. Stock,vegan,Ja,"
)


def write_csv(tmp_path, header, row):
    path = tmp_path / "form.csv"
    path.write_text(header + "\n" + row + "\n", encoding="utf-8")
    return path


def test_reads_partner_email_column(tmp_path):
    groups, _ = handleFile(write_csv(tmp_path, HEADER_WITH_EMAIL_B, ROW_WITH_EMAIL_B))

    group = groups[0]
    assert group.personB == "Ben B"
    assert group.emailB == "ben@x.de"
    assert group.teamname == "Team Pasta"


def test_partner_email_column_is_optional(tmp_path):
    groups, _ = handleFile(write_csv(tmp_path, HEADER_WITHOUT_EMAIL_B, ROW_WITHOUT_EMAIL_B))

    group = groups[0]
    assert group.emailB == ""
    # The columns after the missing one must not shift
    assert group.teamname == "Team Pasta"
    assert group.address == "Hauptstr. 1"
    assert group.dish == "Vorspeise"
    assert group.phone == "0123"


def test_keys_stay_in_group_field_order(tmp_path):
    _, keys = handleFile(write_csv(tmp_path, HEADER_WITHOUT_EMAIL_B, ROW_WITHOUT_EMAIL_B))

    assert keys[1] == "E-Mail Adresse"
    assert keys[3] == "E-Mail Kochpartner"  # fallback label for the missing column
    assert keys[4] == "Teamname"


@pytest.mark.parametrize("header", ["Email B", "EmailB", "E-Mail vom Kochpartner"])
def test_partner_email_header_variants(tmp_path, header):
    groups, _ = handleFile(write_csv(
        tmp_path,
        HEADER_WITH_EMAIL_B.replace("E-Mail vom Kochpartner", header),
        ROW_WITH_EMAIL_B,
    ))

    assert groups[0].personB == "Ben B"
    assert groups[0].emailB == "ben@x.de"


def test_missing_required_column_raises(tmp_path):
    header = HEADER_WITHOUT_EMAIL_B.replace("Teamname,", "")
    row = ROW_WITHOUT_EMAIL_B.replace("Team Pasta,", "")

    with pytest.raises(ValueError, match="Teamname"):
        handleFile(write_csv(tmp_path, header, row))
