# digit_detector.py
import cv2
import numpy as np

digit_colors = [np.array([220, 203, 192]), np.array([66, 203, 58])]
digit_width, digit_height = 11, 16

def draw_digit_borders(game_area, cells):
    """Detects digit-like areas in cells and outlines them on the game_area."""
    game_area_copy = game_area.copy()
    height, width, _ = game_area_copy.shape
    grid_x = len(cells[0])
    grid_y = len(cells) + 1
    cell_width = width / grid_x
    cell_height = (height) / (grid_y - 1)

    for y_cell, row in enumerate(cells):
        for x_cell, cell in enumerate(row):
            x = int(x_cell * cell_width) + 1
            y = int(y_cell * cell_height)
            cell_frame = game_area_copy[y:int(y + cell_height), x:int(x + cell_width)]
            modified_cell = _draw_borders_on_cell(cell_frame)
            game_area_copy[y:int(y + cell_height), x:int(x + cell_width)] = modified_cell

    return game_area_copy

def _draw_borders_on_cell(cell_frame):
    """Helper function to draw borders on a single cell."""
    frame = cell_frame.copy()

    for color in digit_colors:
        digit_mask = np.all(frame == color, axis=-1)
        digit_contours, _ = cv2.findContours(digit_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for digit_contour in digit_contours:
            dx, dy, dw, dh = cv2.boundingRect(digit_contour)
            if abs(dw - digit_width) <= 3 and abs(dh - digit_height) <= 3:
                cv2.rectangle(frame, (dx, dy), (dx + dw, dy + dh), (0, 255, 255), 1)

    return frame