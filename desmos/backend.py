import json
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

WIDTH = 36
HEIGHT = 28
FRAMES = 4382
FPS = 24

with open('data.json') as f:
    matrix_arr = json.load(f)

frame_coords = []

for i in range(FRAMES):
    coords = []

    frame_matrix = matrix_arr[i]

    for x in range(HEIGHT):
        for y in range(WIDTH):
            cod = frame_matrix[x][y]
            if cod == 1 and (
                (x-1 >= 0 and frame_matrix[x-1][y] != cod) or 
                (x+1 < HEIGHT and frame_matrix[x+1][y] != cod) or 
                (y-1 >=0 and frame_matrix[x][y-1] != cod) or 
                (y+1 < WIDTH and frame_matrix[x][y+1] != cod)):
                coords.append((y, HEIGHT-x-1))

    latex = []

    for c1 in coords:
        for c2 in coords:
            if c1 == c2:
                break
            if abs(c1[0] - c2[0]) <= 2 and abs(c1[1] - c2[1]) <= 2:
                if c1[0] != c2[0]:
                    latex.append('y=%f(x-%d)+%d \\{%d\\le x\\le%d\\}' % (
                        (c1[1]-c2[1])/(c1[0]-c2[0]), 
                        c1[0], 
                        c1[1], 
                        min((c1[0], c2[0])),
                        max((c1[0], c2[0]))
                        )
                    )
                else:
                    latex.append('x=%d \\{%d\\le y\\le%d\\}' % (
                        c1[0],
                        min((c1[1], c2[1])),
                        max((c1[1], c2[1]))
                        )
                    )

    frame_coords.append(latex)

@app.route('/')
def index():
    return json.dumps(frame_coords)

app.run()