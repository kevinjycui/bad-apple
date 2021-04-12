import time
import os
import json

import cv2
import numpy as np

WIDTH = 3840
HEIGHT = 2880
FRAMES = 13142
FPS = 60

BASE_PNG_DIR = 'frames'
BASE_PNG_PATH = BASE_PNG_DIR + '/frame%d.png'

def get_edges(i):
    img = cv2.imread(BASE_PNG_PATH % (i + 1), 0)
    edges = cv2.Canny(img, 100, 255)
    
    indices = np.where(edges != [0])
    coords = zip(indices[0], indices[1])
    return list(coords)

def get_vectors(i):

    coords = get_edges(i)

    latex = []

    for j, coord in enumerate(coords):
        dist = HEIGHT
        other = coord
        for n in range(j, min(j+WIDTH, len(coords))):
            nline = coords[n]
            ndist = abs(nline[0] - coord[0]) + abs(nline[1] - coord[1])
            if ndist < dist:
                dist = ndist
                other = nline
        if coord[0] != other[0]:
            latex.append('y=%f(x-%d)+%d \\{%d\\le x\\le%d\\}' % (
                (coord[1]-other[1])/(coord[0]-other[0]), 
                other[0], 
                other[1], 
                min((coord[0], other[0])),
                max((coord[0], other[0]))
                )
            )
        else:
            latex.append('x=%d \\{%d\\le y\\le%d\\}' % (
                coord[0],
                min((coord[1], other[1])),
                max((coord[1], other[1]))
                )
            )

    return latex

print(list(get_vectors(500)))