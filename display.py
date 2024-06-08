import sys
import time
from constants import BOX_WIDTH, ROW_HEADER_WIDTH, DICE_ART, COLUMN_TYPES, BOX_TYPES, BORDERS

def render_stats(iteration, total, highest_score, avg_episode_time, length=50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    remaining_episodes = total - iteration
    estimated_time_left = remaining_episodes * avg_episode_time
    eta = time.strftime("%H:%M:%S", time.gmtime(estimated_time_left))
    print(f'\rProgress: |{bar}| {percent}% Complete ({iteration}/{total}) | Highest Score: {highest_score} | ETA: {eta}', end='\r')
    if iteration == total:
        print()  # New line at the end of the progress

def render_game(game):
    # sys.stdout.write("\033c")
    if game["announcement"] != -1:
        sys.stdout.write(f"Announcement: {BOX_TYPES[game["announcement"]]}\n")
    render_dices(game["dices"])
    sys.stdout.write("\n")
    render_sheet(game["sheet"])
    sys.stdout.flush()

def render_dices(dices):
    dices_representation = ['' for _ in range(5)]
    for i in range(5):
        for j, line in enumerate(DICE_ART[dices[i]]):
            dices_representation[j] += line + '  '
    sys.stdout.write('\n'.join(dices_representation))

def render_sheet(sheet):
    column_headers = " ".join(f"{label:^{BOX_WIDTH}}" for label in COLUMN_TYPES)
    header_row = f"{'':^{ROW_HEADER_WIDTH + 3}}{column_headers}"
    lines = [header_row, BORDERS["border_top"]]

    top_sum = [sum(col[:6]) for col in sheet]
    middle_difference = [col[6] - col[7] if col[6] != -1 and col[7] != -1 else 0 for col in sheet]
    bottom_sum = [sum(col[8:13]) for col in sheet]

    column_totals = [top + mid + bottom for top, mid, bottom in zip(top_sum, middle_difference, bottom_sum)]
    grand_total = sum(column_totals)

    for row_idx, label in enumerate(BOX_TYPES):
        if row_idx == 6:
            lines.append(format_total_row('Σ(1-6)', top_sum))
            lines.append(BORDERS["long_border_bottom"])
        elif row_idx == 8:
            lines.append(format_total_row('Δ', middle_difference))
            lines.append(BORDERS["long_border_bottom"])
        
        row = "│".join(f"{sheet[column][row_idx] if sheet[column][row_idx] != -1 else ' ':^{BOX_WIDTH}}" for column in range(len(sheet)))
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
