import png
from array import array
import wx
import os

class ColorControl(wx.Control):
    """ Color control class represents a clickable square where each instance 
        represents one of 16 shades of the given color """

    def __init__(self, parent, cname, color=(0,0,0), id=wx.ID_ANY, 
            pos=wx.DefaultPosition, size=(20,20), style=wx.NO_BORDER, 
            validator=wx.DefaultValidator, name="ColorControl"):
        """ Constructor for the color control"""

        wx.Control.__init__(self, parent, id, pos, size, style, validator,name)
        self.parent = parent
        self.cname = cname
        self.color = color
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
        self.parent.ClearSelection(self.cname)
        self.parent.Select(self.cname, self.color)
        self.selected = True


class AlphaControl(ColorControl):
    """ The alpha control is a color control, but then for alpha values """
    def __init__(self, parent, cname, color=(0,0,0), id=wx.ID_ANY, 
            pos=wx.DefaultPosition, size=(20,20), style=wx.NO_BORDER, 
            validator=wx.DefaultValidator, name="AlphaControl"):
        """ Constructor for the alpha control """

        ColorControl.__init__(self, parent, cname, color, id, pos, size, style, 
                validator, name)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        """ Paint is slightly different as it incorporates the selected color 
            mixed with the desired amount of alpha """
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

        #c = (255,255,255,255) # FIXME refer to a colorDisplay
        c = self.parent.parent.colorPresetPanel.selected.color
        gc.SetBrush(wx.Brush((c[0], c[1], c[2], self.color[3])))
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


class ColorPicker(wx.Window):
    """ This is the combination of red, green, blue, alpha ColorControls"""
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
            size=(80,320), style=wx.NO_BORDER, name="ColorPicker"):
        """ Contructor for the ColorPicker """

        wx.Window.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent
        self.left = [255, 255, 255, 255]
        self.right = [0, 0, 0, 255]

        self.reds = []
        self.greens = []
        self.blues = []
        self.alphas = []

        redSizer = wx.BoxSizer(wx.VERTICAL)
        greenSizer = wx.BoxSizer(wx.VERTICAL)
        blueSizer = wx.BoxSizer(wx.VERTICAL)
        alphaSizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(0, 4):
            val = 255 - i * 85
            self.reds.append(ColorControl(self, 'red', (val, 0, 0, 255)))
            self.greens.append(ColorControl(self, 'green', (0, val, 0, 255)))
            self.blues.append(ColorControl(self, 'blue', (0, 0, val, 255)))
            redSizer.Add(self.reds[i], 1, wx.SHAPED)
            greenSizer.Add(self.greens[i], 1, wx.SHAPED)
            blueSizer.Add(self.blues[i], 1, wx.SHAPED)

        for i in range(0, 4):
            val = 255 - i * 64
            if val < 0:
                val = 0
            self.alphas.append(AlphaControl(self, 'alpha', (0, 0, 0, val)))
            alphaSizer.Add(self.alphas[i], 1, wx.SHAPED)

        self.reds[3].selected = True
        self.greens[3].selected = True
        self.blues[3].selected = True
        self.alphas[0].selected = True

        colors = wx.BoxSizer(wx.HORIZONTAL)
        colors.Add(redSizer)
        colors.Add(greenSizer)
        colors.Add(blueSizer)
        colors.Add(alphaSizer)

        self.SetSizer(colors)
        self.SetAutoLayout(1)
        colors.Fit(self)

    def ClearSelection(self, cname):
        """ Removes selection outline from all gradients of the cname color"""
        items = getattr(self, cname + 's')
        for item in items:
            setattr(item, 'selected', False)
            item.Refresh()
        #self.colorDisplay.Refresh() # FIXME updated the selected colorDisplay from Presets
        self.parent.colorPresetPanel.selected.Refresh()

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
        #c = self.colorDisplay.color; # FIXME update the selected colorDisplay from Presets
        c = self.parent.colorPresetPanel.selected.color
        if cname == 'red':
            c[0] = color[0]
        elif cname == 'green':
            c[1] = color[1]
        elif cname == 'blue':
            c[2] = color[2]
        else:
            c[3] = color[3]
    
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


class ColorDisplay(wx.Window):
    """ The color display can store a selected color (combination of selected
        red, green, blue, and alpha values). """
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=(30,30), style=wx.NO_BORDER, name="ColorDisplay",
            color=None):
        """ Constructor for the ColorDisplay """
        wx.Window.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent
        self.SetInitialSize(size)
        if color == None:
            self.color = [255,255,255,255]
        else:
            self.color = [color[0], color[1], color[2], color[3]]
        self.selected = False
        self.left = False
        self.right = False
        self.middle = False

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.Select("left"))
        self.Bind(wx.EVT_RIGHT_DOWN, self.Select("right"))
        self.Bind(wx.EVT_MIDDLE_DOWN, self.Select("middle"))

    def Select(self, btn):
        """ Set which mouse button selected this """
        return lambda e: self.OnClick(btn)

    def OnClick(self, btn):
        self.parent.ClearAttr("selected")
        self.parent.ClearAttr(btn)
        self.selected = True
        setattr(self, btn, True)
        self.parent.selected = self
        setattr(self.parent, btn, self)
        self.parent.parent.colorPicker.UpdateColor(self.color)

    def OnPaint(self, event):
        """ Draws its color """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        lightGreyBrush = gc.CreateBrush(wx.Brush((200,200,200,255)))
        darkGreyBrush = gc.CreateBrush(wx.Brush((100,100,100,255)))

        gc.SetBrush(darkGreyBrush)
        gc.DrawRectangle(0, 0, 30, 30)
        gc.SetBrush(lightGreyBrush)
        gc.DrawRectangle(0, 0, 10, 10)
        gc.DrawRectangle(20, 0, 10, 10)
        gc.DrawRectangle(10, 10, 10, 10)
        gc.DrawRectangle(30, 10, 10, 10)
        gc.DrawRectangle(0, 20, 10, 10)
        gc.DrawRectangle(20, 20, 10, 10)

        gc.SetBrush(gc.CreateBrush(wx.Brush(self.color)))
        gc.DrawRectangle(0, 0, 30, 30)

        if self.selected or self.left or self.right or self.middle:
            sel = 0
            c = self.color
            if (c[0] + c[1] + c[2]) / 3 < 128:
                sel = 255
            selectPen =  gc.CreatePen(wx.Pen((sel, sel, sel, 255)))
            selectBrush = gc.CreateBrush(wx.Brush((sel,sel,sel,255)))
            noneBrush = gc.CreateBrush(wx.Brush((0,0,0,0)))
            lightGreyBrush = gc.CreateBrush(wx.Brush((200,200,200,255)))
            darkGreyBrush = gc.CreateBrush(wx.Brush((100,100,100,255)))

        if self.selected:
            gc.SetBrush(noneBrush)
            gc.SetPen(selectPen)
            gc.DrawRectangle(0,0,30,30)

        if self.left:
            gc.SetBrush(selectBrush)
            gc.SetPen(selectPen)
            gc.DrawEllipse(5,5,8,8)
            
        if self.right:
            gc.SetBrush(selectBrush)
            gc.SetPen(selectPen)
            gc.DrawRectangle(15,5,8,8)
            
        if self.middle:
            gc.SetBrush(selectBrush)
            gc.SetPen(selectPen)
            gc.DrawLines([[10,23], [15,15], [20,23]])
            


class ColorPresetPanel(wx.Panel):
    """ This class contains 10 color Displays """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=wx.DefaultSize, style=wx.NO_BORDER, name="ColorPresetPanel"):
        """ Contructor for the ColorPresetPanel """
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent

        presets = []
        # Black, white, transparent
        presets.append(ColorDisplay(self, color=(0,0,0,255)))
        presets.append(ColorDisplay(self, color=(255,255,255,255)))
        presets.append(ColorDisplay(self, color=(0,0,0,0)))

        presets.append(ColorDisplay(self, color=(255,0,0,255)))
        presets.append(ColorDisplay(self, color=(0,255,0,255)))
        presets.append(ColorDisplay(self, color=(0,0,255,255)))
        presets.append(ColorDisplay(self, color=(0,255,255,255)))
        presets.append(ColorDisplay(self, color=(255,0,255,255)))
        presets.append(ColorDisplay(self, color=(255,255,0,255)))
        presets.append(ColorDisplay(self, color=(128,128,128,255)))
        self.presets = presets

        presetsSizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(0,10):
            presetsSizer.Add(self.presets[i], 1, wx.ALIGN_LEFT, 0)

        self.selected = presets[0]
        presets[0].selected = True
        self.left = presets[0]
        presets[0].left = True
        self.right = presets[1]
        presets[1].right = True
        self.middle = presets[2]
        presets[2].middle = True

        self.SetSizer(presetsSizer)
        self.SetAutoLayout(1)
        presetsSizer.Fit(self)

    def ClearAttr(self, attr):
        for p in self.presets:
            setattr(p, attr, False)
            p.Refresh()

class PixelMod:
    def __init__(self, x, y, oldColor, newColor):
        self.x = x
        self.y = y
        self.oldColor = oldColor
        self.newColor = newColor

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.oldColor) \
            + " " + str(self.newColor) 

class DrawCommand:
    def __init__(self, target):
        self.pixelMods = {}
        self.target = target

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

        self.parent = parent
        self.imageSize = imageSize
        self.image = wx.Bitmap.ConvertToImage(wx.Bitmap.FromRGBA(
            imageSize[0], imageSize[1], 255,255,255,255))
        self.color = color
        self.scale = sc = 1
        self.prev = None
        parent.SetVirtualSize((imageSize[0] * sc, imageSize[1] * sc))
        parent.SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.Click("left"))
        self.Bind(wx.EVT_RIGHT_DOWN, self.Click("right"))
        self.Bind(wx.EVT_MIDDLE_DOWN, self.Click("middle"))
        self.Bind(wx.EVT_MOTION, self.OnMotion)


    def _resize(self):
        """ Helper function used when when zooming or loading a new image """
        imageSize = self.imageSize
        wsize = (imageSize[0] * self.scale, imageSize[1] * self.scale)
        self.SetSize(wsize)
        self.SetMinSize(wsize)
        self.SetMaxSize(wsize)
        self.parent.SetVirtualSize(wsize)
        self.parent.SetScrollRate(1, 1)
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
        dc.DrawBitmap(wx.Bitmap(self.image.Scale(iw * sc, ih * sc )), 0, 0)

    def SetPixel(self, x, y, color):
        sc = self.scale
        x = x // sc
        y = y // sc
        r = self.image.GetRed(x,y)
        g = self.image.GetGreen(x,y)
        b = self.image.GetBlue(x,y)
        a = self.image.GetAlpha(x,y)
        self.command.AddPixelMod(PixelMod(x, y, (r,g,b,a), color))
        self.parent.parent.AddCommand(self.command)
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

        for x in range(x0, x1 + 1):
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

        for y in range(y0, y1 + 1):
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
        x = event.GetX()
        y = event.GetY()
        color = getattr(self.parent.parent.colorPresetPanel, btn).color
        self.command = DrawCommand(self)
        self.SetPixel(x, y, color)
        getattr(self.parent.parent.colorPresetPanel, btn).OnClick(btn)
        self.prev = {"x":x, "y":y}

    def OnMotion(self, event):
        """ The onMotion handler function """
        if event.Dragging():
            if event.LeftIsDown():
                color = self.parent.parent.colorPresetPanel.left.color
                btn = "left"
            if event.RightIsDown():
                color = self.parent.parent.colorPresetPanel.right.color
                btn = "right"
            if event.MiddleIsDown():
                color = self.parent.parent.colorPresetPanel.middle.color
                btn = "middle"
            getattr(self.parent.parent.colorPresetPanel, btn).OnClick(btn)
            x = event.GetX()
            y = event.GetY()
            self.PlotLine(color, self.prev["x"], self.prev["y"], x, y)
            self.prev = {"x":x, "y":y}
            self.Refresh(False)


class DrawWindow(wx.ScrolledWindow):
    """ The DrawControl plus horizontal and vertical scrolbars when needed """
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=wx.DefaultSize, style=wx.BORDER_DEFAULT, name="DrawWindow"):
        """ The constructor for the DrawWindow """
        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent

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
        
        self.parent = parent
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
        img = wx.Bitmap.ConvertToImage(wx.Bitmap.FromRGBA(w, h, 255,255,255,255))
        self.parent.drawWindow.drawControl.SetImage(img)
        self.Destroy()



class MainWindow(wx.Frame):
    """ The main window for the Pixel Art Editor """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.filename = ''
        self.dirname = ''
        self.commands = []
        self.cIndex = 0

        # create our custom color picker control
        self.colorPicker = ColorPicker(self)
        self.colorPresetPanel = ColorPresetPanel(self)

        #self.CreateStatusBar() # A Statusbar in the bottom of the window

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

        # Create a color depth menu
        depthMenu = wx.Menu()
        depth32 = depthMenu.Append(wx.ID_ANY, "32bit RGBA", "32bit RGBA")
        depth16 = depthMenu.Append(wx.ID_ANY, "16bit RGBA", "16bit RGBA")
        depth12 = depthMenu.Append(wx.ID_ANY, "12bit RGBA", "12bit RGBA")
        depth8  = depthMenu.Append(wx.ID_ANY, "8bit RGBA", "8bit RGBA")

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
        menuBar.Append(depthMenu, "Depth")
        menuBar.Append(zoomMenu, "Zoom")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

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
        self.Bind(wx.EVT_MENU, self.LowerToBitDepth(16), depth16)
        self.Bind(wx.EVT_MENU, self.LowerToBitDepth(12), depth12)
        self.Bind(wx.EVT_MENU, self.LowerToBitDepth(8), depth8)

        # Use some sizers to see layout options
        self.drawWindow = DrawWindow(self)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.colorPicker, 0, wx.SHAPED)
        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.colorPresetPanel, 0, wx.ALIGN_LEFT)
        sz.Add(self.drawWindow, 1, wx.EXPAND)
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
        self.cIndex -= 1
        self.commands[self.cIndex].Revoke()
        if (self.cIndex == 0):
            self.menuUndo.Enable(False)
        if self.cIndex < len(self.commands):
            self.menuRedo.Enable(True)

    def OnRedo(self, e):
        self.commands[self.cIndex].Invoke()
        self.cIndex += 1
        if self.cIndex > 0:
            self.menuUndo.Enable(True)
        if self.cIndex >= len(self.commands):
            self.menuRedo.Enable(False)

    def AddCommand(self, command):
        if len(self.commands) <= self.cIndex:
            self.commands.append(command)
            self.cIndex += 1
        else:
            self.commands[self.cIndex] = command
            self.cIndex += 1
        if (self.cIndex > 0):
            self.menuUndo.Enable(True)

    def OnSize(self, event):
        (w,h) = self.GetClientSize()
        self.drawWindow.SetSize((w - 80, h - 40)) #FIXME magic numbers (from other controls)

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
