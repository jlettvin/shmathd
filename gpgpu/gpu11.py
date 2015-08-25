#!/usr/bin/env python
###############################################################################
# TODO JMP JE JG JL JGE JLE SETJMP LONGJMP DATA LABEL
# TODO discover how to keep code resident and send it new data
# TODO discover how to reference other pixel data for convolution/correlation
# TODO Use Tower of Hanoi separate data stacks for each type and
#      make different instructions (or modifiers) for each.
# TODO test whether the BLOCKSIZE approach interferes with referencing
# Perhaps convolve a checkerboard with a Gaussian blur.
###############################################################################

"""gpu11.py implements an RPN kernel constructor.
"""

import re

from sys import (argv, path)
from PIL import (Image)
from time import (time)
from numpy import (array, float32, int32, empty_like, uint8)
path.append('../Banner')
# from pprint import pprint
from Banner import (Banner)
# from operator import (add, sub, mul, div)

# pycuda imports do not pass pylint tests.
# pycuda.autoinit is needed for cuda.memalloc.
import pycuda.autoinit  # noqa
from pycuda.driver import (mem_alloc, memcpy_htod, memcpy_dtoh)  # noqa
from pycuda.compiler import (SourceModule)  # noqa


###############################################################################
class CUDAMathConstants(object):
    """Initialize math constants for the interpreter."""
    ###########################################################################
    def __init__(self, **kw):
        """Initialize math constants class."""
        filename = kw.get(
            'filename',
            '/usr/local/cuda-5.5/targets/x86_64-linux/include/'
            'math_constants.h')
        self.caselist = []
        self.identified = {}
        with open('RPN_CUDA_constants.txt', 'w') as manual:
            print>>manual, '# RPN CUDA constants'
            self.hrule(manual)
            print>>manual, '# PUSH CUDA constant onto RPN stack'
            self.hrule(manual)
            with open(filename) as source:
                for line in source:
                    if line.startswith('#define'):
                        token = re.findall(r'(\S+)', line)
                        if len(token) != 3:
                            continue
                        define, name, value = token
                        if '.' not in value:
                            continue
                        # if name.endswith('_HI') or name.endswith('_LO'):
                            # continue
                        self.identified[name] = value
                        print>>manual, '%24s: %s' % (name, value)
            self.hrule(manual)

    ###########################################################################
    def hrule(self, stream):
        """Debugging: output horizontal rule."""
        print>>stream, '#' + '_' * 78

    ###########################################################################
    def functions(self):
        """Prepare function handling."""
        end = '/*************************************************************/'
        text = ''
        for token in self.identified.iteritems():
            name, value = token
            text += ''.join((
                '__device__ int %s\n' % (end),
                'RPN_%s_RPN(Thep the) {' % (name),
                ' IPUP = %s;' % (name),
                ' return 0;',
                '}\n',
            ))
        return text

    ###########################################################################
    def cases(self):
        """Prepare case handling."""
        # case = []
        # count = 0
        for token in self.identified.iteritems():
            name, value = token
            # case += ['error = RPN_%s_RPN(&the)' % (name), ]
            self.caselist += ['{ *dstack++ = %s; }' % (name), ]
        return self.caselist


###############################################################################
class CUDAMathFunctions(object):
    """CUDAMathFunctions class"""

    found = set()

    ###########################################################################
    def __init__(self, **kw):
        """CUDAMathFunctions __init__"""
        clip = kw.get(
            'clip',
            True)
        filename = kw.get(
            'filename',
            '/usr/local/cuda-5.5/targets/x86_64-linux/include/'
            'math_functions.h')
        signature = kw.get(
            'signature',
            'extern __host__ __device__ __device_builtin__ float')
        self.caselist = []
        with open('RPN_CUDA_functions.txt', 'w') as manual:
            print>>manual, '# RPN CUDA functions'
            self.hrule(manual)
            signatureAB = '(float x, float y)'
            signatureA_ = '(float x)'
            self.one = {}
            self.two = {}
            with open(filename) as source:
                for line in source:
                    if line.startswith(signature):
                        A, B, C = line.partition('float')
                        if not C:
                            continue
                        function = C.strip()
                        if function.endswith(') __THROW;'):
                            function = function[:-9]
                        name, paren, args = function.partition('(')
                        if name in CUDAMathFunctions.found:
                            continue
                        else:
                            CUDAMathFunctions.found.add(name)
                        if signatureAB in function:
                            # print 'AB', function
                            if clip:
                                name = name[:-1]  # remove f
                            self.two[name] = name
                            self.caselist += ['{ ab %s(a, b); }' % (name), ]
                        elif signatureA_ in function:
                            # print 'A_', function
                            self.one[name] = name
                            self.caselist += ['{ a_ %s(a); }' % (name), ]
                        else:
                            continue
            print>>manual, '# functions of one float parameter'
            print>>manual, '# pop A and push fun(A).'
            self.hrule(manual)
            for cuda, inner in self.one.iteritems():
                print>>manual, 'float %s(float) // %s' % (inner, name)
            self.hrule(manual)
            print>>manual, '# functions of two float parameters'
            print>>manual, '# pop A, pop B and push fun(A, B)'
            self.hrule(manual)
            for cuda, inner in self.two.iteritems():
                print>>manual, 'float %s(float, float) // %s' % (inner, name)
            self.hrule(manual)

    ###########################################################################
    def hrule(self, stream):
        """CUDAMathFunctions hrule"""
        print>>stream, '#' + '_' * 78

    ###########################################################################
    def functions(self):
        """CUDAMathFunctions functions"""
        return ''

    ###########################################################################
    def cases(self):
        """CUDAMathFunctions cases"""
        return self.caselist


###############################################################################
class Timing(object):
    """Timing class"""
    text = ''

    ###########################################################################
    def __init__(self, msg=''):
        """Timing __init__"""
        self.msg = msg

    ###########################################################################
    def __enter__(self):
        """Timing __enter__"""
        self.t0 = time()

    ###########################################################################
    def __exit__(self, typ, value, tb):
        """Timing __exit__"""
        Timing.text += '%40s: %e\n' % (self.msg, (time() - self.t0))


###############################################################################
class Function(object):
    """Function class"""

    ###########################################################################
    def __init__(self, **kw):
        """Function __init__"""
        self.index = kw.get('start', 0)
        self.name = {}
        self.body = ""
        self.case = ""
        self.tab = " " * 12
        self.final = [0]
        self.code = {'#%d' % d: d for d in range(kw.get('bss', 64))}
        self.bss = self.code.keys()

        for i, name in enumerate(
                kw.get('handcode', [
                    'swap', 'add', 'mul', 'ret', 'sub', 'div',
                    'call', 'noop', 'invert', 'push', 'pop', 'jmp', ])):
            self.add_name(name, i)

    ###########################################################################
    def add_name(self, name, index):
        """Function add_name"""
        self.code[name] = index
        self.name[index] = name

    ###########################################################################
    def assemble(self, source, DATA, **kw):
        """Function assemble"""

        self.label = {'code': [], 'data': [], }
        self.data = []
        fixups = {}
        self.clabels = {}
        self.backclabels = {}
        self.dlabels = {}
        self.backdlabels = {}
        self.final = []
        extra = 0

        for offset, name in enumerate(DATA):
            name = str(name)
            label, colon, datum = name.partition(':')
            if colon:
                self.dlabels[label] = offset + extra
                self.backdlabels[offset + extra] = label
                self.label['data'] += [label, ]
                # print '\t\t\tdata', label, offset + extra
            else:
                datum = label
            values = datum.split()
            self.data += values
            extra += len(values) - 1
        # print 'A0', self.backclabels
        # print 'B0', self.clabels

        for offset, name in enumerate(source):
            name = re.sub(' \t', '', name)
            label, colon, opname = name.partition(':')
            if not colon:
                label, opname = None, label
                # print 'name = %s', (opname)
            else:
                assert label not in self.clabels.keys()
                self.clabels[label] = offset
                self.backclabels[offset] = label
                self.label['code'] += [label, ]
                # print '\t\t\tcode', label

            if opname in self.code.keys():
                self.final += [self.code[opname], ]
                # print 'instruction'
            else:
                self.final += [stop, ]
                fixups[opname] = fixups.get(opname, []) + [offset, ]
                # print 'opname:fixup = %s/%s' %(opname, offset)

        for label, offsets in fixups.iteritems():
            if not label:
                continue
            if label in self.clabels:
                for offset in offsets:
                    self.final[offset] = self.clabels[label]

        if (not self.final) or (self.final[-1] != stop):
            self.final += [stop, ]
        # print 'A1', self.backclabels
        # print 'B1', self.clabels
        if kw.get('verbose', False):
            # print source
            # print self.final
            direct = False
            # print '(',
            for code in self.final:
                if not direct:
                    name = self.name[code]
                    # print "'%s'," % (name),
                    if name in ('push', 'call', 'jmp'):
                        direct = True
                else:
                    label = self.backclabels.get(code, None)
                    if offset is None:
                        # print label, "'#%d'" % (code),
                        pass
                    else:
                        # print "'#%d'," % (code),
                        pass
                    direct = False
            # print ')'
        # print 'A2', self.backclabels
        # print 'B2', self.clabels

    ###########################################################################
    def disassemble(self, **kw):
        """Function disassemble"""
        verbose = kw.get('verbose', False)
        if not verbose:
            return
        direct = False
        # print self.data
        # print self.label['data']
        # print self.backclabels
        print '#'*79
        print '.data'
        # print '#', self.data
        nl = False
        comma = ''
        for offset, datum in enumerate(self.data):
            if not datum:
                continue
            label = self.backdlabels.get(offset, None)
            if label and label in self.label['data']:
                if nl:
                    print
                print '%-12s%+11.9f' % (label+':', float(datum)),
                comma = ','
            else:
                print comma + ' %+11.9f' % (float(datum)),
                comma = ','
            nl = True
        print
        print '#'*79
        print '.code'
        # print '#', self.final
        for offset, code in enumerate(self.final):
            if direct:
                clabel = self.backclabels.get(code, None)
                if clabel:
                    print clabel
                else:
                    print '#%d' % (code)
                direct = False
            else:
                label = self.backclabels.get(offset, None)
                name = self.name[code]
                direct = (name in ('push', 'call', 'jmp'))
                if label and label in self.label['code']:
                    print '%-12s%s' % (label+':', name),
                else:
                    print '            %s' % (name),
                if not direct:
                    print
        print '.end'
        print '#'*79

    ###########################################################################
    def add_body(self, fmt, **kw):
        """Function add_body"""
        cmt = '/*************************************************************/'
        base = "__device__ int " + cmt + "\nRPN_%(name)s_RPN(Thep the) "
        self.body += ((base + fmt) % kw) + '\n'

    ###########################################################################
    def add_case(self, **kw):
        """Function add_case"""
        k = {'number': self.index}
        k.update(kw)
        casefmt = "case %(number)d: error = RPN_%(name)s_RPN(&the); break;\n"
        self.case += self.tab + casefmt % k
        self.code[kw['name']] = self.index
        self.add_name(kw['name'], self.index)

    ###########################################################################
    def add_last(self):
        """Function add_last"""
        self.index += 1

    ###########################################################################
    def unary(self, **kw):
        """Function unary"""
        self.add_case(**kw)
        self.add_body("{ A_ %(name)s(A); return 0; }", **kw)
        self.add_last()

    ###########################################################################
    def binary(self, **kw):
        """Function binary"""
        self.add_case(**kw)
        self.add_body("{ AB %(name)s(A,B); return 0; }", **kw)
        self.add_last()


###############################################################################
def CudaRPN(inPath, outPath, mycode, mydata, **kw):
    """CudaRPN implements the interface to the CUDA run environment.
    """
    verbose = kw.get('verbose', False)
    BLOCK_SIZE = 1024  # Kernel grid and block size
    STACK_SIZE = 64
    # OFFSETS = 64
    # unary_operator_names = {'plus': '+', 'minus': '-'}
    function = Function(
        start=len(hardcase),
        bss=64,
        handcode=kw.get('handcode'))

    with Timing('Total execution time'):
        with Timing('Get and convert image data to gpu ready'):
            im = Image.open(inPath)
            px = array(im).astype(float32)
            function.assemble(mycode, mydata, verbose=True)
            function.disassemble(verbose=True)
            cx = array(function.final).astype(int32)
            dx = array(function.data).astype(float32)
        with Timing('Allocate mem to gpu'):
            d_px = mem_alloc(px.nbytes)
            memcpy_htod(d_px, px)
            d_cx = mem_alloc(cx.nbytes)
            memcpy_htod(d_cx, cx)
            d_dx = mem_alloc(dx.nbytes)
            memcpy_htod(d_dx, dx)
        with Timing('Kernel execution time'):
            block = (BLOCK_SIZE, 1, 1)
            checkSize = int32(im.size[0]*im.size[1])
            grid = (int(im.size[0] * im.size[1] / BLOCK_SIZE) + 1, 1, 1)
            kernel = INCLUDE + HEAD + function.body + convolve + TAIL
            sourceCode = kernel % {
                'pixelwidth': 3,
                'stacksize': STACK_SIZE,
                'case': function.case}
            with open("RPN_sourceCode.c", "w") as target:
                print>>target, sourceCode
            module = SourceModule(sourceCode)
            func = module.get_function("RPN")
            func(d_px, d_cx, d_dx, checkSize, block=block, grid=grid)
        with Timing('Get data from gpu and convert'):
            RPNPx = empty_like(px)
            memcpy_dtoh(RPNPx, d_px)
            RPNPx = uint8(RPNPx)
        with Timing('Save image time'):
            pil_im = Image.fromarray(RPNPx, mode="RGB")
            pil_im.save(outPath)
    # Output final statistics
    if verbose:
        print '%40s: %s%s' % ('Target image', outPath, im.size)
        print Timing.text

###############################################################################
INCLUDE = """// RPN_sourceCode.c
// GENERATED KERNEL IMPLEMENTING RPN ON CUDA

#include <math.h>
"""

HEAD = """
#define a_ float a = *--dstack; *dstack++ =
#define ab float a = *--dstack; float b = *--dstack; *dstack++ =

typedef struct _XY {
    int x;
    int y;
    float n;
} XY, *XYp;

/************************** HANDCODE FUNCTIONS *******************************/
"""

handcode = {
    'pop': "{ --dstack; }",
    'quit': "{ stop = 1; }",
    'noop': "{ }",
    'invert': "{ a_ 1.0 - a; }",
    'swap': """{
                float a = *--dstack;
                float b = *--dstack;
                *++dstack = a;
                *++dstack = b;
            }                                                          """,
    'push': "{ *dstack++ = data[code[ip++]]; }",
    'add': "{ ab a + b; }",
    'sub': "{ ab a - b; }",
    'mul': "{ ab a * b; }",
    'div': "{ ab a / b; }",
    'call': """{
                int to = code[ip++];
                cstack[sp++] = ip;
                ip = to;
            }                                                          """,
    'ret': "{ ip = cstack[--sp]; }",
    'jmp': "{ ip = code[ip]; }",
}

hardcase = []

for i, (case, code) in enumerate(handcode.iteritems()):
    hardcase += ['/* %s */ %s' % (case, code), ]
    if 'stop' in code:
        stop = i

HEAD += """
/************************** CUDA FUNCTIONS ***********************************/
"""

# Name header files and function signatures of linkable functions.
CUDA_sources = {
    '/usr/local/cuda-5.5/targets/x86_64-linux/include/math_functions.h': [
        'extern __host__ __device__ __device_builtin__ float',
        'extern __device__ __device_builtin__ __cudart_builtin__ float',
        'extern _CRTIMP __host__ __device__ __device_builtin__ float',
    ],
    '/usr/local/cuda-5.5/targets/x86_64-linux/include/device_functions.h': [
        # 'extern __device__ __device_builtin__ __cudart_builtin__ float',
        'extern _CRTIMP __host__ __device__ __device_builtin__ float',
        # 'extern __device__ __device_builtin__ float',
    ]
}

INCLUDE += '#include <%s>\n' % ('math_constants.h')

# Ingest header files to make use of linkable functions.
CUDA_constants = CUDAMathConstants()
hardcase += CUDA_constants.cases()

for filename, signatures in CUDA_sources.iteritems():
    stars = max(2, 73 - len(filename))
    pathname, twixt, basename = filename.partition('/include/')
    INCLUDE += '#include <%s>\n' % (basename)
    left = stars/2
    right = stars - left
    left, right = '*' * left, '*' * right
    HEAD += '/*%s %s %s*/\n' % (left, filename, right)
    for signature in signatures:
        CUDA_functions = CUDAMathFunctions(
            filename=filename,
            signature=signature,
            clip=True)
        hardcase += CUDA_functions.cases()

###############################################################################
convolve = """
// data: the data field from which to convolve.
// kn: a length L array of coefficients (terminated by 0.0)
// kx: a length L array of x offsets
// ky: a length L array of y offsets
// X: width of data field (stride, not necessarily visible image width)
// Y: height of data field.
// C: color band (0, 1, or 2)
__device__ float planar_convolve(
    float *data, float *kn, int *kx, int *ky, int X, int Y, int C)
{
    float K = 0.0;
    float V = 0.0;
    int x0 = (threadIdx.x + blockIdx.x * blockDim.x);
    int y0 = (threadIdx.y + blockIdx.y * blockDim.y);
    int D = X * Y;
    int N = 0;
    float ki;
    while((ki = *kn++) != 0.0) {
        int xi = *kx++;
        int yi = *ky++;
        int x = (x0-xi);
        int y = (y0-yi);
        int d = C + (x + y * X) * 3;
        if(d < 0 || d >= D) continue;
        V += data[d];
        K += ki;
        N += 1;
    };
    if(N == 0) {
        V = 0.0;
    } else {
        V /= K*N;
    }
    return V;
}

//__device__ void planar_ring_test(float *data, int C) {
//    float kn[5] = { 1.0, 1.0, 1.0, 1.0 };
//    int kx[5] = { +1,  0, -1,  0, 0 };
//    int ky[5] = {  0, +1,  0, -1, 0 };
//}
"""

convolutionGPU = """
__global__ void convolutionGPU(
                               float *d_Result,
                               float *d_Data,
                               int dataW,
                               int dataH )
{
    //////////////////////////////////////////////////////////////////////
    // most slowest way to compute convolution
    //////////////////////////////////////////////////////////////////////

    // global mem address for this thread
    const int gLoc = threadIdx.x +
                     blockIdx.x * blockDim.x +
                     threadIdx.y * dataW +
                     blockIdx.y * blockDim.y * dataW;

    float sum = 0;
    float value = 0;

    for (int i = -KERNEL_RADIUS; i <= KERNEL_RADIUS; i++)	// row wise
        for (int j = -KERNEL_RADIUS; j <= KERNEL_RADIUS; j++)	// col wise
        {
            // check row first
            if (blockIdx x == 0 && (threadIdx x + i) < 0)	// left apron
                value = 0;
            else if ( blockIdx x == (gridDim x - 1) &&
                        (threadIdx x + i) > blockDim x-1 )	// right apron
                value = 0;
            else
            {
                // check col next
                if (blockIdx y == 0 && (threadIdx y + j) < 0)	// top apron
                    value = 0;
                else if ( blockIdx y == (gridDim y - 1) &&
                            (threadIdx y + j) > blockDim y-1 )	// bottom apron
                    value = 0;
                else	 // safe case
                    value = d_Data[gLoc + i + j * dataW];
            }
            sum += value *
                d_Kernel[KERNEL_RADIUS + i] *
                d_Kernel[KERNEL_RADIUS + j];
        }
        d_Result[gLoc] = sum;
}
"""
###############################################################################

TAIL = """
__device__ int machine(int *code, float *data, float *value) {
    const float numerator = 255.0;
    const float denominator = 1.0 / numerator;
    float DSTACK[%(stacksize)d];
    int CSTACK[%(stacksize)d];
    int opcode;
    int error = 0;
    int *cstack = &CSTACK[0];
    float *dstack = &DSTACK[0];
    int ip = 0, sp = 0, stop = 0;

    *dstack++ = *value * denominator;
    *value = 0.0;
    while((!stop) && (opcode = code[ip++]) != 0) {
        switch(opcode) {
"""

for i, case in enumerate(hardcase):
    TAIL += ' '*12
    TAIL += 'case %3d: %-49s; break;\n' % (i, case)

TAIL += """
%(case)s
            default: error = opcode; break;
        }
        stop |= !!error;
    }
    if(error) {
        *value = float(error);
    } else {
        *value = *--dstack * numerator;
    }

    return error;
}

__global__ void RPN( float *inIm, int *code, float *data, int check ) {
    const int pw = %(pixelwidth)s;
    const int idx = (threadIdx.x ) + blockDim.x * blockIdx.x ;

    if(idx * pw < check * pw) {
        const int offset = idx * pw;
        int error = 0;
        int c;

        for(c=0; c<pw && !error; ++c) {
            error += machine(code, data, inIm + offset + c);
        }
    }
}
"""


###############################################################################
if __name__ == "__main__":
    Banner(arg=[argv[0] + ': main', ], bare=True)
    if len(argv) == 1:
        Banner(arg=[argv[0] + ': default code and data', ], bare=True)
        DATA = [0.0, 1.0]
        CODE = [
            'push', '#1',
            'sub',
            'noop',
            'call', 'here',
            'quit',
            'here:ret', ]
    else:
        Banner(arg=[argv[0] + ': code and data from file: ', ], bare=True)
        DATA = []
        CODE = []
        STATE = 0
        with open(argv[1]) as source:
            for number, line in enumerate(source):
                line = line.strip()
                if STATE == 0:
                    if line.startswith('#'):
                        # print number, 'comment'
                        continue
                    elif line.startswith('.data'):
                        # print number, 'keyword .data'
                        STATE = 1
                    else:
                        assert False, '.data section must come first'
                elif STATE == 1:
                    if line.startswith('#'):
                        # print number, 'comment'
                        continue
                    line = re.sub(r':\s+', ':', line)
                    if line.startswith('.code'):
                        # print number, 'keyword .code'
                        STATE = 2
                    else:
                        # print number, 'add data'
                        DATA += re.split(r'\s+', line)
                elif STATE == 2:
                    if line.startswith('#'):
                        # print number, 'comment'
                        continue
                    line = re.sub(r':\s+', ':', line)
                    # print number, 'add code'
                    CODE += re.split(r'\s+', line)

    # print '.data\n', '\n'.join([str(datum) for datum in data])
    # print '.code\n', '\n'.join(code)

    Banner(arg=[argv[0] + ': run in CUDA', ], bare=True)
    CudaRPN(
        'img/source.png',
        'img/target.png',
        CODE,
        DATA,
        handcode=handcode
    )
###############################################################################
