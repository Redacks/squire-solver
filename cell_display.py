import cv2

def display_cell_data(game_area, cells, bottom_start, top_stop):
    """Displays the cell values and field types in the center of each cell."""
    height, width, _ = game_area.shape
    grid_x = len(cells[0])
    grid_y = len(cells) + 1
    cell_width = width / grid_x
    cell_height = (top_stop - bottom_start) / (grid_y - 1)

    game_area_copy = game_area.copy()

    for y_cell, row in enumerate(cells):
        for x_cell, cell in enumerate(row):
            x = int(x_cell * cell_width) + 1
            y = int(bottom_start + y_cell * cell_height)
            cell_center_x = int(x + cell_width / 2)
            cell_center_y = int(y + cell_height / 2)

            if cell.value is not None:
                text_size_value, _ = cv2.getTextSize(cell.value, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                text_x_value = cell_center_x - text_size_value[0] // 2
                text_y_value = cell_center_y - text_size_value[1] // 2 # Move value up

                cv2.putText(game_area_copy, cell.value, (text_x_value, text_y_value), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            if cell.field_type is not None:
                field_text = str(cell.field_type) #ensure that field_type is a string
                field_text_len = len(field_text)
                font_scale = 1
                thickness = 1

                # Adjust font scale based on text length
                if field_text_len >= 9:
                    font_scale = 0.2
                elif field_text_len >= 7:
                    font_scale = 0.3
                elif field_text_len >= 5:
                    font_scale = 0.4
                elif field_text_len >= 3:
                    font_scale = 0.5

                text_size_field, _ = cv2.getTextSize(field_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                text_x_field = cell_center_x - text_size_field[0] // 2
                text_y_field = cell_center_y + text_size_field[1] // 2 + text_size_value[1] // 2 # Place field type under value

                cv2.putText(game_area_copy, field_text, (text_x_field, text_y_field), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)

    return game_area_copy