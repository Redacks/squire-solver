# cell_saver.py
import os
import cv2

def save_cells(cells, output_dir="output"):
    """Saves each cell's frame_area as a PNG image."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for row_index, row in enumerate(cells):
        for col_index, cell in enumerate(row):
            filename = os.path.join(output_dir, f"cell_{row_index}_{col_index}.png")
            cv2.imwrite(filename, cell.frame_area)