# grid_drawer.py
import cv2

def draw_grid_lines(game_area, grid_x, grid_y, bottom_start, top_stop):
    """Draws a grid on the game area."""
    height, width, _ = game_area.shape
    cell_width = width / grid_x
    cell_height = (top_stop - bottom_start) / (grid_y - 1) # 4 removed rows.

    # Draw horizontal lines
    for i in range(1, grid_y + 1):
        y = int(bottom_start + (i - 1) * cell_height) # -1 because we are starting at 1
        cv2.line(game_area, (0, y), (width, y), (0, 255, 0), 1)

    # Draw vertical lines
    for i in range(grid_x + 1):
        x = int(i * cell_width)
        cv2.line(game_area, (x, int(bottom_start)), (x, int(top_stop)), (0, 255, 0), 1)

    return game_area