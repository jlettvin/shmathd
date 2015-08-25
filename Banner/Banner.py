#!/usr/bin/env python

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
from docopt     import (docopt)
from os         import (uname, getlogin, open, ctermid, O_RDONLY, environ)
from sys        import (stdout, argv)
from platform   import (system)
from subprocess import (check_call)
from struct     import (unpack)
from pprint     import (pprint)
from optparse   import (OptionParser)
from string     import (join)
from itertools  import (product)
from datetime   import (datetime)

###############################################################################
version = "Banner.py 1.1.0"
tintList = {'0':0, 'r':1, 'g':2, 'y':3, 'b':4, 'm':5, 'c':6, 'w':7} # VT100
optsList = {'b':'bare', 'c':'cols', 'd':'draw', 'l':'lead', 't':'tint'}

###############################################################################
def columns():
    """
Achieving left-to-right color-fill in a VT100 terminal emulator
depends on window width.  Finding that size depends on the OS.
This code is logically identical to the code found at the following URL:
stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    osname = system()
    #__________________________________________________________________________
    if osname == 'Windows':
        # First try screen info resource call.
        try:
            from ctypes import windll, create_string_buffer
        except:
            return 80
        handle = windll.kernel32.GetStdHandle(-12) # -11:stdout, -12:stderr
        buf = create_string_buffer(22);
        windll.kernel32.GetConsoleScreenBufferInfo(handle, buf)
        if resource:
            (bx,by,cx,cy,wa,L,T,R,B,mx,my) = unpack("hhhhHhhhhhh", buf.raw)
            return R-L+1;
        # If resource fails, try tput, or default to 80.
        try:
            return int(check_call(['tput', 'cols']))
        except:
            return 80
    #__________________________________________________________________________
    elif osname in ['Linux', 'Darwin'] or osname.startswith('CYGWIN'):
        # First try IOCTL calls on stdio handles.
        for fd in (0,1,2):
            try:
                from fcntl import (ioctl)
                from termios import (TIOCGWINSZ)
                yx = unpack('hh', ioctl(fd, TIOCGWINSZ, '1234'))
                return int(yx[1])
            except:
                pass
        # If IOCTL fails, try tput, or default to 80
        return int(environ.get('COLUMNS', 80))
    #__________________________________________________________________________
    else:
        # Neither Windows nor Sys V (unix, Mac, or cygwin).
        return 80

###############################################################################
def Banner(**kw):
    """
    Banner outputs a colorful banner for which it is easy to scan.
    @param kw['tint'] is a color pair from tintList, defaulting to 'wg!'.
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

    #__________________________________________________________________________
    """Fetch a validated color from kw or use the default white on green."""
    tint = kw.get('tint', 'g0!')  # See default value for --tint.
    hue = normal = '0'
    bold = int(len(tint) == 3 and tint[2] == '!')
    if len(tint) > 1:
        if tintList.has_key(tint[0]) and tintList.has_key(tint[1]):
            hue = '%d;3%d;4%d' % (bold, tintList[tint[0]], tintList[tint[1]])

    """Fetch a validated lead width from kw or use the default 3."""
    lead = max(3, min(int(kw.get('lead', 8)), 8)) # See --lead default value.

    """Fetch a validated line width from kw or use the default 0."""
    width = max(twidth, min(int(kw.get('cols',0)), twidth))

    """Fetch a validated line character from kw or use the default @."""
    draw = kw.get('draw', '@')
    draw = draw if isinstance(draw, str) and len(draw) == 1 else '@'
    start = draw*lead
    divider = draw*width

    """Fetch a validated output stream from kw or use the default sys.stdout."""
    output = kw.get('output', stdout)
    output = output if isinstance(output, type(stdout)) else stdout

    """This is the standard prefix for xterm escape sequences."""
    prefix = '\x1b\x5b'

    """The constructed heads and tails for lines for when they are output."""
    bare = kw.get('bare', False)

    #__________________________________________________________________________
    """These values enable choice of head and tail."""
    listOfLines = kw.get('arg', [])
    defaultLine = [getlogin() +' '+ timestamp +' '+ list(uname())[1] ,]
    listOfLines = listOfLines if listOfLines else defaultLine

    #__________________________________________________________________________
    # VT100 emulator doesn't right-fill the first line with correct color.
    # Special case the first line, whether divider or bare.
    if bare:
        head = ['', prefix + hue + 'm' + start + ' ']
        tail = ['', prefix + normal + 'm']
        size = twidth - lead - 1 - len(listOfLines[0])
        fill = '' if size < 0 else ' '*size
        listOfLines[0] = listOfLines[0]+fill
    else:
        head = [start + ' ', prefix + hue + 'm' + divider]
        tail = ['', '\n' + divider + prefix + normal + 'm']
        size = twidth - len(divider)
        fill = '' if size < 0 else ' '*size
        head[1] = head[1] + fill + '\n' + start + ' '

    listLength = len(listOfLines)
    lastIndex = listLength - 1

    #__________________________________________________________________________
    """Output the list of lines with appropriate heads and tails."""
    for index in range(listLength):
        print>>output, head[index==0 or bare]+listOfLines[index]+tail[index==lastIndex]

###############################################################################
if __name__ == '__main__':

    ###########################################################################
    def command(unit, **kw):
        """command shows what the command-line would look like for **kw."""
        text = 'UNIT TEST %d$ ' % (unit) + argv[0]
        for k,w in kw.iteritems():
            k = optsList.get(k, k)
            text += ' --'+str(k)+'='+str(w) if k != 'arg' else ''
        args = kw.get('arg', [])
        if args:
            for arg in args:
                text += ' "%s"' % arg
        return text

    ###########################################################################
    def test1():
        output = stdout
        print>>output, 'hello'
        # Here is an example using no keywords (all defaults).
        Banner(arg=['colorful', 'multihued'])
        # Here is an example using some keywords (some defaults).
        Banner(arg=['and', 'useful'], tint = 'my', draw = '=', cols = 10)
        # Here is an example using all keywords.
        Banner(
            arg=['gift for all', 'to make banners'],
            tint = 'ym', draw = '~', lead = 5, cols = 80, output = output)
        print>>output, 'world'
        # Now try all possible non-matching color pairs.
        for color in list(product('0rgybmcw', repeat=2)):
            if color[0] == color[1]: continue
            normal = join(color, '')
            bolder = normal + '!'
            Banner(arg=[normal], tint = normal)
            Banner(arg=[bolder], tint = bolder)
        Banner(arg=[])
        Banner(arg=['bare'], bare=True)

    ###########################################################################
    def test2():
        args = {'arg':['hello', 'world'], 'lead':'3'}
        print command(2, **args)
        Banner(**args)

    ###########################################################################
    def test3():
        args = {'arg':['hello world'], 'lead':'3', 'bare':True, 'tint':'yb!'}
        print command(3, **args)
        Banner(**args)

    ###########################################################################
    units = [None, test1, test2, test3]

    ###########################################################################
    def main(**kwargs):
        unit = int(kwargs.get('unit', 0))
        units[unit]() if 0 < unit < len(units) else Banner(**kwargs)

    ###########################################################################
    kwargs = {
            k.replace('-','').replace('<','').replace('>',''): v
            for k,v in
            docopt(__doc__,version=version).iteritems()}

    ###########################################################################
    main(**kwargs)

###############################################################################
