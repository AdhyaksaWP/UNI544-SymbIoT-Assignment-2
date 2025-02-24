import cv2
import binascii
import numpy as np

def buffer_to_img(img_buffer):
    np_arr = np.frombuffer(img_buffer, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def flame_detector(img_buffer):
    img = buffer_to_img(img_buffer)

    if img is not None:
        """" Parameters needed for fire detection based on HSV and minimum contour area """
        lower_red = np.array([0,120,70])
        upper_red = np.array([10,255,255])

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_red, upper_red)

        min_contour_area = 1000
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_contour_area:
                print("Fire Detected")

        cv2.drawContours(img, contours, -1, (0,255,0), 2)
        cv2.imshow("ESP32 Stream", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
