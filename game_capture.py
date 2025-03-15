import pyautogui
import numpy as np
import cv2

screen_w, screen_h = pyautogui.size()
capture_w, capture_h = screen_w // 2, screen_h

def capture_screen():
    screenshot = np.array(pyautogui.screenshot(region=(0, 0, capture_w, capture_h)))
    return cv2.cvtColor(screenshot,cv2.COLOR_BGR2RGB)

import cv2
import numpy as np

def get_game_area(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray_frame, 5, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_squares = [cv2.boundingRect(c) for c in contours if cv2.boundingRect(c)[2] >= 50 and cv2.boundingRect(c)[3] >= 50]

    if len(valid_squares) != 2:
        return None

    valid_squares.sort(key=lambda sq: sq[0])  # Sort from left to right
    left_x, left_y, left_w, left_h = valid_squares[0]
    right_x, right_y, right_w, right_h = valid_squares[1]

    game_area_x = left_x + left_w # right edge of left bar
    game_area_y = min(left_y, right_y) # top of both bars
    game_area_w = right_x - game_area_x # width between right edge of left bar and left edge of right bar
    game_area_h = max(left_y + left_h, right_y + right_h) - game_area_y # bottom of both bars - top of both bars

    # Extract the game area from the original frame
    game_area = frame[game_area_y:game_area_y + game_area_h, game_area_x:game_area_x + game_area_w]

    return game_area