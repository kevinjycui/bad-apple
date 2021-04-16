from PIL import Image
import numpy as np
import potrace


def png_to_np_array(filename):
    img = Image.open(filename)
    data = np.array(img.getdata()).reshape(img.size[0], img.size[1], 3)
    bindata = np.zeros((img.size[0], img.size[1]), np.uint32)
    for i, row in enumerate(data):
        for j, byte in enumerate(row):
            bindata[i, j] = 1 if sum(byte) < 125*3 else 0
    return bindata

def png_to_svg(filename):
    data = png_to_np_array(filename)
    bmp = potrace.Bitmap(data)
    path = bmp.trace()
    return path

print([curve.segments for curve in png_to_svg('pngs/png500.png').curves])
