import shutil
import os
import time
import json

src0 = r'w.txt'
src1 = r'b.jpg'
src2 = r'g.jpg'

src = [src0, src1, src2]

WIDTH = 36
HEIGHT = 28

FRAMES = 4382
FPS = 6

frames = []

with open('data.json') as f:
    d = json.load(f)
#     for f in range(FRAMES):
#         mat = []
#         for j in range(10):
#             arr = []
#             for i in range(20):
#                 code = d[f][int((j/10)*(HEIGHT-1))][int((i/20)*(WIDTH-1))]
#                 arr.append(code)
#             mat.append(arr)
#         frames.append(mat)
    for f in range(FRAMES):
        mat = []
        for j in range(33):
            arr = []
            for i in range(16):
                code = d[f][int((j/33)*(HEIGHT-1))][int((i/16)*(WIDTH-1))]
                arr.append(code)
            mat.append(arr)
        frames.append(mat)

# for f in range(FRAMES):
#     start = time.time()
#     for j in range(10):
#         for i in range(20):
#             n = frames[f][j][i]
#             if f > 0 and n == frames[f-1][j][i]:
#                 continue
#             dst =  'sandbox/%d.%d.jpg' % (j, i)
#             try:
#                 shutil.copy(src[n], dst)
#             except:
#                 pass
#     time.sleep(1.0/FPS - min((1.0/FPS, time.time() - start)))

for j in range(16):
    for i in range(33):
        dst =  'sandbox/%d.%d.mp4' % (j, i)
        shutil.copy(src[0], dst)

exts = ('txt', 'mp4', 'mp3')

for f in range(FRAMES):
    start = time.time()
    for j in range(16):
        for i in range(33):
            n = frames[f][i][j]
            if f > 0 and n == frames[f-1][i][j]:
                continue

            for ext in exts:
                if os.path.isfile('sandbox/%d.%d.%s' % (j, i, ext)):
                    src =  'sandbox/%d.%d.%s' % (j, i, ext)
                    break

            os.rename(src, 'sandbox/%d.%d.%s' % (j, i, exts[n]))

    time.sleep(1.0/FPS - min((1.0/FPS, time.time() - start)))