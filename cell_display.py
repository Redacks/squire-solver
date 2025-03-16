import cv2

def display_cell_data(game_area, cells, bottom_start, top_stop):
    """Displays cell values or field types with specified colors."""
    height, width, _ = game_area.shape
    grid_x = len(cells[0])
    grid_y = len(cells) + 1
    cell_width = width / grid_x
    cell_height = (top_stop - bottom_start) / (grid_y - 1)

    game_area_copy = game_area.copy()

    blue_field_types = ["Door", "Flag"]
    white_field_types = ["Wall"]
    green_field_types = ["Floor"]

    for y_cell, row in enumerate(cells):
        for x_cell, cell in enumerate(row):
            x = int(x_cell * cell_width) + 1
            y = int(bottom_start + y_cell * cell_height)
            cell_center_x = int(x + cell_width / 2)
            cell_center_y = int(y + cell_height / 2)

            if cell.value and cell.value != "":
                text_size_value, _ = cv2.getTextSize(cell.value, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                text_x_value = cell_center_x - text_size_value[0] // 2
                text_y_value = cell_center_y + text_size_value[1] // 2
                cv2.putText(game_area_copy, cell.value, (text_x_value, text_y_value), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                if cell.field_type and cell.field_type != "":
                    field_text = str(cell.field_type)

                    if len(field_text) > 1 and field_text[0].isdigit() and field_text[1] == "x":
                        parts = field_text.split("x")
                        if len(parts) == 2:
                            amount = parts[0] + "x"
                            field_type = parts[1]

                            text_size_amount, _ = cv2.getTextSize(amount, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                            text_x_amount = cell_center_x - text_size_amount[0] // 2
                            text_y_amount = cell_center_y - text_size_amount[1] // 2

                            cv2.putText(game_area_copy, amount, (text_x_amount, text_y_amount), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                            text_size_field, _ = cv2.getTextSize(field_type, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)
                            text_x_field = cell_center_x - text_size_field[0] // 2
                            text_y_field = cell_center_y + text_size_field[1]

                            cv2.putText(game_area_copy, field_type, (text_x_field, text_y_field), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)

                    else:
                        text_size_field, _ = cv2.getTextSize(field_text, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)
                        text_x_field = cell_center_x - text_size_field[0] // 2
                        text_y_field = cell_center_y + text_size_field[1] // 2

                        text_color = (0, 0, 255)  # Default color is red

                        if field_text in blue_field_types:
                            text_color = (255, 0, 0)
                        elif field_text in white_field_types:
                            text_color = (255, 255, 255)
                        elif field_text in green_field_types:
                            text_color = (0, 255, 0)

                        cv2.putText(game_area_copy, field_text, (text_x_field, text_y_field), cv2.FONT_HERSHEY_SIMPLEX, 0.35, text_color, 1)

    return game_area_copy