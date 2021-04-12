import pyautogui as gui
import time
import json
from array import *

from PIL import Image
import cv2
import numpy as np

# method used is vector, ignore raster methods

const_x = 10

colours = {
    'black': (882, 68),
    'grey': (912, 68)
}

WIDTH = 480
HEIGHT = 360
FRAMES = 5258
FPS = 24

BASE_PNG_DIR = 'frames'
BASE_PNG_PATH = BASE_PNG_DIR + '/frame%d.png'

gui.PAUSE = 0.000000000001

def select_colour(colour, position):
    gui.click(colours[colour][0], colours[colour][1])
    time.sleep(0.01)
    gui.doubleClick()
    if position is not None:
        gui.moveTo(position[0], position[1])

def select_brush():
    gui.click(400, 70)
    time.sleep(0.01)
    gui.doubleClick()

def select_bucket(): # selects fill tool (unused)
    gui.click(305, 75)
    time.sleep(0.01)
    gui.doubleClick()

def draw_row(row, prev, y, code): # draws row as raster
    gui.moveTo(const_x, y)
    skip = False
    for i, elem in enumerate(row+[3]):
        if elem == prev[i] and skip:
            continue

        elif elem != prev[i] and skip:
            gui.moveTo(i*20, y)
            skip = False
            continue

        elif (i > 0 and row[i-1] != elem) or elem == prev[i]:
            if elem == prev[i]:
                skip = True
            if code == 1 and row[i-1] == 0:
                gui.dragTo(i*20, y, button='right')
            elif row[i-1] == code:
                gui.dragTo(i*20, y)
            else:
                gui.moveTo(i*20, y)

def draw_matrix(matrix, prev): # raster method
    select_colour('black', gui.position())
    for y, row in enumerate(matrix):
        if (prev is None or row != prev[y]) and 1 in row:
            draw_row(row, [4]*(WIDTH+1) if prev is None else prev[y] + [4], y*20 + 180, 1)
    select_colour('grey', gui.position())
    for y, row in enumerate(matrix):
        if (prev is None or row != prev[y]) and 2 in row:
            draw_row(row, [4]*(WIDTH+1) if prev is None else prev[y] + [4], y*20 + 180, 2)

def draw_vectors(frame): # vector method

    img = cv2.imread('frames/frame%d.png' % (frame+1), 0)
    # img = cv2.imread('sample.jpg', 0)
    # with Image.open('frames/frame%d.png' % (frame+1)) as im:
    #     px = im.load()

    _, binary = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        lst = contour.tolist()
        begin = lst[0][0]
        gui.moveTo(begin[0]*2+15, begin[1]*2+180)
        for i in range(1, len(lst)):
            point = lst[i][0]
            gui.dragTo(point[0]*2+15, point[1]*2+180)
        gui.dragTo(begin[0]*2+15, begin[1]*2+180)

        # x = 0
        # y = 0
        # for edge in edges:
        #     x += edge[0]
        #     y += edge[1]
        # x //= len(edges)
        # y //= len(edges)

        # if px[x,y][0] < 125:
        #     select_bucket()
        #     gui.click(x*3+15, y*2+180)
        #     time.sleep(0.01)
        #     gui.doubleClick()


    # fill_blacks(frame, edges)

    time.sleep(1)

    gui.hotkey('ctrl', 'a')
    gui.press('del')
    select_brush()
        
# hk = SystemHotkey()
# hk.register(('control', 'x'), callback=abort)

time.sleep(15)

select_brush()

# with open('data.json') as f:
#     data = json.load(f)

# draw_matrix(data[100], None)

# prev = None
# select_colour('black', None)

# for i in range(0, len(data), 1):
#     matrix = data[i]
#     draw_matrix(matrix, prev)
#     prev = matrix
# draw_vectors(500)

# draw_vectors(585, data[585])

for i in range(0, FRAMES, 3):
    draw_vectors(i)

# draw_vectors(500)

# for i in range(1011, len(data), 8):
#     draw_vectors(i)