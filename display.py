# util/display.py
import sys
from constants import BOX_WIDTH, ROW_HEADER_WIDTH, DICE_ART, COLUMN_TYPES, BOX_TYPES, BORDERS

def draw_game(game):
    sys.stdout.write("\033c")
    draw_dices(game.dices)
    sys.stdout.write("\n")
    draw_sheet(game.sheet)
    sys.stdout.flush()

def draw_dices(dices):
    dices_representation = ['' for _ in range(5)]
    for i in range(5):
        for j, line in enumerate(DICE_ART[dices[i].value]):
            dices_representation[j] += line + '  '
    sys.stdout.write('\n'.join(dices_representation))

def draw_sheet(sheet):
    column_headers = " ".join(f"{label:^{BOX_WIDTH}}" for label in COLUMN_TYPES)
    header_row = f"{'':^{ROW_HEADER_WIDTH + 3}}{column_headers}"
    lines = [header_row, BORDERS["border_top"]]

    top_sum = sheet.get_top_sum()
    middle_difference = sheet.get_middle_difference()
    bottom_sum = sheet.get_bottom_sum()

    column_totals = [top + mid + bottom for top, mid, bottom in zip(top_sum, middle_difference, bottom_sum)]
    grand_total = sum(column_totals)

    for row_idx, label in enumerate(BOX_TYPES):
        if row_idx == 6:
            lines.append(format_total_row('Σ(1-6)', top_sum))
            lines.append(BORDERS["long_border_bottom"])
        elif row_idx == 8:
            lines.append(format_total_row('Δ', middle_difference))
            lines.append(BORDERS["long_border_bottom"])
        
        row = "│".join(f"{column.boxes[row_idx].value if column.boxes[row_idx].value is not None else ' ':^{BOX_WIDTH}}" for column in sheet.columns)
        row = f"  {label:<{ROW_HEADER_WIDTH}} │{row}│"
        lines.append(row)
        
        if row_idx in [5, 7, 12]:
            lines.append(BORDERS["long_border_top"])
        else:
            lines.append(BORDERS["border"])

    lines.append(format_total_row('Σ', bottom_sum))
    lines.append(BORDERS["long_border_bottom_final"])

    grand_total_row = f"{'':^{(ROW_HEADER_WIDTH + 3) + (BOX_WIDTH + 1) * 3}}│{grand_total:^{BOX_WIDTH * 2 + 1}}│"
    lines.append(grand_total_row)
    lines.append(BORDERS["border_bottom_final"])

    sys.stdout.write("\n".join(lines))

def format_total_row(label, values):
    total_sum = sum(values)
    return f"│{label:^{ROW_HEADER_WIDTH + 2}}│" + "│".join(f"{value:^{BOX_WIDTH}}" for value in values) + f"│{total_sum:^{BOX_WIDTH}}│"
