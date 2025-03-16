# cell_data.py
from digit_detector import detect_digits
from field_detector import detect_field_type

class Cell:
    def __init__(self, frame_area, cell_x, cell_y):
        self.frame_area = frame_area
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.value = None
        self.field_type = None

    def detect_digit(self):
        """Detects digits and updates the cell's value."""
        self.value = detect_digits(self.frame_area)

    def detect_field(self):
        """Detects the field type and updates the cell's field_type."""
        self.field_type = detect_field_type(self.frame_area)

def get_cell_data(game_area, grid_x, grid_y, bottom_start, top_stop):
    """Returns a 2D array of Cell objects representing the grid."""
    height, width, _ = game_area.shape
    cell_width = width / grid_x
    cell_height = (top_stop - bottom_start) / (grid_y - 1)

    grid = []
    for y_cell in range(1, grid_y):
        row = []
        for x_cell in range(grid_x):
            x = int(x_cell * cell_width) + 1
            y = int(bottom_start + (y_cell - 1) * cell_height)
            cell_frame = game_area[y:int(y + cell_height), x:int(x + cell_width)]
            cell = Cell(cell_frame, x_cell, y_cell)
            row.append(cell)
        grid.append(row)
    return grid