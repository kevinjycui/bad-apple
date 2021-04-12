from PIL import Image
import pyautogui as gui
import time
import json

import cv2
import numpy as np

PNG_PATH = 'sample.jpg'

WIDTH = 360
HEIGHT = 228

def compareColours(colour1, colour2):
    return sum(abs(colour1[i] - colour2[i]) for i in range(3))
    
rgbs = {
    'black': (0, 0, 0),
    'grey': (127, 127, 127),
    'dark red': (136, 0, 21),
    'red': (237, 28, 36),
    'orange': (255, 127, 39),
    'yellow': (255, 242, 0),
    'green': (34, 177, 76),
    'turquoise': (0, 162, 232),
    'indigo': (63, 72, 204),
    'purple': (163, 73, 164),
    'white': (255, 255, 255),
    'light grey': (195, 195, 195),
    'brown': (185, 122, 87),
    'rose': (255, 174, 201),
    'gold': (255, 201, 14),
    'light yellow': (239, 228, 176),
    'lime': (181, 230, 29),
    'light turquoise': (153, 217, 234),
    'blue grey': (112, 146, 190),
    'lavender': (200, 191, 231)
}

colour_pos = {}

for i, x in enumerate(range(882, 1132, 25)):
    colour_pos[list(rgbs.keys())[i]] = (x, 68)
    colour_pos[list(rgbs.keys())[i+10]] = (x, 98)

def select_colour(colour, position):
    gui.click(colour_pos[colour][0], colour_pos[colour][1])
    time.sleep(0.1)
    gui.doubleClick()
    if position is not None:
        gui.moveTo(position[0], position[1])

# try:
#     with open('bak.json') as f:
#         matrix = json.load(f)
#     visited = []
#     for x in range(HEIGHT):
#         visited.append([False]*WIDTH)
# except FileNotFoundError:
#     with Image.open(PNG_PATH) as im:
#         px = im.load()

#     matrix = []
#     visited = []

#     for x in range(HEIGHT):
#         row = []
#         for y in range(WIDTH):
#             diff = 255*3
#             colour = ''
#             for colpair in rgbs.items():
#                 comp = compareColours(colpair[1], px[y,x])
#                 if comp < diff:
#                     diff = comp
#                     colour = colpair[0]
#             row.append(colour)
#         matrix.append(row)
#         visited.append([False]*WIDTH)

#     with open('bak.json', 'w+') as f:
#         json.dump(matrix, f)

def drawDrag(i, j):
    gui.dragTo(i*3 + 10, j*2 + 180)

def moveTo(i, j):
    gui.moveTo(i*3 + 10, j*2 + 180)

def distance(a, b):
    x, y = a
    w, z = b
    return abs(x-w) + abs(y-z)

def check_draw(i, j, prev_pos):
    if distance((i, j), prev_pos) <= 2:
        drawDrag(i, j)
    else:
        moveTo(i, j)
    return (i, j)

# for i, row in enumerate(matrix):
#     for j, elem in enumerate(row):
#         if not visited[i][j] and elem != 'white':
#             print(elem)
#             queue = [(i, j)]
#             select_colour(elem, gui.position())
#             prev_pos = (i, j)
#             moveTo(i, j)
#             while len(queue) > 0:
#                 x, y = queue.pop()
#                 drawDrag(x, y)
#                 if i-1 >= 0 and not visited[i-1][j] and matrix[i-1][j] == elem:
#                     queue.append((i-1, j))
#                     # prev_pos = check_draw(i-1, j, prev_pos)
#                     visited[i-1][j] = True
#                 if i+1 < HEIGHT and not visited[i+1][j] and matrix[i+1][j] == elem:
#                     queue.append((i+1, j))
#                     # prev_pos = check_draw(i+1, j, prev_pos)
#                     visited[i+1][j] = True
#                 if j-1 >= 0 and not visited[i][j-1] and matrix[i][j-1] == elem:
#                     queue.append((i, j-1))
#                     # prev_pos = check_draw(i, j-1, prev_pos)
#                     visited[i][j-1] = True
#                 if j+1 < WIDTH and not visited[i][j+1] and matrix[i][j+1] == elem:
#                     queue.append((i, j+1))
#                     # prev_pos = check_draw(i, j+1, prev_pos)
#                     visited[i][j+1] = True


def draw_vectors(): # vector method

    WIDTH = 36
    HEIGHT = 28
    FRAMES = 4382
    FPS = 24

    img = cv2.imread('sample.jpg', 0)
    edges = cv2.Canny(img, 100, 255)

    indices = np.where(edges != [0])
    coords = list(zip(indices[1], indices[0]))

    # coords = []

    # for x in range(HEIGHT):
    #     for y in range(WIDTH):
    #         cod = frame_matrix[x][y]
    #         if cod == 1 and (
    #             (x-1 >= 0 and frame_matrix[x-1][y] != cod) or 
    #             (x+1 < HEIGHT and frame_matrix[x+1][y] != cod) or 
    #             (y-1 >=0 and frame_matrix[x][y-1] != cod) or 
    #             (y+1 < WIDTH and frame_matrix[x][y+1] != cod)):
    #             coords.append((y, x))

    for c1 in coords:
        for c2 in coords:
            if c1 == c2:
                break
            if abs(c1[0] - c2[0]) <= 1 and abs(c1[1] - c2[1]) <= 1:
                gui.moveTo(int(c1[0]*2.25), int(c1[1]*1.55) + 180)
                gui.dragTo(int(c2[0]*2.25), int(c2[1]*1.55) + 180)

    gui.hotkey('ctrl', 'a')
    gui.press('del')
    select_brush()

draw_vectors()
        
# hk = SystemHotkey()
# hk.register(('control', 'x'), callback=abort)