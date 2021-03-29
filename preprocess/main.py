from PIL import Image

import time
import os
import json

WIDTH = 36
HEIGHT = 28
FRAMES = 4382
FPS = 24

BASE_PNG_DIR = 'pngs'
BASE_PNG_PATH = BASE_PNG_DIR + '/png%d.png'

matrix_arr = []

for i in range(FRAMES):
    with Image.open(BASE_PNG_PATH % (i + 1)) as im:
        px = im.load()
    matrix = []
    for x in range(HEIGHT):
        row = []
        for y in range(WIDTH):
            # if px[y,x][0] < 125:
            #     row.append(1)
            # else:
            #     row.append(0)
            if px[y,x][0] < 85:
                row.append(1)
            elif px[y,x][0] > 170:
                row.append(0)
            else:
                row.append(2)
        matrix.append(row)
    matrix_arr.append(matrix)

# Save matrix
with open('data2.json', 'w+') as f:
    json.dump(matrix_arr, f)

# Simple command-line example test
#
# os.system('clear')
# 
# for i in range(FRAMES):
#     with Image.open(BASE_PNG_PATH % (i + 1)) as im:
#         px = im.load()
#     for x in range(HEIGHT):
#         for y in range(WIDTH):
#             if px[y,x][0] < 125:
#                 print('   ', end='')
#             else:
#                 print('###', end='')
#         print()
#     time.sleep(1.0/FPS)
#     os.system('clear')
