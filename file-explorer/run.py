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
    # I changed the f into frame to avoid shadowing
    for frame in range(FRAMES):
        mat = []
        for j in range(33):
            arr = []
            for i in range(16):
                code = d[frame][int((j / 33) * (HEIGHT - 1))][int((i / 16) * (WIDTH - 1))]
                arr.append(code)
            mat.append(arr)
        frames.append(mat)

for j in range(16):
    for i in range(33):
        dst = 'sandbox/%d.%d.mp4' % (j, i)
        shutil.copy(src[0], dst)

exts = ('txt', 'mp4', 'mp3')

# range now starts with 1 > because
for f in range(1, FRAMES):
    start = time.time()
    for j in range(16):
        for i in range(33):
            n = frames[f][i][j]
            # < now you can avoid the check of f > 0
            if n == frames[f - 1][i][j]:
                continue
            else:
                # Avoid the for-loop here, and use the previous frame to get correctly the extension
                src = 'sandbox/%d.%d.%s' % (j, i, exts[frames[f - 1][i][j]])
                os.rename(src, 'sandbox/%d.%d.%s' % (j, i, exts[n]))

    time.sleep(1.0 / FPS - min((1.0 / FPS, time.time() - start)))
