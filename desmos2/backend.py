import json
from flask import Flask
from flask_cors import CORS
from flask import request

import time
import os
import json
import gc

import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

WIDTH = 36
HEIGHT = 28
FRAMES = 4383
FPS = 60

BASE_PNG_DIR = '../preprocess/pngs'
BASE_PNG_PATH = BASE_PNG_DIR + '/png%d.png'

frames = []


class Domain:
    def __init__(self, left, right, vert):
        self.left = left
        self.right = right
        self.vert = vert

    def __str__(self):
        if self.vert:
            return '%d\le y\le%d' % (self.left, self.right)
        return '%d\le x\le%d' % (self.left, self.right)


class Expression:
    def __init__(self, expr, dom):
        self.expr = expr
        self.dom = dom
        self.vert = self.dom[0].vert
    
    def __str__(self):
        return self.expr + ' \{' + ','.join(map(str, self.dom)) + '\}'

    def __eq__(self, other):
        return self.expr == other.expr

    def concat(self, other):
        self.dom += other.dom

    def merge_domains_psa(self):
        maxe = 0
        for dom in self.dom:
            maxe = max(maxe, dom.right)
        psa = [0]*(maxe+1)
        for dom in self.dom:
            psa[dom.left]+=1
            psa[dom.right]-=1
        prev = 0
        self.dom = []
        cur_dom = None
        for i in range(1, maxe+1):
            psa[i] += psa[i-1]
            if prev == 0 and psa[i] != 0:
                cur_dom = Domain(i, None, self.vert)
            elif prev != 0 and psa[i] == 0:
                if cur_dom is None:
                    raise Exception('Unexpected NoneType Domain')
                cur_dom.right = i
                self.dom.append(cur_dom)
                cur_dom = None
            prev = psa[i]
        if cur_dom is not None:
            cur_dom.right = maxe
            self.dom.append(cur_dom)
        

def get_edges(i):
    img = cv2.imread(BASE_PNG_PATH % (i + 1), 0)
    edges = cv2.Canny(img, 100, 255)
    
    indices = np.where(edges != [0])
    coords = zip(indices[1], HEIGHT-indices[0]-1)
    return list(coords)

def get_vectors(i):

    coords = get_edges(i)

    latex = []

    for c1 in coords:
        for c2 in coords:
            if c1 == c2:
                break
            if abs(c1[0] - c2[0]) <= 2 and abs(c1[1] - c2[1]) <= 2:
                if c1[0] != c2[0]:
                    lat = Expression(
                        'y=%f(x-%d)+%d' % ((c1[1]-c2[1])/(c1[0]-c2[0]), c1[0], c1[1]), 
                        [Domain(min((c1[0], c2[0])), max((c1[0], c2[0])), False)])
                else:
                    lat = Expression(
                        'x=%d' % c1[0],
                        [Domain(min((c1[1], c2[1])), max((c1[1], c2[1])), True)])
                try:
                    ind = latex.index(lat)
                    latex[ind].concat(lat)
                except ValueError:
                    latex.append(lat)

    for lat in latex:
        lat.merge_domains_psa()

    return list(map(str, latex))

@app.route('/')
def index():
    frame = int(request.args.get('frame'))
    res = json.dumps(get_vectors(frame))
    return res

@app.route('/test')
def test():
    return json.dumps(open('latex-data-test.json').read())

app.run()