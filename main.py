import typing, enum

W, H = 400, 300

U = typing.TypeVar('U')

class Align(enum.Enum):
    START = 0
    CENTER = 1
    END = 2
    SPACE_BETWEEN = 3
    SPACE_AROUND = 4
    SPACE_EVENLY  = 5

class Flex(enum.Enum):
    COLUMN = 0
    ROW = 1

def rgb(r: int, g: int, b: int) -> int:
    return r << 16 | g << 8 | b

def rgb565(r: int, g: int = None, b: int = None) -> int:
    if g == None and b == None:
        return rgb565(r >> 16, (r >> 8) & 0xff, r & 0xff)
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);

def screenFill(screen, width, height, bgColor):
    for j in screen:
        while len(j) < width:
            j.append(bgColor)
    while len(screen) < height:
        screen.append([bgColor for _ in range(width)])

def screenAdd(screen, render, xOff, yOff, bColor = 0):
    if not len(render) or not len(render[0]): return
    y = 0
    while y < len(render):
        x = 0
        while x < len(render[0]):
            while len(screen) - 1 < y + yOff:
                screen.append([])
                for i in range(xOff + len(render[0]) if (xOff + len(render[0])) > len(screen[0]) else len(screen[0])):
                    screen[len(screen) - 1].append(bColor)
            while len(screen[y + yOff]) - 1 < x + xOff:
                screen[y+yOff].append(bColor)
            screen[y + yOff][x + xOff] = render[y][x]
            x+=1
        y+=1

def screenCopy(screen, render, xOff, yOff):
    if not len(render) or not len(render[0]): return
    y = 0
    while y < ((len(screen) - yOff) if (yOff + len(render)) > len(screen) else len(render)) :
        x = 0
        while x < ((len(screen[0]) - xOff) if (xOff + len(render[0])) > len(screen[0]) else len(render[0])):
            screen[y + yOff][x + xOff] = render[y][x]
            x+=1
        y+=1

def continued(self: list[U], elem: U, start: int = 0) -> int:
        ind = self.find(elem, start)
        if ind > -1:
            ctd = 1
            while True:
                ind += 1
                if ind < len(self) and self[ind] == elem:
                    ctd += 1
                else:
                    break
            return ctd
        else: return 0


class Div:
    def __init__(
            self, width: float = 0, height: float = 0, flex: Flex = Flex.ROW, 
            alignItem: Align | None = None, justifyContent: Align | None = None, alignSelf: Align | None = None, 
            bgColor: tuple[int, int, int, int] | int = (255, 255, 255), gap: float = 0, children: list[typing.Self] = []):
        self._width = width
        self._height = height
        self.flex = flex
        self.bgColor = rgb(*bgColor) if isinstance(bgColor, tuple) else bgColor
        self.gap = gap
        self.alignItem = alignItem
        self.justifyContent = justifyContent
        self.alignSelf: str = alignSelf
        self.children = children
        self.__ren = None
    
    def dragonRender(self, screen: list[list[tuple[int, int, int, int]]] | tuple[int, int] | None = (W, H), x: int = 0, y: int = 0) -> list[list[tuple[int, int, int, int]]]:
        ren = []
        w = 0
        h = 0

        maxH: int = (self._height if self.flex == Flex.ROW else self._width) or self.dragonHeight()

        spacing = 0
        jOff = 0
    
        for i, child in enumerate(self.children):
            rend = child.render()
            if not len(rend) or not len(rend[0]): continue

            ext = (self.gap if w else 0)
            
            if self.flex == Flex.ROW:
                if child._width and child._width + ext > self._width - w:
                    h += maxH + self.gap
                    w = 0
                    ext = 0
                    maxH = self._height or self.dragonHeight(i)
            elif self.flex == Flex.COLUMN:
                if child._height and child._height + ext > self._height - w:
                    h += maxH + self.gap
                    w = 0
                    ext = 0
                    maxH = self._width or self.dragonHeight(i)
            
            al = 0

            match child.alignSelf or self.alignItem:
                case Align.CENTER:
                    if self.flex == Flex.ROW:
                        al = (maxH - len(rend)) / 2
                    else:
                        al = (maxH - len(rend[0])) / 2
                case Align.END:
                    if self.flex == Flex.ROW:
                        al = maxH - len(rend)
                    else:
                        al = maxH - len(rend[0])

            if self.flex == Flex.ROW:
                screenAdd(ren, rend, (w + ext), int(h + al), self.bgColor)
                w += child._width + ext
            elif self.flex == Flex.COLUMN:
                screenAdd(ren, rend, int(h + al), (w + ext), self.bgColor)
                w += child._height + ext

        self.baseRender(ren, h + maxH)

        self.__ren = ren
        return ren
    
    def baseRender(self, render, dHeight):
        if self.flex == Flex.ROW:
            screenFill(render, self._width, self._height or dHeight, self.bgColor)
        else:
            screenFill(render, self._width or dHeight, self._height, self.bgColor)


    def dragonShow(self):
        for i in self.dragonRender(): print(i)

    def render(self):
        return self.__ren or self.dragonRender()

    def dragonHeight(self, index: int = 0) -> int:
        w = 0
        maxH = 0
        for c in self.children[index:]:
            ext = (self.gap if w else 0)

            if self.flex == Flex.ROW:
                if c._width and c._width + (ext) > self._width - w:
                    break
                if c.height > maxH: 
                    maxH = c.height
                w += c._width + (ext)
            elif self.flex == Flex.COLUMN:
                if c._height and c._height + (ext) > self._height - w:
                    break
                if c.width > maxH: 
                    maxH = c.width
                w += c._height + (ext)
        return maxH

    def rows(self):
        pass

    def __getitem__(self, children: tuple[typing.Self] | typing.Self) -> typing.Self:
        if isinstance(children, tuple):
            self.children = list(children)
        else:
            self.children = [children]
        return self
    
    @property
    def height(self):
        return len(self.render())
    
    @property
    def width(self):
        self.render()
        return len(self.__ren[0]) if len(self.__ren) else 0
    
    def _renderToC(self):
        render = self.dragonRender();
        content = f"static uint16_t render[{len(render)}][{len(render[0])}] = " + '{\n\t' + ",\n\t".join('{' + ','.join(str(rgb565(col)) for col in row) + '}' for row in render) + '\n};'
        header = open("img.h", 'w')
        header.write(content)
        header.close()

    def _optimizedRenderToC(self):
        render = self.dragonRender()
        content = f"static uint16_t render[{len(render)}][{len(render[0])}] = " + '{\n\t'


Div(30*8, None, bgColor = 0, alignItem = Align.CENTER, flex = Flex.ROW)[
    Div(30*8, None, bgColor = 0, gap = 1, alignItem = Align.CENTER, flex = Flex.ROW)[
        Div(14*8, 10*8, bgColor = 0xff0000), 
        Div(14*8, 10*8, bgColor = 0x00ff00), 
        Div(30*8, 10*8, bgColor = 0x00ffff),
        Div(10*8, 10*8, bgColor = 0xffffff),
        Div(18*8, 10*8, bgColor = 0xff33fe), 
        Div(16*8, 10*8, bgColor = 0xf8f7ee),
        Div(12*8, 10*8, bgColor = 0x0000ff), 
    ]
]._renderToC()

'''
Div(30, None, bgColor = 0, alignItem = Align.CENTER, flex = Flex.ROW)[
    Div(30, None, bgColor = 0, gap = 1, alignItem = Align.CENTER, flex = Flex.ROW)[

        Div(5, 5, bgColor = 5), 
        Div(5, 7, bgColor = 8), 
        Div(12, 5, bgColor = 6, gap = 1, alignItem = Align.CENTER) 
        [
            Div(3, 3, bgColor = 3),
            Div(3, 3, bgColor = 2, alignSelf = Align.CENTER)
        ], 
        Div(5, 5, bgColor = 5), 
        Div(5, 5, bgColor = 5),
        Div(5, 5, bgColor = 5),
        Div(5, 9, bgColor = 6),
        Div(5, 5, bgColor = 5),
        Div(5, 5, bgColor = 5),
        Div(5, 5, bgColor = 5),
        Div(5, 5, bgColor = 5),
        Div(5, 5, bgColor = 5),
        Div(5, 5, bgColor = 5)
    ]
]._renderToC()
'''