import cv2
import numpy as np
import os

digit_colors = [np.array([220, 203, 192]), np.array([66, 203, 58])]
digit_width, digit_height = 11, 16

# Load digit templates
digit_templates = {}
template_dir = os.path.join("masks", "digits")

for filename in os.listdir(template_dir):
    if filename.endswith(".png"):
        digit_name = filename.split(".")[0]
        filepath = os.path.join(template_dir, filename)
        digit_img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

        if digit_img is None:
            print(f"Error: Could not load {filepath}")
            continue

        if digit_img.shape[2] == 3:
            alpha_channel = np.ones(digit_img.shape[:2], dtype=np.uint8) * 255
            digit_img = np.dstack((digit_img, alpha_channel))

        alpha_channel = digit_img[:, :, 3]
        transparent_mask = alpha_channel == 0
        digit_img[transparent_mask] = [0, 0, 0, 0]

        digit_templates[digit_name] = digit_img

def preprocess_digit(digit_region):
    digit_region_rgb = cv2.cvtColor(digit_region, cv2.COLOR_BGR2RGB)
    green_mask_region = np.all(digit_region_rgb == digit_colors[1], axis=-1)
    digit_region_rgb[green_mask_region] = digit_colors[0]
    return digit_region_rgb

def recognize_digit(digit_region):
    digit_region_rgb = preprocess_digit(digit_region)
    best_match = None
    best_diff = float('inf')

    for digit_name, template in digit_templates.items():
        template_rgb = preprocess_digit(template[:, :, :3])
        if template_rgb.shape[:2] != digit_region_rgb.shape[:2]:
            template_resized = cv2.resize(template_rgb, (digit_region_rgb.shape[1], digit_region_rgb.shape[0]), interpolation=cv2.INTER_AREA)
        else:
            template_resized = template_rgb

        diff = np.sum(np.abs(digit_region_rgb.astype(np.int32) - template_resized.astype(np.int32)))

        if diff < best_diff:
            best_diff = diff
            best_match = digit_name

    if best_match is not None:
        if best_match == "unknown":
            return "?"
        elif best_match.startswith("digit"):
            return best_match[5:]
        else:
            return best_match  # return the name of the file if it is not digit or unknown.
    else:
        return None

def find_digit_positions(cell_frame):
    """Detects digit and symbol positions in a cell and returns their bounding boxes."""
    digit_colors = [np.array([220, 203, 192]), np.array([66, 203, 58])]
    digit_width = 11
    digit_height = 16
    tolerance = 3
    center_tolerance = 5
    positions = []

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

        # Add combined contours
        for cx, cy, cw, ch in combined_contours:
            positions.append((cx, cy, cw, ch))

        # Add individual contours that were not combined
        for i, contour in enumerate(contours):
            if i not in used_contours:
                x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
                if abs(w_cont - digit_width) <= tolerance and abs(h_cont - digit_height) <= tolerance:
                    positions.append((x_cont, y_cont, w_cont, h_cont))

    positions.sort(key=lambda x: x[0])  # Sort from left to right
    return positions

def detect_digits(cell_frame):
    """Detects digits and 'unknown' in a cell and returns the recognized values in correct order."""
    positions = find_digit_positions(cell_frame)
    digits_found = []

    for x, y, w, h in positions:
        digit_region = cell_frame[y:y + h, x:x + w].copy()
        filtered_region = np.zeros_like(digit_region)
        for digit_color in digit_colors:
            color_mask = np.all(digit_region == digit_color, axis=-1)
            filtered_region[color_mask] = digit_color
        green_mask = np.all(filtered_region == digit_colors[1], axis=-1)
        filtered_region[green_mask] = digit_colors[0]

        recognized_digit = recognize_digit(filtered_region)
        if recognized_digit is not None:
            digits_found.append((x, str(recognized_digit)))

    return "".join(digit[1] for digit in digits_found)