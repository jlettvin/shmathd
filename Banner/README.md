# Banner.py
Python utility to generate colorized output for vt100 emulator terminals.

This may be used either standalone in bash scripts or as an import for Python scripts.

```
Copyright(c) 2012-2015 Jonathan D. Lettvin, All Rights Reserved.
License: GPLv3 http://www.gnu.org/licenses/gpl-3.0.en.html
```

Banner is used to output visually useful titles from the command-line.

```
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
draw: Use a specific character (like .) to form draw lines (.......)
lead: Use a specific length (like 3) on text lines (@@@ your banner text)
cols: Use a specific length (like 14) to form draw lines (@@@@@@@@@@@@@@)
unit: Show example output for various arguments.
```

unit 1: Show example headers for all combinations of output color pairs.

Text for default banner is "{login} {datetime} {machine}".
Draw lines are composed from multiple draw characters.
Colors are from VT100 legacy support in most terminal emulators.
```
    0:black        r:red           g:green         y:yellow
    b:blue         m:magenta       c:cyan          w:white
```

Example 1: jlettvin$ ./Banner.py
```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@ jlettvin 2015-08-22T13:42:50.985580 Jonathans-MacBook-Pro.local
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

Example 2: jlettvin$ ./Banner.py --draw . --cols 30 hello world
```
..............................
... hello
... world
..............................
```

Example 2: jlettvin$ ./Banner.py --bare "Lorem ipsum dolor sit amet"
```
@@@ Lorem ipsum dolor sit amet
```
