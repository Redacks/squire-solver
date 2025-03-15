# cell_data.py
import cv2
import numpy as np

class Cell:
    def __init__(self, frame_area, cell_x, cell_y):
        self.frame_area = frame_area
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.value = None
        self.item = None

    def detect_digit(self):
        """Detects digit-like areas in the cell and updates the value."""
        digit_colors = [np.array([192, 203, 220]), np.array([58, 203, 66])]
        digit_width, digit_height = 11, 16

        frame = self.frame_area.copy()
        digits_found = []

        for color in digit_colors:
            digit_mask = np.all(frame == color, axis=-1)
            digit_contours, _ = cv2.findContours(digit_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for digit_contour in digit_contours:
                dx, dy, dw, dh = cv2.boundingRect(digit_contour)
                if abs(dw - digit_width) <= 3 and abs(dh - digit_height) <= 3:
                    digits_found.append((dx, dy, dw, dh))

        if digits_found:
            self.value = "Digit(s) detected"  # Basic indication, refine later
        else:
            self.value = None

    def detect_item(self):
        """Placeholder for item detection logic."""
        # Replace with your actual item detection code
        self.item = "Item detection not implemented"

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
            row.append(Cell(cell_frame, x_cell, y_cell))
        grid.append(row)
    return grid