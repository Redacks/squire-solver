import cv2
import numpy as np

cv2.namedWindow("Squire", cv2.WINDOW_NORMAL)
last_frame = None

def render_output(output_frame):
    global last_frame

    if output_frame is not None:
        last_frame = output_frame

    if last_frame is None: 
        last_frame = np.ones((100, 100, 3), np.uint8) * 255
        
    cv2.imshow("Squire", last_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("Squire", cv2.WND_PROP_VISIBLE) < 1:
        return True
    return False