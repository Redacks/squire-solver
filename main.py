# main.py
import time
import cv2

from cell_saver import save_cells
from game_capture import capture_screen, get_game_area
from render_output import render_output
from grid_drawer import draw_grid_lines
from cell_data import get_cell_data
from cell_display import display_cell_data

grid_x = 10
grid_y = 17
bottom_start = 48
top_stop = 17 * 48 - 3

while True:
    frame = capture_screen()
    game_area = get_game_area(frame)

    if game_area is not None:
        area_with_grid = draw_grid_lines(game_area.copy() * 0, grid_x, grid_y, bottom_start, top_stop)
        cells = get_cell_data(game_area, grid_x, grid_y, bottom_start, top_stop)

        # Detect digits for each cell
        for row in cells:
            for cell in row:
                cell.detect_field()
                cell.detect_digit()
                
        area_with_digits = display_cell_data(area_with_grid, cells, bottom_start, top_stop)

        if render_output(area_with_digits):
            if(cells is not None):
                save_cells(cells)
            break
    else:
        if render_output(None):
            break

cv2.destroyAllWindows()