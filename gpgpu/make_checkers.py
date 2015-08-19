#!/usr/bin/env python

from sys import argv
from scipy import array, arange
from scipy.misc import toimage
from itertools import product
from pprint import pprint

edge = 60
half = edge/2
check = 10
argc = len(argv)
if argc >= 2:
    temp = int(argv[1])
    if 1024 >= temp >= 60:
        edge = temp
        half = edge/2
if argc >= 3:
    temp = int(argv[2])
    if half >= temp >= 1:
        check = temp
shape = (edge, edge)
XY = list(product(arange(edge), repeat=2))
value = [255*int((x/check)&1 == (y/check)&1) for (x,y) in XY]

board = array(value).reshape(shape)
image = toimage(board)
image.save('img/checkers_%04d_%02d.png' % (edge, check))
