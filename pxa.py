import wxversion
wxversion.select('3.0')
import wx
import os

class ColorControl(wx.Control):
    """ Color control class represents a clickable square where each instance 
        represents one of 16 shades of the given color """
    nonePen = False
    noneBrush = False
    blackPen = False
    whitePen = False

    def __init__(self, parent, cname, color=(0,0,0), id=wx.ID_ANY, 
            pos=wx.DefaultPosition, size=(20,20), style=wx.NO_BORDER, 
            validator=wx.DefaultValidator, name="ColorControl"):
        """ Constructor for the color control"""

        wx.Control.__init__(self, parent, id, pos, size, style, validator,name)
        self.parent = parent
        self.cname = cname
        self.color = color
        self.selected = False;
        self.selectPen = False;
        self.brush = wx.Brush(color)
        self.SetInitialSize(size)
        self.InheritAttributes()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)

    def _initPens(self, gc):
        """ Private helper function to initialize the drawing pens """
        # create an outline color that will contrast enough to see
        self.brush = gc.CreateBrush(wx.Brush(self.color))
        ColorControl.nonePen =  gc.CreatePen(wx.Pen(
            wx.Colour(0,0,0,0), 1, wx.TRANSPARENT))
        ColorControl.noneBrush = gc.CreateBrush(wx.Brush((0,0,0,0)))
        ColorControl.whitePen =  gc.CreatePen(wx.Pen(
            wx.Colour(255,255,255,255), 1, wx.SOLID))
        ColorControl.blackPen =  gc.CreatePen(wx.Pen(
            wx.Colour(0,0,0,255), 1, wx.SOLID))

    def _drawSelected(self, gc):
        if self.selected: 
            gc.SetBrush(ColorControl.noneBrush)
            gc.SetPen(ColorControl.whitePen)
            gc.DrawRectangle(0,0,19,19)
            gc.SetPen(ColorControl.blackPen)
            gc.StrokeLine(0,0,9,0)
            gc.StrokeLine(0,0,0,9)
            gc.StrokeLine(19,19,10,19)
            gc.StrokeLine(19,19,19,10)

    def OnPaint(self, event):
        """ make the item look the way it should """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if ColorControl.nonePen == False:
            self._initPens(gc)

        gc.SetPen(ColorControl.nonePen)
        gc.SetBrush(self.brush)
        gc.DrawRectangle(0,0,20,20)
        self._drawSelected(gc)

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
            validator=wx.DefaultValidator, name="ColorControl"):
        """ Constructor for the alpha control """

        ColorControl.__init__(self, parent, cname, color, id, pos, size, style, 
                validator, name)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        """ Paint is slightly different as it incorporates the selected color 
            mixed with the desired amount of alpha """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if ColorControl.nonePen == False:
            self._initPens(gc)

        gc.SetPen(ColorControl.nonePen)
        gc.SetBrush(ColorControl.noneBrush)
        gc.DrawRectangle(0,0,20,20)
        c = self.parent.colorDisplay.color
        gc.SetBrush(wx.Brush((c[0], c[1], c[2], self.color[3])))
        gc.DrawRectangle(0,0,20,20)
        self._drawSelected(gc)

class ColorDisplay(wx.Window):
    """ The color display shows a selected color (combination of selected
        red, green, blue, and alpha values). 
        
        I'm planning on having 10 colorDisplays for frequently used colors... 
        Perhaps also invoked by pressing the numeric buttons on the keyboard"""
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=(80,60), style=wx.NO_BORDER, name="ColorPicker", color=None):
        """ Constructor for the ColorDisplay """

        wx.Window.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent
        if color == None:
            self.color = [255,255,255,255]
        else:
            self.color = color;
        self.SetInitialSize(size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        """ Draw the selected color """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.color)))
        gc.DrawRectangle(5, 5, 45, 35)


class ColorPicker(wx.Window):
    """ This is the combination of 16 red, green, blue, alpha ColorControls 
        and the ColorDisplay """ 
# TODO make 10 color displays, and they should not be part of the color picker!
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=wx.DefaultSize, style=wx.NO_BORDER, name="ColorPicker"):
        """ Contructor for the ColorPicker """

        wx.Window.__init__(self, parent, id, pos, size, style, name)
        self.left = [255, 255, 255, 255]
        self.right = [0, 0, 0, 255]

        self.reds = []
        self.greens = []
        self.blues = []
        self.alphas = []
        self.colorDisplay = ColorDisplay(self)

        redSizer = wx.BoxSizer(wx.VERTICAL)
        greenSizer = wx.BoxSizer(wx.VERTICAL)
        blueSizer = wx.BoxSizer(wx.VERTICAL)
        alphaSizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(0, 16):
            self.reds.append(ColorControl(
                self, 'red', (255 - i*17, 0, 0, 255)))
            self.greens.append(ColorControl(
                self, 'green', (0, 255 - i*17, 0, 255)))
            self.blues.append(ColorControl(
                self, 'blue', (0, 0, 255 - i*17, 255)))
            self.alphas.append(AlphaControl(
                self, 'alpha', (0, 0, 0, 255 - i*17)))
            redSizer.Add(self.reds[i], 1, wx.SHAPED)
            greenSizer.Add(self.greens[i], 1, wx.SHAPED)
            blueSizer.Add(self.blues[i], 1, wx.SHAPED)
            alphaSizer.Add(self.alphas[i], 1, wx.SHAPED)

        self.reds[0].selected = True
        self.greens[0].selected = True
        self.blues[0].selected = True
        self.alphas[0].selected = True

        colors = wx.BoxSizer(wx.HORIZONTAL)
        colors.Add(redSizer)
        colors.Add(greenSizer)
        colors.Add(blueSizer)
        colors.Add(alphaSizer)

        blocks = wx.BoxSizer(wx.VERTICAL)
        blocks.Add(colors)
        blocks.Add(self.colorDisplay)

        self.SetSizer(blocks)
        self.SetAutoLayout(1)
        blocks.Fit(self)

    def ClearSelection(self, cname):
        """ Removes selection outline from all gradients of the cname color"""
        items = getattr(self, cname + 's')
        for item in items:
            setattr(item, 'selected', False)
            item.Refresh()
        self.colorDisplay.Refresh()
        if cname != 'alpha':
            for alpha in self.alphas:
                alpha.Refresh()

    def Select(self, cname, color):
        """ Sets the selection outline on a gradient item 
            cname: gives the name of the color (red, green, blue, alpha)
            color: gives the color value to get the intensity from in order to
            select the correct gradient for this cname
            """
        c = self.colorDisplay.color;
        if cname == 'red':
            c[0] = color[0]
        elif cname == 'green':
            c[1] = color[1]
        elif cname == 'blue':
            c[2] = color[2]
        else:
            c[3] = color[3]

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
        self.image = wx.ImageFromBitmap(wx.EmptyBitmapRGBA(
            imageSize[0], imageSize[1], 255,255,255,255))
        self.color = color
        self.scale = sc = 1
        parent.SetVirtualSize((imageSize[0] * sc, imageSize[1] * sc))
        parent.SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

        wsize = (imageSize[0] * self.scale, imageSize[1] * self.scale)
        self.SetSize(wsize)
        self.SetMinSize(wsize)
        self.SetMaxSize(wsize)

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

    def _convert16(self, val):
        """ Helper function used by Convert16 """ 
        base = val >> 4
        return (base << 4) + base

    def SetImage(self, img):
        """ Start using / displaying the provided image """
        self.image = img
        size = img.GetSize()
        self.imageSize = (size.x, size.y)
        self._resize()

    def SetZoom(self, n):
        """ Zoom in or out to the provided scale """
        self.scale = n
        self._resize()

    def Convert16(self):
        """ Makes the image look like 16bit RGBA """
        for x in range(self.imageSize[0]):
            for y in range(self.imageSize[1]):
                r = self.image.GetRed(x, y)
                g = self.image.GetGreen(x, y)
                b = self.image.GetBlue(x, y)
                a = self.image.GetAlpha(x, y)
                r = self._convert16(r)
                g = self._convert16(g)
                b = self._convert16(b)
                a = self._convert16(a)
                self.image.SetRGB(x, y, r, g, b)
                self.image.SetAlpha(x, y, a)
        self.Refresh(False)

    def OnPaint(self, event):
        """ The onPaint handler function """
        (iw, ih) = self.imageSize
        sc = self.scale
        dc = wx.PaintDC(self)
        dc.DrawBitmap(wx.BitmapFromImage(self.image.Scale(iw * sc, ih * sc )), 
                0, 0)

    def _setPixel(self, x, y, (r, g, b, a)):
        """ Helper function to change a single pixel in the image """
        sc = self.scale
        nx = x / sc
        ny = y / sc
        self.image.SetRGB(nx, ny, r, g, b)
        self.image.SetAlpha(nx, ny, a)
        self.Refresh(False)

    def OnLeftClick(self, event):
        """ The onLeftClick handler function """
        color = self.parent.parent.colorpk.colorDisplay.color
        self._setPixel(event.GetX(), event.GetY(), color)

    def OnMotion(self, event):
        """ The onMotion handler function """
        if event.Dragging():
            if event.LeftIsDown():
                color = self.parent.parent.colorpk.colorDisplay.color
                self._setPixel(event.GetX(), event.GetY(), color)


class DrawWindow(wx.ScrolledWindow):
    """ The DrawControl plus horizontal and vertical scrolbars when needed """
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, 
            size=(800,600), style=wx.BORDER_DEFAULT, name="DrawWindow"):
        """ The constructor for the DrawWindow """

        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent

        self.drawControl = DrawControl(self)
        self.SetMinSize(size) # do we need this?
        sizerh = wx.BoxSizer(wx.HORIZONTAL)
        sizerv = wx.BoxSizer(wx.VERTICAL)
        sizerh.Add(sizerv, 1, wx.ALIGN_CENTER_VERTICAL)
        sizerv.Add(self.drawControl, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        self.SetSizer(sizerh)
        self.SetAutoLayout(1)
        sizerh.Fit(self)


class MainWindow(wx.Frame):
    """ The main window for the Pixel Art Editor """
    def __init__(self, parent, title):
        self.filename = ''
        self.dirname = ''

        wx.Frame.__init__(self, parent, title=title)

        # create our custom color picker control
        self.colorpk = ColorPicker(self)
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About",
                " Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Create an image menu
        imageMenu = wx.Menu()
        convert = imageMenu.Append(wx.ID_ANY, "16bit RGBA", 
                "Convert to 16bit RGBA")

        # Create a zoom menu
        zoomMenu = wx.Menu()
        z100 = zoomMenu.Append(wx.ID_ANY, "100%", "Zoom 100%")
        z200 = zoomMenu.Append(wx.ID_ANY, "200%", "Zoom 200%")
        z400 = zoomMenu.Append(wx.ID_ANY, "400%", "Zoom 400%")
        z800 = zoomMenu.Append(wx.ID_ANY, "800%", "Zoom 800%")
        z1600 = zoomMenu.Append(wx.ID_ANY, "1600%", "Zoom 1600%")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(imageMenu, "Image")
        menuBar.Append(zoomMenu, "Zoom")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Events.
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.Zoom(1), z100)
        self.Bind(wx.EVT_MENU, self.Zoom(2), z200)
        self.Bind(wx.EVT_MENU, self.Zoom(4), z400)
        self.Bind(wx.EVT_MENU, self.Zoom(8), z800)
        self.Bind(wx.EVT_MENU, self.Zoom(16), z1600)
        self.Bind(wx.EVT_MENU, self.Convert16, convert)

        # Use some sizers to see layout options
        self.drawWindow = DrawWindow(self)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.colorpk, 0, wx.SHAPED)
        self.sizer.Add(self.drawWindow, 1, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

    def OnAbout(self, e):
        """ The onAbout handler, shows the about dialog """
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A Pixel Art Editor \n in wxPython", 
                "About PXA Editor", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, e):
        """ The onExit handler """
        self.Close(True)  # Close the frame.

    def OnOpen(self, e):
        """ Open an image file and display it """
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", 
                "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            img = wx.Image(os.path.join(self.dirname, self.filename))
            if not img.HasAlpha():
                img.InitAlpha()
            self.drawWindow.drawControl.SetImage(img)
        dlg.Destroy()

    def Zoom(self, n):
        """ Set the zoom to the amount clicked on """
        return lambda e: self.drawWindow.drawControl.SetZoom(n)

    def Convert16(self, e):
        """ Menu Item handler to convert the image to 16bit RGBA """
        self.drawWindow.drawControl.Convert16()


def main():
    """ The main function, that starts the program """
    app = wx.App(False)
    frame = MainWindow(None, "Pixel Art")
    app.MainLoop()

if __name__ == "__main__":
    main()
