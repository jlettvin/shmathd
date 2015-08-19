#!/usr/bin/python

#import Image
import scipy
from scipy import ones
from scipy.misc import toimage
from sys import argv

def make(**kw):
    step  = kw.get( 'step', 3e-2)
    scale = kw.get('scale', 3e-1)
    print step, scale
    name = 'img/gray_%3.2f_%3.2f.png' % (step, scale)
    print name
    X, Y = 640, 320
    X0, X1, X2, X3 = 0, X/2-1, X/2, X-1

    gray = ones((Y,X),dtype=float)
    gray[:,X0:X1] -= step
    gray[:,X2:X3] += step

    noise = ((scipy.random.random((Y,X))*2)-1) * scale

    board = (gray+noise)*127
    #print gray.max(), noise.max(), image.max()
    #print gray.min(), noise.min(), image.min()

    image = toimage(board)
    image.save(name)

    #saved = Image.fromarray(board)
    ##print name
    #saved.save(name)
    #scipy.misc.toimage(saved)

if __name__ == "__main__":
    argc = len(argv)
    step = 3e-2 if argc < 2 else float(argv[1])
    scale = 3e-1 if argc < 3 else float(argv[2])
    assert 3e-2 <= step <= 5e-2
    assert 3e-1 <= scale <= 5e-1
    make(step=step, scale=scale)

#make(step=3e-2, scale=3e-1)
#make(step=3e-2, scale=5e-1)
#make(step=5e-2, scale=3e-1)
#make(step=5e-2, scale=5e-1)
