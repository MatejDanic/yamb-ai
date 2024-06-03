from .column import Column

class Sheet:

    def __init__(self):
        self.columns = [Column(i) for i in range(4)]  # Use column_labels as types for initialization

    def fill_box(self, column, box, value):
        self.columns[column].fill_box(box, value)

    def is_completed(self):
        return all(column.is_completed() for column in self.columns)
    
    def get_top_sum(self):
        return [column.get_top_sum() for column in self.columns]
    
    def get_middle_difference(self):
        return [column.get_middle_difference() for column in self.columns]
    
    def get_bottom_sum(self):
        return [column.get_bottom_sum() for column in self.columns]
    
    def are_all_non_anouncement_columns_completed(self):
        return all(column.is_completed() for column in self.columns[:-1])