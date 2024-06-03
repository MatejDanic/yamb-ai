from .box import Box

class Column: 
    def __init__(self, type):
        self.type = type
        self.boxes = [Box(str(j)) for j in range(13)]
    
    def fill_box(self, box, value):
        self.boxes[box].value = value
    
    def is_completed(self):
        return all(box.value is not None for box in self.boxes)
    
    def get_top_sum(self):
        return sum(box.value if box.value is not None else 0 for box in self.boxes[0:6])
    
    def get_middle_difference(self):
        return (self.boxes[6].value if self.boxes[6].value is not None else 0) - (self.boxes[7].value if self.boxes[7].value is not None else 0)
    
    def get_bottom_sum(self):
        return sum(box.value if box.value is not None else 0 for box in self.boxes[8:13])