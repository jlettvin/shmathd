#!/usr/bin/env python
# pylint: disable=W0142

"""Banner.py
Copyright(c) 2012-2015 Jonathan D. Lettvin, All Rights Reserved.
License: GPLv3 http://www.gnu.org/licenses/gpl-3.0.en.html

Banner is used to output visually useful titles from the command-line.

Usage:
    Banner.py [-b] [-c <COLS>] [-d <DRAW>] [-l <LEAD>] [-t <TINT>] [<arg>...]
    Banner.py (-h | --help)
    Banner.py -u UNIT
    Banner.py --version

Options:
    -b, --bare         Minimized output                     [default: False]
    -c, --cols=<COLS>  Char count to use when drawing lines [default: 0]
    -d, --draw=<DRAW>  Char to use when drawing lines       [default: @]
    -l, --lead=<LEAD>  Lead char count when printing banner [default: 3]
    -t, --tint=<TINT>  Foreground/background 2 color pair   [default: g0!]
    -u, --unit=<UNIT>  Unit test example number             [default: 0]

bare: Eliminate the "draw" character lines above and below the banner.
tint: Use a VT100 foreground/background color pair in the banner.
draw: Use a specific character (like _) to form draw lines (_______)
lead: Use a specific length (like 3) on text lines (@@@ your banner text)
cols: Use a specific length (like 14) to form draw lines (@@@@@@@@@@@@@@)
unit: Show example output for various arguments.

unit 1: Show example headers for all combinations of output color pairs.

Text for default banner is "{login} {datetime} {machine}".
Draw lines are composed from multiple draw characters.
Colors are from VT100 legacy support in most terminal emulators.
    0:black        r:red           g:green         y:yellow
    b:blue         m:magenta       c:cyan          w:white

Example 1: jlettvin$ ./Banner.py
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@ jlettvin 2015-08-22T13:42:50.985580 Jonathans-MacBook-Pro.local
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

Example 2: jlettvin$ ./Banner.py --draw _ --cols 30 hello world
______________________________
___ hello
___ world
______________________________

Example 2: jlettvin$ ./Banner.py --bare "Lorem ipsum dolor sit amet"
@@@ Lorem ipsum dolor sit amet
"""

###############################################################################
from os import (uname, getlogin, environ)
from sys import (stdout, argv)
from docopt import (docopt)
from struct import (unpack)
from string import (join)
from platform import (system)
from datetime import (datetime)
from itertools import (product)
from subprocess import (check_call)

###############################################################################
VERSION = "Banner.py 1.1.0"
OSNAME = system()
TINTLIST = {'0': 0, 'r': 1, 'g': 2, 'y': 3, 'b': 4, 'm': 5, 'c': 6, 'w': 7}
OPTSLIST = {'b': 'bare', 'c': 'cols', 'd': 'draw', 'l': 'lead', 't': 'tint'}


###############################################################################
def columns():
    """
Achieving left-to-right color-fill in a VT100 terminal emulator
depends on window width.  Finding that size depends on the OS.
This code is logically identical to the code found at the following URL:
stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    cols = 80
    # _________________________________________________________________________
    if OSNAME == 'Windows':
        # First try screen info resource call.
        try:
            from ctypes import (windll, create_string_buffer)
            handle = windll.kernel32.GetStdHandle(-12)  # -11:stdout -12:stderr
            buf = create_string_buffer(22)
            resource = windll.kernel32.GetConsoleScreenBufferInfo(handle, buf)
            if resource:
                (left, right) = unpack("hhhhHhhhhhh", buf.raw)[5:2]
                cols = right - left + 1
        except ImportError:
            pass
        # If resource fails, try tput, or default to 80.
        try:
            cols = int(check_call(['tput', 'cols']))
        except StandardError:
            pass
    # _________________________________________________________________________
    elif OSNAME in ['Linux', 'Darwin'] or OSNAME.startswith('CYGWIN'):
        # First try IOCTL calls on stdio handles.
        for descriptor in (0, 1, 2):
            try:
                from fcntl import (ioctl)
                from termios import (TIOCGWINSZ)
                shape = unpack('hh', ioctl(descriptor, TIOCGWINSZ, '1234'))
                cols = int(shape[1])
            except ImportError:
                pass
        # If IOCTL fails, try tput, or default to 80
        if cols == 0:
            cols = int(environ.get('COLUMNS', 80))
    # _________________________________________________________________________
    else:
        # Neither Windows nor Sys V (unix, Mac, or cygwin).
        pass
    return cols


###############################################################################
def banner(**kw):
    """
    banner outputs a colorful banner for which it is easy to scan.
    @param kw['tint'] is a color pair from TINTLIST, defaulting to 'wg!'.
    @param kw['cols'] is the width of the banner line draw.
    @param kw['draw'] is the single character used in the line draw.
    @param kw['output'] is the output stream to which the banner is written.

    @param kw['tint'] can have a 3rd character '!' meaning bold.

    The output color pair is changed to the new specified color pair.
    A horizontal line of cols draw characters is output.
    The list of lines are output with a line start of draw characters.
    A horizontal line of cols draw characters is output.
    The output color pair is changed to the xterm default color pairs.

    xterm escape codes, including those used for color, are found here:
    http://en.wikipedia.org/wiki/ANSI_escape_code
    """
    timestamp = datetime.now().isoformat()
    twidth = columns()              # Get terminal width (see function above).

    # _________________________________________________________________________
    # Fetch a validated color from kw or use the default white on green.
    tint = kw.get('tint', 'g0!')  # See default value for --tint.
    hue = normal = '0'
    bold = int(len(tint) == 3 and tint[2] == '!')
    if len(tint) > 1:
        if tint[0] in TINTLIST and tint[1] in TINTLIST:
            hue = '%d;3%d;4%d' % (bold, TINTLIST[tint[0]], TINTLIST[tint[1]])

    # Fetch a validated lead width from kw or use the default 3.
    lead = max(3, min(int(kw.get('lead', 8)), 8))  # See --lead default value.

    # Fetch a validated line width from kw or use the default 0.
    width = max(twidth, min(int(kw.get('cols', 0)), twidth))

    # Fetch a validated line character from kw or use the default @.
    draw = kw.get('draw', '@')
    draw = draw if isinstance(draw, str) and len(draw) == 1 else '@'
    start = draw*lead
    divider = draw*width

    # Fetch a validated output stream from kw or use the default sys.stdout.
    output = kw.get('output', stdout)
    output = output if isinstance(output, type(stdout)) else stdout

    # This is the standard prefix for xterm escape sequences.
    prefix = '\x1b\x5b'

    # The constructed heads and tails for lines for when they are output.
    bare = kw.get('bare', False)

    # _________________________________________________________________________
    # These values enable choice of head and tail.
    lines = kw.get('arg', [])
    lined = [getlogin() + ' ' + timestamp + ' ' + list(uname())[1], ]
    lines = lines if lines else lined

    # _________________________________________________________________________
    # VT100 emulator doesn't right-fill the first line with correct color.
    # Special case the first line, whether divider or bare.
    if bare:
        head = ['', prefix + hue + 'm' + start + ' ']
        tail = ['', prefix + normal + 'm']
        size = twidth - lead - 1 - len(lines[0])
        fill = '' if size < 0 else ' '*size
        lines[0] = lines[0]+fill
    else:
        head = [start + ' ', prefix + hue + 'm' + divider]
        tail = ['', '\n' + divider + prefix + normal + 'm']
        size = twidth - len(divider)
        fill = '' if size < 0 else ' '*size
        head[1] = head[1] + fill + '\n' + start + ' '

    length = len(lines)
    final = length - 1

    # _________________________________________________________________________
    # Output the list of lines with appropriate heads and tails.
    for index in range(length):
        print>>output, head[index == 0 or bare] + \
            lines[index]+tail[index == final]

###############################################################################
if __name__ == '__main__':

    ###########################################################################
    def command(unit, **kw):
        """command shows what the command-line would look like for **kw."""
        text = 'UNIT TEST %d$ ' % (unit) + argv[0]
        for key, val in kw.iteritems():
            key = OPTSLIST.get(key, key)
            text += ' --'+str(key)+'='+str(val) if key != 'arg' else ''
        args = kw.get('arg', [])
        if args:
            for arg in args:
                text += ' "%s"' % arg
        return text

    ###########################################################################
    def test1():
        """Unit test exhaustively exercising some parameters."""
        output = stdout
        print>>output, 'hello'
        # Here is an example using no keywords (all defaults).
        banner(arg=['colorful', 'multihued'])
        # Here is an example using some keywords (some defaults).
        banner(arg=['and', 'useful'], tint='my', draw='=', cols=10)
        # Here is an example using all keywords.
        banner(
            arg=['gift for all', 'to make banners'],
            tint='ym', draw='~', lead=5, cols=80, output=output)
        print>>output, 'world'
        # Now try all possible non-matching color pairs.
        for color in list(product('0rgybmcw', repeat=2)):
            if color[0] == color[1]:
                continue
            normal = join(color, '')
            bolder = normal + '!'
            banner(arg=[normal], tint=normal)
            banner(arg=[bolder], tint=bolder)
        banner(arg=[])
        banner(arg=['bare'], bare=True)

    ###########################################################################
    def test2():
        """Unit test showing multi-line message with frame."""
        args = {'arg': ['hello', 'world'], 'lead': '3'}
        print command(2, **args)
        banner(**args)

    ###########################################################################
    def test3():
        """Unit test showing single-line message without frame."""
        args = {
            'arg': ['hello world'], 'lead': '3', 'bare': True, 'tint': 'yb!'}
        print command(3, **args)
        banner(**args)

    ###########################################################################
    UNITS = [None, test1, test2, test3]

    ###########################################################################
    def main(**kw):
        """Main for operating Banner.py from the command-line"""
        unit = int(kw.get('unit', 0))
        if 0 < unit < len(UNITS):
            UNITS[unit]()
        else:
            banner(**kw)

    ###########################################################################
    KWARGS = {
        k.translate(None, "<->"): v
        for k, v in
        docopt(__doc__, version=VERSION).iteritems()}

    ###########################################################################
    main(**KWARGS)

###############################################################################
