import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from utils.grabbers.mss import Grabber
from utils.controls.mouse.win32 import MouseControls
from screen_to_world import get_move_angle
import time
import math

from utils.grabbers.mss import Grabber
from utils.fps import FPS
import cv2
import multiprocessing
import numpy as np
from utils.nms import non_max_suppression_fast
from utils.cv2 import filter_rectangles

from utils.controls.mouse.win32 import MouseControls
from utils.win32 import WinHelper
import keyboard

import time
from utils.time import sleep

from screen_to_world import get_move_angle

# Assuming you have these values defined somewhere in your code
fov = [106.26, 73.74]  # horizontal, vertical
x360 = 16364  # x value to rotate on 360 degrees
x1 = x360/360

def find_red_on_screen():
    grabber = Grabber()
    mouse = MouseControls()

    def check_dot(hue_point, center_x, center_y):
        dot_img = grabber.get_image({"left": center_x + 5, "top": center_y + 28, "width": 6, "height": 6})
        dot_img = cv2.cvtColor(dot_img, cv2.COLOR_BGR2HSV)
        avg_color_per_row = np.average(dot_img, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        return (hue_point - 10 < avg_color[0] < hue_point + 20) and (avg_color[1] > 120) and (avg_color[2] > 100)

    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)

    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    lower_red_1 = np.array([0, 100, 100])
    upper_red_1 = np.array([10, 255, 255])
    lower_red_2 = np.array([160, 100, 100])
    upper_red_2 = np.array([180, 255, 255])
    mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
    mask = mask_1 + mask_2

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    game_window_rect = WinHelper.GetWindowRect("aimlab_tb", (8, 30, 16, 39))  # assuming you have this

    for contour in contours:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2
            center_y = y + h // 2

            rel_diff = get_move_angle((center_x, center_y), game_window_rect, x1, fov)
            mouse.move_relative(int(rel_diff[0]), int(rel_diff[1]))
            time.sleep(0.02)  # assuming you want to keep a sleep, adjust as necessary

        #    if check_dot(87, center_x, center_y):  # 87 is the hue value
            mouse.hold_mouse()
            time.sleep(0.001)
            mouse.release_mouse()
            time.sleep(0.001)
            break

# Check if Aim Lab window is active
aimlab_window = [window for window in gw.getWindowsWithTitle('aimlab_tb') if window.visible]
if not aimlab_window:
    print("Aim Lab window not found or not visible.")
    exit()

is_toggled = False
while True:
    if keyboard.is_pressed('F4'):
        is_toggled = not is_toggled
        if is_toggled:
            print("Toggled ON")
        else:
            print("Toggled OFF")
        time.sleep(0.5)  # Small sleep to avoid toggling rapidly with a single press
    
    if is_toggled:
        find_red_on_screen()
    else:
        time.sleep(0.1)  # Sleep a bit when not toggled to avoid excessive CPU usage