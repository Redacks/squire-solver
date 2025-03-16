# digit_border_drawer.py
import cv2
import numpy as np

digit_colors = [np.array([220, 203, 192]), np.array([66, 203, 58])]
digit_width = 11
digit_height = 16
tolerance = 3
center_tolerance = 5
question_mark_count = 0  # Counter for question mark windows

def draw_digit_borders(game_area, cells, bottom_start, top_stop, grid_x, grid_y):
    """Draws yellow borders around detected digit regions in place."""
    global question_mark_count  # Access the global counter
    height, width, _ = game_area.shape
    cell_width = width / grid_x
    cell_height = (top_stop - bottom_start) / (grid_y - 1)

    for row in cells:
        for cell in row:
            if cell.field_type != "Floor":
                continue

            x = int(cell.cell_x * cell_width)
            y = int(bottom_start + (cell.cell_y - 1) * cell_height)
            cell_frame = cell.frame_area.copy()  # Make a copy for cropping

            for color in digit_colors:
                mask = np.all(cell_frame == color, axis=-1).astype(np.uint8)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                combined_contours = []
                used_contours = set()

                for i, contour1 in enumerate(contours):
                    if i in used_contours:
                        continue
                    x1, y1, w1, h1 = cv2.boundingRect(contour1)
                    center_x1 = x1 + w1 // 2
                    for j, contour2 in enumerate(contours):
                        if i == j or j in used_contours:
                            continue
                        x2, y2, w2, h2 = cv2.boundingRect(contour2)
                        center_x2 = x2 + w2 // 2
                        if abs(center_x1 - center_x2) <= center_tolerance and y2 > y1 and y2 - (y1 + h1) <= 10:
                            combined_x = min(x1, x2)
                            combined_y = min(y1, y2)
                            combined_w = max(x1 + w1, x2 + w2) - combined_x
                            combined_h = max(y1 + h1, y2 + h2) - combined_y

                            if abs(combined_w - digit_width) <= tolerance and abs(combined_h - digit_height) <= tolerance:
                                combined_contours.append((combined_x, combined_y, combined_w, combined_h))
                                used_contours.add(i)
                                used_contours.add(j)
                                break

                # Draw combined contours and show question mark window
                for cx, cy, cw, ch in combined_contours:
                    cv2.rectangle(game_area, (x + cx, y + cy), (x + cx + cw, y + cy + ch), (0, 255, 255), 2)
                    question_mark_region = cell_frame[cy:cy + ch, cx:cx + cw] #Crop the found region.
                    if question_mark_region.size > 0:
                        scaled_question_mark = cv2.resize(question_mark_region, (cw * 5, ch * 5)) #scale up
                        cv2.imshow(f"Question Mark {question_mark_count}", scaled_question_mark)
                        cv2.waitKey(1)
                        question_mark_count += 1

                # Draw individual contours that were not combined.
                for i, contour in enumerate(contours):
                    if i not in used_contours:
                        x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
                        if abs(w_cont - digit_width) <= tolerance and abs(h_cont - digit_height) <= tolerance:
                            cv2.rectangle(game_area, (x + x_cont, y + y_cont), (x + x_cont + w_cont, y + y_cont + h_cont), (0, 255, 255), 2)

    return game_area