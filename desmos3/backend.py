import json
from flask import Flask
from flask_cors import CORS

from PIL import Image
import numpy as np
import potrace

app = Flask(__name__)
CORS(app)

FRAMES = 5258

def png_to_np_array(filename):
    img = Image.open(filename)
    data = np.array(img.getdata()).reshape(img.size[1], img.size[0], 3)
    bindata = np.zeros((img.size[1], img.size[0]), np.uint32)
    for i, row in enumerate(data):
        for j, byte in enumerate(row):
            bindata[img.size[1]-i-1, j] = 1 if sum(byte) < 127*3 else 0
        #     print('###' if bindata[i, j] == 1 else '   ', end='')
        # print()
    return bindata

def png_to_svg(filename):
    data = png_to_np_array(filename)
    bmp = potrace.Bitmap(data)
    path = bmp.trace()
    return path

frame_coords = []

for i in range(FRAMES):

    latex = []

    path = png_to_svg('frames/frame%d.png' % (i+1))

    for curve in path.curves:
        segments = curve.segments
        start = curve.start_point
        for segment in segments:
            x0, y0 = start
            if segment.is_corner:
                x1, y1 = segment.c
                x2, y2 = segment.end_point
                latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (x0, x1, y0, y1))
                latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (x1, x2, y1, y2))
            else:
                x1, y1 = segment.c1
                x2, y2 = segment.c2
                x3, y3 = segment.end_point
                latex.append('((1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)),\
                (1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)))' % \
                (x0, x1, x1, x2, x1, x2, x2, x3, y0, y1, y1, y2, y1, y2, y2, y3))
            start = segment.end_point

    frame_coords.append(latex)

@app.route('/')
def index():
    return json.dumps(frame_coords)

app.run()