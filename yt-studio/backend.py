import json

from flask import Flask
from flask_cors import CORS
from flask import request

from PIL import Image

from time import time

import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

FRAMES = 5258

LINE_WIDTH = 396
LINE_HEIGHT = 276

line_memory = []

class Matrix:
    def __init__(self, data):
        self.data = data

        # visited = []
        # for i in range(LINE_WIDTH):
        #     visited.append([False] * LINE_HEIGHT)

        # for i in range(LINE_WIDTH):
        #     for j in range(LINE_HEIGHT):
        #         if self.getpixel(i, j) == 0 and not visited[i][j]:
        #             q = [(i, j)]
        #             cache = []

        #             while len(q) > 0:
        #                 x, y = q.pop()
        #                 cache.append((x, y))

        #                 if x+1 < LINE_WIDTH and not visited[x+1][y] and self.getpixel(x+1, y) == 0:
        #                     q.append((x+1, y))
        #                     visited[x+1][y] = True

        #                 if x-1 >= 0 and not visited[x-1][y] and self.getpixel(x-1, y) == 0:
        #                     q.append((x-1, y))
        #                     visited[x-1][y] = True

        #                 if y+1 < LINE_HEIGHT and not visited[x][y+1] and self.getpixel(x, y+1) == 0:
        #                     q.append((x, y+1))
        #                     visited[x][y+1] = True

        #                 if y-1 >= 0 and not visited[x][y-1] and self.getpixel(x, y-1) == 0:
        #                     q.append((x, y-1))
        #                     visited[x][y-1] = True

        #             if len(cache) <= 70:
        #                 for i, j in cache:
        #                     self.data[j * LINE_WIDTH + i] = 1
    
    def getpixel(self, x, y):
        return self.data[y * LINE_WIDTH + x]

    def setpixel(self, x, y, val):
        self.data[y * LINE_WIDTH + x] = val

class Edge:
    def __init__(self, x, y, adj):
        self.x = x
        self.y = y
        self.adj = adj
    
    def __gt__(self, other):
        return self.adj > other.adj

def getmatrix(filename):
    CROPPED_WIDTH = 120

    im = Image.open(filename).resize((CROPPED_WIDTH, LINE_HEIGHT)).convert('RGB')
    im_arr = list(im.getdata())

    data = [1] * (LINE_HEIGHT * LINE_WIDTH)
    margin = (LINE_WIDTH - CROPPED_WIDTH) // 2

    for x in range(CROPPED_WIDTH):
        for y in range(LINE_HEIGHT):
            data[y * LINE_WIDTH + x + margin] = 0 if sum(im_arr[y * CROPPED_WIDTH + x]) < 125 * 3 else 1

    return Matrix(data)

def raycast_edges(matrix):
    matedges = []
    for x in range(LINE_WIDTH):
        adj = 1
        edges = []
        for y in range(1, LINE_HEIGHT):
            if matrix.getpixel(x, y) != matrix.getpixel(x, y-1):
                edges.append(Edge(x, y, adj))
                adj = 1
            else:
                adj += 1
        matedges.append(sorted(filter(lambda e : e.adj > 6, edges)))

    lines = [[] for i in range(5)]
    for x in range(LINE_WIDTH):
        prev = LINE_HEIGHT - 1
        for i in range(5):
            lines[i].append(prev if len(matedges[x]) <= i else matedges[x][i].y)
            prev = lines[i][len(lines[i])-1]

    return lines

# def raycast(matrix, prev):

#     # print(matrix.getpixel(0,0))

#     first = False

#     if prev == []:
#         prev = [0] * LINE_WIDTH
#         first = True

#     line = []
#     for x in range(LINE_WIDTH):
#         y = prev[x]
        
#         if first:
#             pxl = 0
#         elif y >= LINE_HEIGHT:
#             line.append(LINE_HEIGHT-1)
#             continue
#         else:
#             pxl = matrix.getpixel(x, y)
#         while y < LINE_HEIGHT - 1 and pxl  == matrix.getpixel(x, y):
#             y += 1

#         line.append(y)

#     return line

# def fill(matrix):
#     line = []
#     direction = -1
#     prev = LINE_HEIGHT - 1
#     term = 0
#     for x in range(LINE_WIDTH):
#         point = prev
#         for y in range(prev, term, direction):
#             if matrix.getpixel(x, y) == 1 or (y == term - 1 and direction == 1) or (y == 1 and direction == -1):
#                 point = y
#                 direction = -direction
#                 prev = point
#                 term = LINE_HEIGHT - term
#                 break
#         line.append(point)
#     return line

def process(frame):
    filename = 'frames/frame%d.png' % frame
    prev = []
    matrix = getmatrix(filename)

    # for j in range(0, LINE_HEIGHT, 10):
    #     for i in range(0, LINE_WIDTH, 10):
    #         print('  ' if matrix.getpixel(i, j) == 1 else '##', end='')
    #     print()

    # print('>=================================================================')

    # for i in range(LINE_HEIGHT):
    #     print(matrix.getpixel(179, i), end='')
    # print()

    # for i in range(LINE_WIDTH):
    #     adj = 1
    #     for j in range(1, LINE_HEIGHT):
    #         if matrix.getpixel(i, j) == 0:
    #             adj += 1
    #         else:
    #             # if i == 179:
    #             #     print(adj)
    #             if adj < 7:
    #                 for k in range(j-1, j-1-adj, -1):
    #                     matrix.setpixel(i, k, 1)
    #             adj = 1

    # for i in range(LINE_HEIGHT):
    #     print(matrix.getpixel(179, i), end='')
    # print()

    # lines = []
    # for i in range(4):
    #     lines.append(raycast(matrix, [] if i == 0 else lines[i-1]))
    # lines.append(fill(matrix))

    lines = raycast_edges(matrix)
        
    print('\r--> Frame %d/%d' % (frame, FRAMES), end='')

    return lines

@app.route('/')
def index():
    frame = int(request.args.get('frame'))
    if frame > FRAMES:
        return json.dumps({'result': None})
    return json.dumps({'result': line_memory[frame-1]})

if __name__ == '__main__':

    # lines = process(190)
    # for i, l in enumerate(lines):
    #     plt.plot(range(len(l)), list(map(lambda x : LINE_HEIGHT - x, l)))

    # plt.show()

    # print('\n'.join(list(set(map(str, process(43))))))
    
    print('Processing %d frames... Please wait for processing to finish before running on frontend\n' % FRAMES)

    start = time()

    line_memory = list(map(process, range(1, FRAMES+1)))

    print('\r--> Processing complete in %.1f seconds\n' % (time() - start))

    app.run()
