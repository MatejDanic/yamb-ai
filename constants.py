# constants.py
BOX_WIDTH = 8
ROW_HEADER_WIDTH = 8

DICE_ART = {
    1: ["┌─────────┐", "│         │", "│    o    │", "│         │", "└─────────┘"],
    2: ["┌─────────┐", "│  o      │", "│         │", "│      o  │", "└─────────┘"],
    3: ["┌─────────┐", "│  o      │", "│    o    │", "│      o  │", "└─────────┘"],
    4: ["┌─────────┐", "│  o   o  │", "│         │", "│  o   o  │", "└─────────┘"],
    5: ["┌─────────┐", "│  o   o  │", "│    o    │", "│  o   o  │", "└─────────┘"],
    6: ["┌─────────┐", "│  o   o  │", "│  o   o  │", "│  o   o  │", "└─────────┘"]
}

COLUMN_TYPES = ['DOWN', 'UP', 'FREE', 'ANN']

BOX_TYPES = [
    'Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes', 
    'MAX', 'MIN', 'Trips', 'Straight', 
    'Boat', 'Carriage', 'Yamb'
]

BORDERS = {
    "border": ' ' * (ROW_HEADER_WIDTH + 3) + '├' + '─' * (BOX_WIDTH) + ('┼' + '─' * (BOX_WIDTH)) * 3 + "┤",
    "border_top": ' ' * (ROW_HEADER_WIDTH + 3) + '┌' + '─' * (BOX_WIDTH) + ('┬' + '─' * (BOX_WIDTH)) * 3 + "┐",
    "border_bottom_final": ' ' * (ROW_HEADER_WIDTH + 3) + ' ' * (BOX_WIDTH + 1) * 3 + '└' + '─' * (BOX_WIDTH * 2 + 1) + "┘",
    "long_border_top": '┌' + '─' * (ROW_HEADER_WIDTH + 2) + '┼' + '─' * (BOX_WIDTH) + ('┼' + '─' * (BOX_WIDTH)) * 4 + "┐",
    "long_border_bottom": '└' + '─' * (ROW_HEADER_WIDTH + 2) + '┼' + '─' * (BOX_WIDTH) + ('┼' + '─' * (BOX_WIDTH)) * 4 + "┘",
    "long_border_bottom_final": '└' + '─' * (ROW_HEADER_WIDTH + 2) + '┴' + '─' * (BOX_WIDTH) + ('┴' + '─' * (BOX_WIDTH)) * 2 + ('┼' + '─' * (BOX_WIDTH))  + ('┴' + '─' * (BOX_WIDTH)) + "┤"
}
