import cv2
import numpy as np
import pyautogui

screen_w, screen_h = pyautogui.size()
capture_w, capture_h = screen_w // 2, screen_h

cv2.namedWindow("Detected Grid", cv2.WINDOW_NORMAL)

target_color = np.array([234, 165, 108])
digit_colors = [np.array([192, 203, 220]), np.array([58, 203, 66])]
digit_width, digit_height = 11, 16
y_offset, x_offset = 5, -1

# Load digit templates (one per digit)
digit_templates = {}
for i in range(10):
    filename = f"digit{i}.png"
    digit_img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    if digit_img is None:
        print(f"Error: Could not load {filename}")
        continue

    alpha_channel = digit_img[:, :, 3]
    transparent_mask = alpha_channel == 0
    digit_img[transparent_mask] = [0, 0, 0, 0]
    digit_templates[i] = digit_img

def preprocess_digit(digit_region):
    digit_region_rgb = cv2.cvtColor(digit_region, cv2.COLOR_BGR2RGB)
    green_mask_region = np.all(digit_region_rgb == digit_colors[1], axis=-1)
    digit_region_rgb[green_mask_region] = digit_colors[0]
    return digit_region_rgb

def recognize_digit(digit_region):
    digit_region_rgb = preprocess_digit(digit_region)
    best_match = None
    best_diff = float('inf')

    for digit, template in digit_templates.items():
        template_rgb = preprocess_digit(template[:, :, :3])
        if template_rgb.shape[:2] != digit_region_rgb.shape[:2]:
            template_resized = cv2.resize(template_rgb, (digit_region_rgb.shape[1], digit_region_rgb.shape[0]), interpolation=cv2.INTER_AREA)
        else:
            template_resized = template_rgb

        diff = np.sum(np.abs(digit_region_rgb.astype(np.int32) - template_resized.astype(np.int32)))

        if diff < best_diff:
            best_diff = diff
            best_match = digit

    if best_match is not None:
        return best_match
    else:
        return None

while True:
    screenshot = np.array(pyautogui.screenshot(region=(0, 0, capture_w, capture_h)))
    frame = screenshot.copy()

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_squares = [cv2.boundingRect(c) for c in contours if cv2.boundingRect(c)[2] >= 50 and cv2.boundingRect(c)[3] >= 50]

    if len(valid_squares) == 2:
        valid_squares.sort(key=lambda sq: sq[0])
        left_x, left_y, left_w, left_h = valid_squares[0]
        right_x, right_y, right_w, right_h = valid_squares[1]
        game_area_x, game_area_y = left_x + left_w, min(left_y, right_y)
        game_area_w, game_area_h = right_x - game_area_x, max(left_y + left_h, right_y + right_h) - game_area_y

        grid_cols, grid_rows = 10, 20
        cell_width, cell_height = game_area_w / grid_cols, game_area_h / grid_rows
        grid_x_offset, grid_y_offset = game_area_x + x_offset, game_area_y + y_offset

        grid_values = [["" for _ in range(grid_cols)] for _ in range(grid_rows - 3)] # Ignore last 3 rows

        for i in range(grid_cols):
            for j in range(grid_rows - 3): # Ignore last 3 rows
                x1, y1 = int(grid_x_offset + i * cell_width) + 2, int(grid_y_offset + j * cell_height) + 2
                x2, y2 = int(grid_x_offset + (i + 1) * cell_width) - 2, int(grid_y_offset + (j + 1) * cell_height) - 2
                grid_cell_rgb = frame[y1:y2, x1:x2].copy()

                target_mask = np.all(np.abs(grid_cell_rgb - target_color) <= 10, axis=-1)
                target_percentage = np.sum(target_mask) / grid_cell_rgb.size
                has_digits = False

                if target_percentage > 0:
                    digit_regions = []
                    for color in digit_colors:
                        digit_mask = np.all(grid_cell_rgb == color, axis=-1)
                        digit_contours, _ = cv2.findContours(digit_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        for digit_contour in digit_contours:
                            dx, dy, dw, dh = cv2.boundingRect(digit_contour)
                            if abs(dw - digit_width) <= 3 and abs(dh - digit_height) <= 3:
                                digit_region = frame[y1 + dy:y1 + dy + dh, x1 + dx:x1 + dx + dw].copy()
                                filtered_region = np.zeros_like(digit_region)
                                for digit_color in digit_colors:
                                    color_mask = np.all(digit_region == digit_color, axis=-1)
                                    filtered_region[color_mask] = digit_color
                                green_mask = np.all(filtered_region == digit_colors[1], axis=-1)
                                filtered_region[green_mask] = digit_colors[0]
                                digit_regions.append((filtered_region, x1 + dx, y1 + dy))
                    digit_regions.sort(key=lambda region: region[1])

                    recognized_digits = ""
                    for region, _, _ in digit_regions:
                        recognized_digit = recognize_digit(region)
                        if recognized_digit is not None:
                            recognized_digits += str(recognized_digit)
                            has_digits = True
                    if has_digits:
                        grid_values[j][i] = recognized_digits
                    elif target_percentage > 0.3:
                        grid_values[j][i] = "0"
                    else:
                        grid_values[j][i] = "?"

        display_frame = np.zeros_like(frame)
        for i in range(grid_cols):
            for j in range(grid_rows -3): # Ignore last 3 rows
                x1, y1 = int(grid_x_offset + i * cell_width) + 2, int(grid_y_offset + j * cell_height) + 2
                x2, y2 = int(grid_x_offset + (i + 1) * cell_width) - 2, int(grid_y_offset + (j + 1) * cell_height) - 2
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
                cv2.putText(display_frame, grid_values[j][i], (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        cv2.imshow("Detected Grid", display_frame)

    if cv2.getWindowProperty("Detected Grid", cv2.WND_PROP_VISIBLE) < 1 or cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()