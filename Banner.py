#!/usr/bin/env python

"""Banner.py
Copyright(c) 2012-2015 Jonathan D. Lettvin, All Rights Reserved.

Banner is used to output visually useful titles from the command-line.
Colors are from VT100 legacy support in most terminal emulators.
0 black
r red
g green
y yellow
b blue
m magenta
c cyan
w white
Divider lines are composed from multiple characters (default '***').

Usage:
    Banner.py \
[--bare] \
[--test] \
[--verbose] \
[--color=<COLOR>] \
[--divider=<CHAR>] \
[--lead=<LEAD>] \
[--width=<COUNT>] \
[<args>...]
    Banner.py (-h | --help)
    Banner.py --version

Options:
    -v, --verbose         Verbose [default: False]
    -b, --bare            Minimized output [default: False]
    -t, --test            Exhaustive test [default: False]
    -c, --color=<COLOR>   Foreground/background 2 color spec [default: r-]
    -d, --divider=<CHAR>  Char to use when drawing lines [default: *]
    -l, --lead=<LEAD>     Lead char count when drawing lines [default: 3]
    -w, --width=<COUNT>   Char count to use when drawing lines [default: 70]
"""

from docopt     import (docopt)
from pprint     import (pprint)
from optparse   import (OptionParser)
from os         import (uname, getlogin)
from datetime   import (datetime)
from sys        import (stdout)
from string     import (join)
from itertools  import (product)

from terminalsize import (get_terminal_size)

version = "Banner.py 1.1.0"

def outputBanner(**kw):
    """
    outputBanner outputs a colorful banner for which it is easy to scan.
    @param kw['color'] is a color pair from colorList, defaulting to 'wg'.
    @param kw['width'] is the width of the banner line divider.
    @param kw['divider'] is the single character used in the line divider.
    @param kw['output'] is the output stream to which the banner is written.

    @param kw['color'] can have a 3rd character '!' meaning bold.

    The output color is changed to the new specified color.
    A horizontal line of width divider characters is output.
    The list of lines are output with a line start of divider characters.
    A horizontal line of width divider characters is output.
    The output color is changed to the xterm default colors.

    xterm escape codes, including those used for color, are found here:
    http://en.wikipedia.org/wiki/ANSI_escape_code
    """
    if kw.get('verbose'): pprint(kw)
    colorList = {'0':0, 'r':1, 'g':2, 'y':3, 'b':4, 'm':5, 'c':6, 'w':7}

    """Fetch a validated color from kw or use the default white on green."""
    color = kw.get('color', 'wg')
    hue = normal = '0'
    bold = 1 if len(color) == 3 and color[2] == '!' else 0
    if bold: color = color[0:2]
    if len(color) == 2:
        if colorList.has_key(color[0]) and colorList.has_key(color[1]):
            hue = '%d;3%d;4%d' % (bold, colorList[color[0]], colorList[color[1]])

    """Fetch a validated lead width from kw or use the default 3."""
    lead = int(kw.get('lead', 3))
    lead = lead if 0 < lead <= 8 else 3

    """Fetch a validated line width from kw or use the default 70."""
    width = int(kw.get('width', 70))
    width = width if lead < width <= 80 else 70

    """Fetch a validated line character from kw or use the default *."""
    divider = kw.get('divider', '*')
    divider = divider if isinstance(divider, str) and len(divider) == 1 else '*'
    start = divider*lead
    divider *= width

    """Fetch a validated output stream from kw or use the default sys.stdout."""
    output = kw.get('output', stdout)
    output = output if isinstance(output, type(stdout)) else stdout

    """This is the standard prefix for xterm escape sequences."""
    prefix = '\x1b\x5b'

    """The constructed heads and tails for lines for when they are output."""
    bare = kw.get('bare', False)
    if bare:
        head = ['', prefix + hue + 'm' + start + ' ']
        tail = ['', prefix + normal + 'm']
    else:
        head = [start + ' ', prefix + hue + 'm' + divider+ '\n' + start + ' ']
        tail = ['', '\n' + divider+ prefix + normal + 'm']

    (twidth, theight) = get_terminal_size()

    """These values enable choice of head and tail."""
    listOfLines = []
    #listOfLines = ['',]
    listOfLines += kw['args']
    listOfLines = listOfLines if listOfLines else [
            getlogin()
            +' '+
            datetime.now().isoformat()
            +' '+
            list(uname())[1]
            ,
            ]
    # VT100 emulator doesn't right-fill the first line with correct color.
    listOfLines[0] = listOfLines[0]+' '*(twidth - lead - 1 - len(listOfLines[0]))
    listLength = len(listOfLines)
    lastIndex = listLength - 1

    """Output the list of lines with appropriate heads and tails."""
    for index in range(listLength):
        print>>output, head[index==0 or bare]+listOfLines[index]+tail[index==lastIndex]

if __name__ == '__main__':
    def test():
        output = stdout
        print>>output, 'hello'
        # Here is an example using no keywords (all defaults).
        outputBanner(args=['colorful', 'multihued'])
        # Here is an example using some keywords (some defaults).
        outputBanner(args=['and', 'useful'], color = 'my', divider = '=', width = 10)
        # Here is an example using all keywords.
        outputBanner(
            args=['gift for all', 'to make banners'],
            color = 'ym', divider = '~', lead = 5, width = 80, output = output)
        print>>output, 'world'
        # Now try all possible non-matching color pairs.
        for color in list(product('0rgybmcw', repeat=2)):
            if color[0] == color[1]: continue
            normal = join(color, '')
            bolder = normal + '!'
            outputBanner(args=[normal], color = normal)
            outputBanner(args=[bolder], color = bolder)
        outputBanner(args=[])
        outputBanner(args=['bare'], bare=True)

    def main(**kwargs):
        test() if kwargs.get('test') else outputBanner(**kwargs)

    kwargs = {
            k.replace('-','').replace('<','').replace('>',''): v
            for k,v in
            docopt(__doc__,version=version).iteritems()}
    main(**kwargs)
