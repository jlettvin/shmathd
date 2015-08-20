#!/usr/bin/env python

import sys, string, itertools
from optparse import OptionParser

def outputBanner(listOfLines, **kw):
    """
    outputBanner outputs a colorful banner for which it is easy to scan.
    @param listOfLines is a list of strings (with no newlines).
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

    An empty listOfLines means no banner will be output.

    xterm escape codes, including those used for color, are found here:
    http://en.wikipedia.org/wiki/ANSI_escape_code
    """
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
    lead = kw.get('lead', 3)
    lead = lead if 0 < lead <= 8 else 3

    """Fetch a validated line width from kw or use the default 50."""
    width = kw.get('width', 50)
    width = width if lead < width <= 80 else 50

    """Fetch a validated line character from kw or use the default *."""
    divider = kw.get('divider', '*')
    divider = divider if isinstance(divider, str) and len(divider) == 1 else '*'
    start = divider*lead
    divider *= width

    """Fetch a validated output stream from kw or use the default sys.stdout."""
    output = kw.get('output', sys.stdout)
    output = output if isinstance(output, type(sys.stdout)) else sys.stdout

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

    """These values enable choice of head and tail."""
    listOfLines = listOfLines if listOfLines else ['default banner line',]
    listLength = len(listOfLines)
    lastIndex = listLength - 1

    """Output the list of lines with appropriate heads and tails."""
    for index in range(listLength):
        print>>output, head[index==0 or bare]+listOfLines[index]+tail[index==lastIndex]

if __name__ == '__main__':
    def test():
        output = sys.stdout
        print>>output, 'hello'
        # Here is an example using no keywords (all defaults).
        outputBanner(['colorful', 'multihued'])
        # Here is an example using some keywords (some defaults).
        outputBanner(['and', 'useful'], color = 'my', divider = '=', width = 10)
        # Here is an example using all keywords.
        outputBanner(
            ['gift for all', 'to make banners'],
            color = 'ym', divider = '~', lead = 5, width = 80, output = output)
        print>>output, 'world'
        # Now try all possible non-matching color pairs.
        for color in list(itertools.product('0rgybmcw', repeat=2)):
            if color[0] == color[1]: continue
            normal = string.join(color, '')
            bolder = normal + '!'
            outputBanner([normal], color = normal)
            outputBanner([bolder], color = bolder)
        outputBanner([])
        outputBanner(['bare'], bare=True)

    def main(args, **kwargs):
        test() if kwargs.get('test') else outputBanner(args, **kwargs)

    parser = OptionParser()
    parser.add_option('-b', '--bare'   , action="store_true" , default=False,help="No head/tail")
    parser.add_option('-t', '--test'   , action="store_true" , default=False,help="Test")
    parser.add_option('-c', '--color'  , default='r-'        , help='color pair (i.e. "rg")')
    parser.add_option('-d', '--divider', default='*'         , help='character to form divider')
    parser.add_option('-w', '--width'  , default=50, type=int, help='divider width')
    parser.add_option('-l', '--lead'   , default=3 , type=int, help='lead width')
    (opts, args) = parser.parse_args()
    kwargs = vars(opts)

    main(args, **kwargs)
