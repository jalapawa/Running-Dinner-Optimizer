from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def export(manager):

    distribution = manager.get_optimum()
    groups = manager.get_groups()
    mapping = manager.get_map()

    wb = Workbook()
    ws = wb.active

    for col in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        ws.column_dimensions[col].width = 30
    
    yellow_fill = PatternFill(
        fill_type="solid",
        fgColor="FFFF00"
    )

    purple_fill = PatternFill("solid", fgColor="A02B93")
    pink_fill = PatternFill("solid", fgColor="F1CEEE")

    # Header row
    ws.append([
        "Teamname",
        "Adresse der Küche",
        "Wie erreicht man euch im Notfall (Telefonnummer)",
        "Hinweise an die zu bekochenden Gäste (z.B. wie findet man eure Küche, Klingelschild, Stockwerk, Zimmernummer etc.)",
        "Hinweis an die Köche (Allergien, Unverträglichkeiten etc.)",
    ])

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = yellow_fill


    # Group data
    for g in groups:
        ws.append([
            g.teamname,
            g.address,
            g.phone,
            g.guestInfo,
            g.cookInfo,
        ])

    # Two empty rows
    ws.append([])
    ws.append([])

    team1 = ["Vorspeise bei:"]
    team2 = [""]
    team3 = [""]
    # Distribution data
    for key, value in list(distribution.items())[:(len(distribution) // 3)]:
        team1.extend([mapping[key]])
        team2.extend([mapping[value[0]]])
        team3.extend([mapping[value[1]]])
    ws.append(team1)
    for cell in ws[ws.max_row]:
        cell.fill = purple_fill
    ws.append(team2)
    for cell in ws[ws.max_row]:
        cell.fill = pink_fill
    ws.append(team3)
    for cell in ws[ws.max_row]:
        cell.fill = pink_fill

    ws.append([])

    team1 = ["Hauptspeise bei:"]
    team2 = [""]
    team3 = [""]
    # Distribution data
    for key, value in list(distribution.items())[(len(distribution) // 3) : (2 * len(distribution) // 3)]:
        team1.extend([mapping[key]])
        team2.extend([mapping[value[0]]])
        team3.extend([mapping[value[1]]])
    ws.append(team1)
    for cell in ws[ws.max_row]:
        cell.fill = purple_fill
    ws.append(team2)
    for cell in ws[ws.max_row]:
        cell.fill = pink_fill
    ws.append(team3)
    for cell in ws[ws.max_row]:
        cell.fill = pink_fill

    ws.append([])

    team1 = ["Nachspeise bei:"]
    team2 = [""]
    team3 = [""]
    # Distribution data
    for key, value in list(distribution.items())[(2 * len(distribution) // 3):]:
        team1.extend([mapping[key]])
        team2.extend([mapping[value[0]]])
        team3.extend([mapping[value[1]]])
    ws.append(team1)
    for cell in ws[ws.max_row]:
        cell.fill = purple_fill
    ws.append(team2)
    for cell in ws[ws.max_row]:
        cell.fill = pink_fill
    ws.append(team3)
    for cell in ws[ws.max_row]:
        cell.fill = pink_fill

    for cell in ws["A"]:
        cell.font = cell.font.copy(bold=True)

    wb.save("test.xlsx")


