from simple_yamb import SimpleYamb


class Yamb(SimpleYamb):
    def __init__(self):
        super().__init__()   
        self.sheet = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]  
        self.announcement = -1

    def reset(self):
        super().reset()
        self.sheet = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]  
        self.announcement = -1

    def announce(self, box):
        self.announcement = box

    def validate_announcement(self, box):
        return self.announcement == -1 and self.roll_count == 1 and self.sheet[3][box] == -1
    
    def is_announcement_required(self):
        return self.roll_count == 1 and self.announcement == -1 and self.are_all_non_anouncement_columns_completed()       

    def are_all_non_anouncement_columns_completed(self):
        return len(self.sheet) == 4 and all(all(box != -1 for box in column) for column in self.sheet[:-1])