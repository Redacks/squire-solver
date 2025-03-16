import cv2
import numpy as np
import os

def color_pct(cell_frame, color):
    """Calculates the percentage of a given color in a cell frame."""
    height, width, _ = cell_frame.shape
    total_pixels = height * width
    color_mask = np.all(cell_frame == color, axis=-1)
    return np.count_nonzero(color_mask) / total_pixels

# Load field type templates
field_type_templates = {}
field_type_names = {}  # Map template file names to field type names
template_dir = os.path.join("masks", "fields")
if os.path.exists(template_dir):
    for filename in os.listdir(template_dir):
        if filename.endswith(".png"):
            field_type_name = filename.split(".")[0]  # Extract name from filename
            field_type_names[filename] = field_type_name
            filepath = os.path.join(template_dir, filename)
            field_img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
            if field_img is None:
                print(f"Error: Could not load {filepath}")
                continue

            if field_img.shape[2] == 3:  # If no alpha channel, add one
                alpha_channel = np.ones(field_img.shape[:2], dtype=np.uint8) * 255
                field_img = np.dstack((field_img, alpha_channel))

            alpha_channel = field_img[:, :, 3]
            transparent_mask = alpha_channel == 0
            field_img[transparent_mask] = [0, 0, 0, 0]
            field_type_templates[filename] = field_img

def recognize_field_type(cell_frame):
    """Recognizes field types based on template matching with alpha channel."""
    best_match = None
    best_diff = float('inf')
    best_template_area = 0

    for filename, template in field_type_templates.items():
        template_rgb = template[:, :, :3]
        alpha_channel = template[:, :, 3]

        if template_rgb.shape[:2] != cell_frame.shape[:2]:
            template_resized = cv2.resize(template_rgb, (cell_frame.shape[1], cell_frame.shape[0]), interpolation=cv2.INTER_AREA)
            alpha_resized = cv2.resize(alpha_channel, (cell_frame.shape[1], cell_frame.shape[0]), interpolation=cv2.INTER_AREA)
        else:
            template_resized = template_rgb
            alpha_resized = alpha_channel

        # Create a mask for non-transparent pixels
        alpha_mask = alpha_resized > 0

        # Calculate difference only for non-transparent pixels
        diff = np.sum(np.abs(cell_frame[alpha_mask].astype(np.int32) - template_resized[alpha_mask].astype(np.int32)))
        template_area = np.count_nonzero(alpha_mask)

        if diff < best_diff:
            best_diff = diff
            best_match = filename
            best_template_area = template_area

    if best_match is not None:
        confidence = 1.0 - (best_diff / (best_template_area * 255 * 3)) # Normalize confidence
        if confidence > 0.9:
            return field_type_names[best_match], confidence

    return None, 0.0

def detect_field_type(cell_frame):
    """Detects the field type based on color percentages and template matching."""

    # Define colors for wall and floor
    wall_color = np.array([180, 155, 139])
    floor_color = np.array([108, 165, 234])
    void_color = np.array([49, 38, 63])

    # Calculate color percentages
    wall_percentage = color_pct(cell_frame, wall_color)
    floor_percentage = color_pct(cell_frame, floor_color)
    void_percentage = color_pct(cell_frame, void_color)


    # Determine field type based on percentages
    if void_percentage > 0.9: 
        return ""
    if wall_percentage > 0.2:
        return "Wall"
    elif floor_percentage > 0.4:
        return "Floor"
    else:
        # If color percentages don't match, use template matching
        template_match, confidence = recognize_field_type(cell_frame)
        if template_match:
            #return str(round(confidence*100)/100)
            return template_match
        else:
            return "?" # return empty string if nothing is found