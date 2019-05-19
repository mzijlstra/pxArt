import png
from array import array
import wx
import os

#global variable
WINDOW = None

class ActiveColor(wx.Control):
    """ ActiveColors shows what color is connected to left and right button"""
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=(80,41), style=wx.NO_BORDER, validator=wx.DefaultValidator,
            name="ActiveColor"):
        global WINDOW
        wx.Control.__init__(self, parent, id, pos, size, style, validator,name)
        
        self.foreground = [0,0,0,255]
        self.background = [255,255,255,255]

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        WINDOW.activeColor = self

    def OnLeftClick(self, event):
        pass

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        pen =  gc.CreatePen(wx.Pen(wx.Colour(0,0,0,255)))
        nonePen =  gc.CreatePen(wx.Pen(wx.Colour(0,0,0,0)))
        fore = gc.CreateBrush(wx.Brush(self.foreground))
        back = gc.CreateBrush(wx.Brush(self.background))
        lightGreyBrush = gc.CreateBrush(wx.Brush((200,200,200,255)))
        darkGreyBrush = gc.CreateBrush(wx.Brush((100,100,100,255)))

        gc.SetBrush(darkGreyBrush)
        gc.DrawRectangle(30, 10, 40, 30)
        gc.DrawRectangle(10, 00, 40, 30)
        gc.SetBrush(lightGreyBrush)
        gc.DrawRectangle(10, 00, 10, 10)
        gc.DrawRectangle(30, 00, 10, 10)
        gc.DrawRectangle(20, 10, 10, 10)
        gc.DrawRectangle(40, 10, 10, 10)
        gc.DrawRectangle(60, 10, 10, 10)
        gc.DrawRectangle(10, 20, 10, 10)
        gc.DrawRectangle(30, 20, 10, 10)
        gc.DrawRectangle(50, 20, 10, 10)
        gc.DrawRectangle(40, 30, 10, 10)
        gc.DrawRectangle(60, 30, 10, 10)

        gc.SetPen(pen)
        gc.SetBrush(back)
        gc.DrawRectangle(30,10,40,30)
        gc.SetBrush(fore)
        gc.DrawRectangle(10,00,40,30)

    def CheckTransparant(self, ground):
        g = getattr(self, ground)
        if g[0] + g[1] + g[2] == 0 and g[3] <= 63:
            g[3] = 0
        else:
            g[3] = g[3] | 63

    def SetColor(self, ground, color):
        c = getattr(self, ground)
        c[0] = color[0]
        c[1] = color[1]
        c[2] = color[2]
        c[3] = color[3]
        self.CheckTransparant(ground)

class ActiveColorPane(wx.CollapsiblePane):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=wx.DefaultSize, style=wx.NO_BORDER, 
            validator=wx.DefaultValidator, name="ActiveColorPane"):
        wx.CollapsiblePane.__init__(self, parent, id, "FG / BG",pos, size, 
                style, validator,name)

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnChange)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(ActiveColor(self.GetPane()))
        w = self.GetPane()
        w.SetSizer(sizer)
        sizer.SetSizeHints(w)
        # don't start collapsed
        self.Expand()

    def OnChange(self, event):
        self.GetParent().Layout()


class ColorControl(wx.Control):
    """ Color control class represents a clickable square where each instance 
        represents one of 16 shades of the given color """

    def __init__(self, parent, owner, cname, color=(0,0,0), ground="foreground",
            id=wx.ID_ANY, pos=wx.DefaultPosition, size=(20,20), 
            style=wx.NO_BORDER, validator=wx.DefaultValidator, 
            name="ColorControl"):
        """ Constructor for the color control"""

        wx.Control.__init__(self, parent, id, pos, size, style, validator,name)
        self.cname = cname
        self.owner = owner
        self.color = color
        self.ground = ground
        self.selected = False
        self.SetInitialSize(size)
        self.InheritAttributes()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)

    def OnPaint(self, event):
        """ make the item look the way it should """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        nonePen =  gc.CreatePen(wx.Pen(wx.Colour(0,0,0,0)))
        noneBrush = gc.CreateBrush(wx.Brush((0,0,0,0)))
        brush = gc.CreateBrush(wx.Brush(self.color))
        # create an outline color that will contrast enough to see
        selectPen = gc.CreatePen(wx.Pen(wx.Colour(255, 255, 255, 255)))

        gc.SetPen(nonePen)
        gc.SetBrush(brush)
        gc.DrawRectangle(0,0,20,20)

        if self.selected: 
            gc.SetBrush(noneBrush)
            gc.SetPen(selectPen)
            gc.DrawRectangle(0,0,19,19)

    def OnLeftClick(self, event):
        """ Remove selection from all other ColorControls of this color and 
            make this one selected """
        self.owner.ClearSelection(self.cname)
        self.owner.Select(self.cname, self.color)
        self.selected = True


class AlphaControl(ColorControl):
    """ The alpha control is a color control, but then for alpha values """
    def __init__(self, parent, owner, cname, color=(0,0,0), 
            ground="foreground", id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=(20,20), style=wx.NO_BORDER, validator=wx.DefaultValidator, 
            name="AlphaControl"):
        """ Constructor for the alpha control """

        ColorControl.__init__(self, parent, owner, cname, color, ground, id, 
                pos, size, style, validator, name)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        """ Paint is slightly different as it incorporates the selected color 
            mixed with the desired amount of alpha """
        global WINDOW
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        nonePen =  gc.CreatePen(wx.Pen(wx.Colour(0,0,0,0)))
        lightGreyBrush = gc.CreateBrush(wx.Brush((200,200,200,255)))
        darkGreyBrush = gc.CreateBrush(wx.Brush((100,100,100,255)))

        gc.SetPen(nonePen)
        gc.SetBrush(darkGreyBrush)
        gc.DrawRectangle(0,0,20,20)
        gc.SetBrush(lightGreyBrush)
        gc.DrawRectangle(0,0,10,10)
        gc.DrawRectangle(10,10,10,10)

        c = getattr(WINDOW.activeColor, self.ground)
        color = (c[0], c[1], c[2], (self.color[3] | 63))
        if c[0] + c[1] + c[2] == 0 and self.color[3] == 63:
            color = (0,0,0,0)
        gc.SetBrush(wx.Brush(color))
        gc.DrawRectangle(0,0,20,20)

        if self.selected: 
            sel = 0
            if (c[0] + c[1] + c[2]) / 3 < 128:
                sel = 255;
            selectPen =  gc.CreatePen(wx.Pen((sel, sel, sel, 255)))
            noneBrush = gc.CreateBrush(wx.Brush((0,0,0,0)))
            gc.SetBrush(noneBrush)
            gc.SetPen(selectPen)
            gc.DrawRectangle(0,0,19,19)


class ColorPicker(wx.CollapsiblePane):
    """ This is the combination of red, green, blue, alpha ColorControls"""
    def __init__(self, parent, ground="foreground", id=wx.ID_ANY, 
            pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER, 
            validator=wx.DefaultValidator, name="ColorPicker", 
            label="Foreground", color=(0,0,0,255)):
        """ Contructor for the ColorPicker """
        global WINDOW
        wx.CollapsiblePane.__init__(self, parent, id, label, pos, size, style, 
                validator, name)

        self.ground = ground
        if ground == "foreground":
            WINDOW.FGPicker = self
        else:
            WINDOW.BGPicker = self

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnChange)

        self.reds = []
        self.greens = []
        self.blues = []
        self.alphas = []

        p = self.GetPane()
        s = self
        redSizer = wx.BoxSizer(wx.VERTICAL)
        greenSizer = wx.BoxSizer(wx.VERTICAL)
        blueSizer = wx.BoxSizer(wx.VERTICAL)
        alphaSizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(0, 4):
            val = 255 - i * 85
            self.reds.append(ColorControl(p, s, 'red', (val, 0, 0, 255), ground))
            self.greens.append(ColorControl(p, s, 'green', (0, val, 0, 255), ground))
            self.blues.append(ColorControl(p, s, 'blue', (0, 0, val, 255), ground))
            self.alphas.append(AlphaControl(p, s, 'alpha', (0, 0, 0, val|63), ground))
            redSizer.Add(self.reds[i], 1, wx.SHAPED)
            greenSizer.Add(self.greens[i], 1, wx.SHAPED)
            blueSizer.Add(self.blues[i], 1, wx.SHAPED)
            alphaSizer.Add(self.alphas[i], 1, wx.SHAPED)

        self.reds[3 - (color[0] >> 6)].selected = True
        self.greens[3 - (color[1] >> 6)].selected = True
        self.blues[3 - (color[2] >> 6)].selected = True
        self.alphas[3 - (color[3] >> 6)].selected = True

        colors = wx.BoxSizer(wx.HORIZONTAL)
        colors.Add(redSizer)
        colors.Add(greenSizer)
        colors.Add(blueSizer)
        colors.Add(alphaSizer)

        p.SetSizer(colors)
        self.Expand()

    def OnChange(self, event):
        self.GetParent().Layout()

    def ClearSelection(self, cname):
        """ Removes selection outline from all gradients of the cname color"""
        global WINDOW
        items = getattr(self, cname + 's')
        for item in items:
            setattr(item, 'selected', False)
            item.Refresh()
        WINDOW.activeColor.Refresh() 

        # When changing one of R,G,B the alphas column also needs updating
        if cname != 'alpha':
            for alpha in self.alphas:
                alpha.Refresh()

    def Select(self, cname, color):
        """ Sets the selection outline on a gradient item 
            cname: gives the name of the color (red, green, blue, alpha)
            color: gives the color value to get the intensity from in order to
            select the correct gradient for this cname
            """
        global WINDOW
        c = getattr(WINDOW.activeColor, self.ground)
        # this changes the value of ground inside activeColor!
        if cname == 'red':
            c[0] = color[0]
        elif cname == 'green':
            c[1] = color[1]
        elif cname == 'blue':
            c[2] = color[2]
        else:
            c[3] = color[3]
        WINDOW.activeColor.CheckTransparant(self.ground)
    
    def UpdateColor(self, color):
        self.ClearSelection("red")
        self.ClearSelection("green")
        self.ClearSelection("blue")
        self.ClearSelection("alpha")
        self.reds[3 - (color[0] >> 6)].selected = True
        self.greens[3 - (color[1] >> 6)].selected = True
        self.blues[3 - (color[2] >> 6)].selected = True
        self.alphas[3 - (color[3] >> 6)].selected = True
        self.Refresh()


class PaletteItem(wx.Control):
    """ PaletteItem stores a specific color (combination of selected
        red, green, blue, and alpha values). """
    def __init__(self, parent, color=[0,0,0,0], id=wx.ID_ANY, 
            pos=wx.DefaultPosition, size=(10,10), style=wx.NO_BORDER, 
            validator=wx.DefaultValidator, name="PaletteItem"):

        wx.Control.__init__(self, parent, id, pos, size, style, validator,name)
        self.SetInitialSize(size)
        self.color = color

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.Select("foreground"))
        self.Bind(wx.EVT_RIGHT_DOWN, self.Select("background"))

    def Select(self, ground):
        """Get/Set foreground/background based on mouse button pressed """
        return lambda e: self.OnClick(e, ground)

    def OnClick(self, e, ground):
        global WINDOW
        if e.ShiftDown():
            c = getattr(WINDOW.activeColor, ground)
            self.color[0] = c[0]
            self.color[1] = c[1]
            self.color[2] = c[2]
            self.color[3] = c[3]
            self.Refresh()
        else:
            if ground == "foreground":
                WINDOW.FGPicker.UpdateColor(self.color)
            else:
                WINDOW.BGPicker.UpdateColor(self.color)
            WINDOW.activeColor.SetColor(ground, self.color) 

    def OnPaint(self, event):
        """ Draws its color """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        lightGreyBrush = gc.CreateBrush(wx.Brush((200,200,200,255)))
        darkGreyBrush = gc.CreateBrush(wx.Brush((100,100,100,255)))

        gc.SetBrush(darkGreyBrush)
        gc.DrawRectangle(0, 0, 10, 10)
        gc.SetBrush(lightGreyBrush)
        gc.DrawRectangle(0, 0, 5, 5)
        gc.DrawRectangle(5, 5, 5, 5)

        gc.SetBrush(gc.CreateBrush(wx.Brush(self.color)))
        gc.DrawRectangle(0, 0, 10, 10)


class ColorPalette(wx.CollapsiblePane):
    """ This class contains 256 PaletteItems """
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=wx.DefaultSize, style=wx.NO_BORDER, 
            validator=wx.DefaultValidator, name="ColorPalette"):
        """ Contructor for the ColorPalette """
        global WINDOW
        wx.CollapsiblePane.__init__(self, parent, id, "Palette", pos, size, 
                style, validator, name)
        WINDOW.palette = self
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnChange)

        p = self.GetPane()
        items = []
        for a in range(0,4):
          for g in range(0, 4):
            for b in range(0,4,2):
              for r in range(0,4):
                items.append(PaletteItem(p, [r*85,g*85,b*85,a*85|63]))
                items.append(PaletteItem(p, [r*85,g*85,(b+1)*85,a*85|63]))
        # make full black, lowest alpha fully transparant
        items[0].color[3] = 0

        rows = wx.BoxSizer(wx.VERTICAL)
        for y in range(0,32):
            cols = wx.BoxSizer(wx.HORIZONTAL)
            for x in range(0,8):
                cols.Add(items[y * 8 + x])
            rows.Add(cols)

        p.SetSizer(rows)
        self.Expand()

    def OnChange(self, event):
        self.GetParent().Layout()

    def Clear(self):
        pass #TODO implement

    def Reset(self):
        pass #TODO implement


class PixelMod:
    """ Pixel modification class used by DrawCommand class """
    def __init__(self, x, y, oldColor, newColor):
        self.x = x
        self.y = y
        self.oldColor = oldColor
        self.newColor = newColor

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.oldColor) \
            + " " + str(self.newColor) 

class DrawCommand:
    """ DrawCommand class as part of the command pattern for undo/redo """
    def __init__(self, target):
        self.pixelMods = {}
        self.target = target
        self.children = []
        self.parent = None;

    def AddPixelMod(self, mod):
        if (mod.x,mod.y) not in self.pixelMods:
            self.pixelMods[(mod.x,mod.y)] = mod

    def Invoke(self):
        for m in self.pixelMods.values():
            self.target._setPixel(m.x,m.y,m.newColor)

    def Revoke(self):
        for m in self.pixelMods.values():
            self.target._setPixel(m.x,m.y,m.oldColor)


class DrawControl(wx.Control):
    """ The DrawControl class contains the image which we are maniplulating  """

    def __init__(self, parent, imageSize=(64,64), color=(255,255,255,255), 
            id=wx.ID_ANY,  pos=wx.DefaultPosition, size=wx.DefaultSize, 
            style=wx.BORDER_DEFAULT, validator=wx.DefaultValidator,
                    name="DrawControl"):
        """ Constructor for DrawControl """
        wx.Control.__init__(self, parent, id, pos, size, style, validator,name)

        self.imageSize = imageSize
        self.image = wx.Bitmap.ConvertToImage(wx.Bitmap.FromRGBA(
            imageSize[0], imageSize[1], 0,0,0,0))
        self.color = color
        self.scale = sc = 1
        self.prev = None
        self.GetParent().SetVirtualSize((imageSize[0] * sc, imageSize[1] * sc))
        self.GetParent().SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.Click("left"))
        self.Bind(wx.EVT_RIGHT_DOWN, self.Click("right"))
        self.Bind(wx.EVT_MIDDLE_DOWN, self.Click("middle"))
        self.Bind(wx.EVT_MOTION, self.OnMotion)


    def _resize(self):
        """ Helper function used when when zooming or loading a new image """
        imageSize = self.imageSize
        sc = self.scale
        wsize = (imageSize[0] * sc + 2, imageSize[1] * sc + 2)
        self.SetSize(wsize)
        self.SetMinSize(wsize)
        self.SetMaxSize(wsize)
        self.GetParent().SetVirtualSize(wsize)
        self.GetParent().SetScrollRate(1, 1)
        self.Refresh()

    def _32to16(self, val):
        """ Helper function used by lowerToBitDepth """ 
        base = val >> 4
        return (base << 4) + base

    def _32to12(self, val):
        """ Helper function used by lowerToBitDepth """ 
        base = val >> 5
        return (base << 5) + (base << 2) + (base >> 1)

    def _32to8(self, val):
        """ Helper function used by lowerToBitDepth """
        base = val >> 6
        return (base << 6) + (base << 4) + (base << 2) + base

    def lowerToBitDepth(self, depth):
        """ Makes the image look like 16bit RGBA """
        for x in range(self.imageSize[0]):
            for y in range(self.imageSize[1]):
                r = self.image.GetRed(x, y)
                g = self.image.GetGreen(x, y)
                b = self.image.GetBlue(x, y)
                a = self.image.GetAlpha(x, y)
                method = getattr(self, "_32to"+str(depth))
                r = method(r)
                g = method(g)
                b = method(b)
                a = method(a)
                self.image.SetRGB(x, y, r, g, b)
                self.image.SetAlpha(x, y, a)
        self.Refresh(False)

    def SetImage(self, img):
        """ Start using / displaying the provided image """
        self.image = img
        size = img.GetSize()
        self.imageSize = (size.x, size.y)
        self.lowerToBitDepth(8)
        self._resize()

    def SetZoom(self, n):
        """ Zoom in or out to the provided scale """
        self.scale = n
        self._resize()
        WINDOW.statusBar.SetStatusText("1:" +str(n), 1)

    def OnPaint(self, event):
        """ The onPaint handler function """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        nonePen =  gc.CreatePen(wx.Pen(wx.Colour(0,0,0,0)))
        lightGreyBrush = gc.CreateBrush(wx.Brush((200,200,200,255)))
        darkGreyBrush = gc.CreateBrush(wx.Brush((100,100,100,255)))
        gc.SetPen(nonePen)

        (w, h) = self.GetClientSize()
        for x in range(0, w, 20):
            for y in range(0, h, 20):
                gc.SetBrush(lightGreyBrush)
                gc.DrawRectangle(x,y,10,10)
                gc.DrawRectangle(x+10,y+10,10,10)
                gc.SetBrush(darkGreyBrush)
                gc.DrawRectangle(x+10,y,10,10)
                gc.DrawRectangle(x,y+10,10,10)

        (iw, ih) = self.imageSize
        sc = self.scale
        dc = wx.PaintDC(self)
        dc.DrawBitmap(wx.Bitmap(self.image.Scale(iw * sc, ih * sc)), 0, 0)

    def SetPixel(self, x, y, color):
        global WINDOW
        sc = self.scale
        x = x // sc
        y = y // sc
        r = self.image.GetRed(x,y)
        g = self.image.GetGreen(x,y)
        b = self.image.GetBlue(x,y)
        a = self.image.GetAlpha(x,y)
        self.command.AddPixelMod(PixelMod(x, y, (r,g,b,a), color))
        WINDOW.AddCommand(self.command)
        self.command.Invoke()

    def _setPixel(self, x, y, color):
        """ Helper function to change a single pixel in the image """
        (r, g, b, a) = color
        (w, h) = self.imageSize
        if w > x >= 0 and h > y >= 0:
            self.image.SetRGB(x, y, r, g, b)
            self.image.SetAlpha(x, y, a)
        self.Refresh(False)

    # Bresenham's line drawing algorithm (as found on wikipidia)
    def PlotLine(self, color, x0, y0, x1, y1):
        sc = self.scale
        x0 = x0//sc
        y0 = y0//sc
        x1 = x1//sc
        y1 = y1//sc

        if abs(y1 - y0) < abs(x1 - x0):
            if x0 > x1:
                self._plotLineLow(color, x1, y1, x0, y0)
            else:
                self._plotLineLow(color, x0, y0, x1, y1)
        else:
            if y0 > y1:
                self._plotLineHigh(color, x1, y1, x0, y0)
            else:
                self._plotLineHigh(color, x0, y0, x1, y1)
        # redraws the entire line so far (opportunity for optimization)
        self.command.Invoke()

    def _plotLineLow(self, color, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        D = 2*dy - dx
        y = y0
        (w,h) = self.imageSize

        for x in range(x0, x1 + 1):
            if x < 0 or x >= w or y < 0 or y >= h:
                continue
            r = self.image.GetRed(x,y)
            g = self.image.GetGreen(x,y)
            b = self.image.GetBlue(x,y)
            a = self.image.GetAlpha(x,y)
            self.command.AddPixelMod(PixelMod(x, y, (r,g,b,a), color))
            if D > 0:
                y = y + yi
                D = D - 2*dx
            D = D + 2*dy

    def _plotLineHigh(self, color, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
        D = 2*dx - dy
        x = x0
        (w,h) = self.imageSize

        for y in range(y0, y1 + 1):
            if x < 0 or x >= w or y < 0 or y >= h:
                continue
            r = self.image.GetRed(x,y)
            g = self.image.GetGreen(x,y)
            b = self.image.GetBlue(x,y)
            a = self.image.GetAlpha(x,y)
            self.command.AddPixelMod(PixelMod(x, y, (r,g,b,a), color))
            if D > 0:
                x = x + xi
                D = D - 2*dy
            D = D + 2*dx


    def Click(self, btn):
        """ Creates an onclick handler """
        return lambda e: self.OnClick(e, btn)

    def OnClick(self, event, btn):
        """ Generic event handler for left, right, middle """
        global WINDOW
        x = event.GetX()
        y = event.GetY()
        ground = "foreground"
        if btn == "right":
            ground = "background"
        color = getattr(WINDOW.activeColor, ground)
        self.command = DrawCommand(self) #a new command everytime we click
        self.SetPixel(x, y, color)
        self.prev = {"x":x, "y":y}

    def OnMotion(self, event):
        """ The onMotion handler function """
        global WINDOW
        x = event.GetX()
        y = event.GetY()
        s = self.scale
        status = str(int(x/s)) + "," + str(int(y/s))
        WINDOW.statusBar.SetStatusText(status, 2)
        if event.Dragging():
            if event.LeftIsDown():
                color = WINDOW.activeColor.foreground
            if event.RightIsDown():
                color = WINDOW.activeColor.background
            self.PlotLine(color, self.prev["x"], self.prev["y"], x, y)
            self.prev = {"x":x, "y":y}
            self.Refresh(False)


class DrawWindow(wx.ScrolledWindow):
    """ The DrawControl plus horizontal and vertical scrolbars when needed """
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=wx.DefaultSize, style=wx.BORDER_DEFAULT, name="DrawWindow"):
        """ The constructor for the DrawWindow """
        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)

        self.drawControl = DrawControl(self)
        sizerh = wx.BoxSizer(wx.HORIZONTAL)
        sizerv = wx.BoxSizer(wx.VERTICAL)
        sizerh.Add(sizerv, 1, wx.ALIGN_CENTER_VERTICAL)
        sizerv.Add(self.drawControl, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        self.SetSizer(sizerh)
        self.SetAutoLayout(1)
        sizerh.Fit(self)
        self.SetMinSize((800,600))

class NewImageDialog(wx.Dialog):
    """ Dialog window for creating a new image """
    def __init__(self, parent, id=wx.ID_ANY, title="New Image", 
            pos=wx.DefaultPosition, size=(250,300), style=wx.BORDER_DEFAULT, 
            name="NewImageDialog"):
        wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)
        
        self.width = wx.TextCtrl(self)
        self.height = wx.TextCtrl(self)

        okButton = wx.Button(self, label='Ok', id=wx.ID_OK)
        closeButton = wx.Button(self, label='Close', id=wx.ID_CLOSE)
		
        okButton.Bind(wx.EVT_BUTTON, self.OnOk)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

        self.width.SetValue("64")
        wBox = wx.BoxSizer(wx.HORIZONTAL)
        wBox.Add(wx.StaticText(self, label="Width", size=(60, 40)))
        wBox.Add(self.width)

        self.height.SetValue("64")
        hBox = wx.BoxSizer(wx.HORIZONTAL)
        hBox.Add(wx.StaticText(self, label="Height", size=(60, 40)))
        hBox.Add(self.height)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(okButton)
        btnSizer.Add(closeButton)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wBox)
        sizer.Add(hBox)
        sizer.Add(btnSizer)
        sizer.Fit(self)

        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Show()

    def OnClose(self, e):
        self.Destroy()

    def OnOk(self, e):
        w = int(self.width.GetValue())
        h = int(self.height.GetValue())
        img = wx.Bitmap.ConvertToImage(wx.Bitmap.FromRGBA(w, h, 0,0,0,0))
        self.GetParent().drawWindow.drawControl.SetImage(img)
        self.Destroy()



class MainWindow(wx.Frame):
    """ The main window for the Pixel Art Editor """
    def __init__(self, parent, title):
        global WINDOW
        wx.Frame.__init__(self, parent, title=title)
        WINDOW = self
        self.activeColor = None
        self.FGPicker = None
        self.BGPicker = None
        self.palette = None

        self.filename = ''
        self.dirname = ''
        self.command = DrawCommand(self)

        # create our components
        activeColorPane = ActiveColorPane(self)
        foreground = ColorPicker(self, color=self.activeColor.foreground, 
                ground="foreground", label="Foreground")
        background = ColorPicker(self, color=self.activeColor.background, 
                ground="background", label="Background")
        colorPalette = ColorPalette(self)
        self.drawWindow = DrawWindow(self)

        # create a statusbar
        self.statusBar = self.CreateStatusBar(3)
        self.SetStatusWidths([-1, 50, 100]) 

        # Setting up the menu.
        filemenu= wx.Menu()
        menuNew = filemenu.Append(wx.ID_NEW, "&New", "Create a new image")
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuSave = filemenu.Append(wx.ID_SAVE, "&Save", "Save to file")
        menuSaveAs = filemenu.Append(wx.ID_SAVEAS, "Save As", "Save to specified file")
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About",
                " Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        editMenu = wx.Menu()
        self.menuUndo = editMenu.Append(wx.ID_UNDO, "&Undo", "Undo an operation")
        self.menuRedo = editMenu.Append(wx.ID_REDO, "&Redo", "Redo an operation")
        self.menuUndo.Enable(False)
        self.menuRedo.Enable(False)

        # Create a zoom menu
        zoomMenu = wx.Menu()
        z100 = zoomMenu.Append(wx.ID_ANY, "1:1", "Zoom 100%")
        z200 = zoomMenu.Append(wx.ID_ANY, "1:2", "Zoom 200%")
        z300 = zoomMenu.Append(wx.ID_ANY, "1:3", "Zoom 300%")
        z400 = zoomMenu.Append(wx.ID_ANY, "1:4", "Zoom 400%")
        z500 = zoomMenu.Append(wx.ID_ANY, "1:5", "Zoom 500%")
        z600 = zoomMenu.Append(wx.ID_ANY, "1:6", "Zoom 600%")
        z700 = zoomMenu.Append(wx.ID_ANY, "1:7", "Zoom 700%")
        z800 = zoomMenu.Append(wx.ID_ANY, "1:8", "Zoom 800%")
        z900 = zoomMenu.Append(wx.ID_ANY, "1:9", "Zoom 900%")
        z1000 = zoomMenu.Append(wx.ID_ANY, "1:10", "Zoom 1000%")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(zoomMenu, "Zoom")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # create keyboard shortcuts
        entries = [wx.AcceleratorEntry() for i in range(2)]
        entries[0].Set(wx.ACCEL_CTRL, ord('Z'), wx.ID_UNDO, self.menuUndo)
        entries[1].Set(wx.ACCEL_CTRL, ord('Y'), wx.ID_REDO, self.menuRedo)
        accel = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel)

        # Events.
        self.Bind(wx.EVT_MENU, self.OnNew, menuNew)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menuSaveAs)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnUndo, self.menuUndo)
        self.Bind(wx.EVT_MENU, self.OnRedo, self.menuRedo)
        self.Bind(wx.EVT_MENU, self.Zoom(1), z100)
        self.Bind(wx.EVT_MENU, self.Zoom(2), z200)
        self.Bind(wx.EVT_MENU, self.Zoom(3), z300)
        self.Bind(wx.EVT_MENU, self.Zoom(4), z400)
        self.Bind(wx.EVT_MENU, self.Zoom(5), z500)
        self.Bind(wx.EVT_MENU, self.Zoom(6), z600)
        self.Bind(wx.EVT_MENU, self.Zoom(7), z700)
        self.Bind(wx.EVT_MENU, self.Zoom(8), z800)
        self.Bind(wx.EVT_MENU, self.Zoom(9), z900)
        self.Bind(wx.EVT_MENU, self.Zoom(10), z1000)

        # Use some sizers to see layout options
        vert1 = wx.BoxSizer(wx.VERTICAL)
        vert1.Add(activeColorPane, 0, wx.ALIGN_TOP)
        vert1.Add(foreground, 0, wx.ALIGN_TOP)
        vert1.Add(background, 0, wx.ALIGN_TOP)
        vert1.Add(colorPalette, 0, wx.ALIGN_TOP)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.drawWindow, 1, wx.EXPAND)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(vert1, 0)
        self.sizer.Add(sz,1)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

        # set starting zoom level
        self.drawWindow.drawControl.SetZoom(5)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnNew(self, e):
# TODO create a custom dialog, as shown at:http://zetcode.com/wxpython/dialogs/
        dlg = NewImageDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnOpen(self, e):
        """ Open an image file and display it """
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", 
                "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            img = wx.Image(os.path.join(dirname, filename))
            if not img.HasAlpha():
                img.InitAlpha()
            self.drawWindow.drawControl.SetImage(img)
        dlg.Destroy()

    def OnAbout(self, e):
#TODO use a wx.AboutBox instead, as shown: http://zetcode.com/wxpython/dialogs/
        """ The onAbout handler, shows the about dialog """
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A Pixel Art Editor \n in wxPython", 
                "About PXA Editor", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    def _Save(self, filename):
        img = self.drawWindow.drawControl.image
        data = list()

        for y in range(img.GetHeight()):
            line = array("B")
            for x in range(img.GetWidth()):
                line.append(img.GetRed(x, y))
                line.append(img.GetGreen(x, y))
                line.append(img.GetBlue(x, y))
                line.append(img.GetAlpha(x, y))
            data.append(line)

        png.from_array(data, "RGBA").save(filename)


    def OnSave(self, e):
        if not self.filename:
            return self.OnSaveAs(e)
        self._Save(self.filename)

    def OnSaveAs(self, e):
        """ Create and show the save dialog """
        dlg = wx.FileDialog(self, message = "Save file as ...", 
                defaultDir = self.dirname, defaultFile = "", 
                wildcard = "*.*", 
                style = wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            if not self.filename.endswith(".png"):
                self.filename += ".png"
            self._Save(self.filename)


    def OnExit(self, e):
        """ The onExit handler """
        self.Close(True)  # Close the frame.

    def OnUndo(self, e):
        if self.command.target != self:
            self.command.Revoke()
            self.command = self.command.parent
            if self.command.target == self:
                self.menuUndo.Enable(False)
        self.menuRedo.Enable(True)

    def OnRedo(self, e):
        if len(self.command.children) >= 1:
            child = self.command.children[-1]
            child.Invoke()
            self.command = child
            if len(child.children) == 0:
                self.menuRedo.Enable(False)
        self.menuUndo.Enable(True)

    def AddCommand(self, command):
        command.parent = self.command
        self.command.children.append(command);
        self.command = command
        self.menuUndo.Enable(True)
        self.menuRedo.Enable(False)

    def OnSize(self, event):
        (w,h) = self.GetClientSize()
        self.drawWindow.SetSize((w - 80, h)) #FIXME magic number (size of other controls)

    def Zoom(self, n):
        """ Set the zoom to the amount clicked on """
        return lambda e: self.drawWindow.drawControl.SetZoom(n)

    def LowerToBitDepth(self, n):
        """ returns menu item handler to call lowerToBitDepth of given value"""
        return lambda e: self.drawWindow.drawControl.lowerToBitDepth(n)


def main():
    """ The main function, that starts the program """
    app = wx.App(False)
    frame = MainWindow(None, "Pixel Art")
    app.MainLoop()

if __name__ == "__main__":
    main()
