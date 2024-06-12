from simple_yamb import SimpleYamb


class Yamb(SimpleYamb):
    def __init__(self):
        super().__init__()   
        self.sheet = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]  
        self.announcement = -1

    def fill_box(self, column, box):
        super.fill_box(column, box)
        self.announcement = -1

    def roll_dice(self, dice_to_roll):
        super.roll_dice(dice_to_roll)
        if (self.roll_count == 3):
            self.fill_box(3, self.announcement)

    def is_box_available(self, column, box):
        if self.sheet[column][box] == -1:
            if column == 0:
                return box == 0 or self.sheet[column][box - 1] != -1
            elif column == 1:
                return box == 12 or self.sheet[column][box + 1] != -1
            elif column == 3:
                return box == self.announcement
            return column == 2
        return False

    def announce(self, box):
        self.announcement = box

    def validate_announcement(self, box):
        return self.announcement == -1 and self.roll_count == 1 and self.sheet[3][box] == -1
    
    def is_announcement_required(self):
        return self.roll_count == 1 and self.announcement == -1 and self.are_all_non_anouncement_columns_completed()       

    def are_all_non_anouncement_columns_completed(self):
        return len(self.sheet) == 4 and all(all(box != -1 for box in column) for column in self.sheet[:-1])