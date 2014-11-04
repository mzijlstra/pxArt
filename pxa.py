import wx
import os


class ColorControl(wx.Control):
        nonePen = False
        selectPen = False
        noneBrush = False

        def __init__(self, parent, cname, color=(0,0,0), id=wx.ID_ANY,  pos=wx.DefaultPosition,
                        size=(20,20), style=wx.NO_BORDER, validator=wx.DefaultValidator,
                        name="ColorControl"):
                """ Constructor for the color control"""

                wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
                self.parent = parent
                self.cname = cname
                self.color = color
                self.left = False
                self.right = False
                self.brush = wx.Brush(color)
                self.SetInitialSize(size)
                self.InheritAttributes()
                self.Bind(wx.EVT_PAINT, self.onPaint)
                self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
                self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)

        def onPaint(self, event):
                """ make the item look the way it should """
                dc = wx.PaintDC(self)
                gc = wx.GraphicsContext.Create(dc)
                if ColorControl.nonePen == False:
                        ColorControl.nonePen =  gc.CreatePen(wx.Pen(wx.Colour(0,0,0,0), 1, wx.TRANSPARENT))
                        ColorControl.selectPen =  gc.CreatePen(wx.Pen(wx.Colour(150,150,150,255), 1, wx.SOLID))
                        ColorControl.noneBrush = gc.CreateBrush(wx.Brush((0,0,0,0)))
                        self.brush = gc.CreateBrush(wx.Brush(self.color))

                gc.SetPen(ColorControl.nonePen)
                gc.SetBrush(self.brush)
                gc.DrawRectangle(0,0,20,20)

                self.drawSelection(gc)

        def drawSelection(self, gc):
                gc.SetBrush(ColorControl.noneBrush)
                gc.SetPen(ColorControl.selectPen)
                if self.left: 
                        gc.DrawRectangle(0,0,9,18)
                if self.right:
                        gc.DrawRectangle(10,0,9,18)

        def onLeftClick(self, event):
                self.parent.clearSelection('left', self.cname)
                self.parent.select('left', self.cname, self.color)
                self.left = True

        def onRightClick(self, event):
                self.parent.clearSelection('right', self.cname)
                self.parent.select('right', self.cname, self.color)
                self.right = True


class AlphaControl(ColorControl):

        def __init__(self, parent, cname, color=(0,0,0), id=wx.ID_ANY,  pos=wx.DefaultPosition,
                        size=(20,20), style=wx.NO_BORDER, validator=wx.DefaultValidator,
                        name="ColorControl"):
                """ Constructor for the color control"""

                ColorControl.__init__(self, parent, cname, color, id, pos, size, style, validator, name)
                self.Bind(wx.EVT_PAINT, self.onPaint)

        def onPaint(self, event):
                dc = wx.PaintDC(self)
                gc = wx.GraphicsContext.Create(dc)
                gc.SetPen(ColorControl.nonePen)
                gc.SetBrush(wx.Brush(self.parent.right))
                gc.DrawRectangle(0,0,20,20)
                c = self.parent.left
                gc.SetBrush(wx.Brush((c[0], c[1], c[2], self.color[3])))
                gc.DrawRectangle(0,0,20,20)

                self.drawSelection(gc)


class ColorDisplay(wx.Window):
        def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(80,60), style=wx.NO_BORDER, name="ColorPicker"):
                wx.Window.__init__(self, parent, id, pos, size, style, name)
                self.parent = parent
                self.SetInitialSize(size)
                self.Bind(wx.EVT_PAINT, self.onPaint)

        def onPaint(self, event):
                dc = wx.PaintDC(self)
                gc = wx.GraphicsContext.Create(dc)
                gc.SetBrush(gc.CreateBrush(wx.Brush(self.parent.right)))
                gc.DrawRectangle(30, 20, 45, 35)
                gc.SetBrush(gc.CreateBrush(wx.Brush(self.parent.left)))
                gc.DrawRectangle(5, 5, 45, 35)


class ColorPicker(wx.Window):
        def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER, name="ColorPicker"):
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
                        self.reds.append(ColorControl(self, 'red', (255 - i*17, 0, 0, 255)))
                        self.greens.append(ColorControl(self, 'green', (0, 255 - i*17, 0, 255)))
                        self.blues.append(ColorControl(self, 'blue', (0, 0, 255 - i*17, 255)))
                        self.alphas.append(AlphaControl(self, 'alpha', (0, 0, 0, 255 - i*17)))
                        redSizer.Add(self.reds[i], 1, wx.SHAPED)
                        greenSizer.Add(self.greens[i], 1, wx.SHAPED)
                        blueSizer.Add(self.blues[i], 1, wx.SHAPED)
                        alphaSizer.Add(self.alphas[i], 1, wx.SHAPED)

                self.reds[0].left = self.greens[0].left = self.blues[0].left = True
                self.reds[15].right = self.greens[15].right = self.blues[15].right = True
                self.alphas[15].left = self.alphas[15].right = True

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

        def clearSelection(self, lr, cname):
                items = getattr(self, cname + 's')
                for item in items:
                        setattr(item, lr, False)
                        item.Refresh()
                self.colorDisplay.Refresh()
                if cname != 'alpha':
                        for alpha in self.alphas:
                                alpha.Refresh()

        def select(self, lr, cname, color):
                c = getattr(self, lr)
                if cname == 'red':
                        c[0] = color[0]
                elif cname == 'green':
                        c[1] = color[1]
                elif cname == 'blue':
                        c[2] = color[2]
                else:
                        c[3] = color[3]

class DrawControl(wx.Control):

        def __init__(self, parent, imageSize=(64,64), color=(255,255,255,255), id=wx.ID_ANY,  pos=wx.DefaultPosition,
                        size=wx.DefaultSize, style=wx.ALWAYS_SHOW_SB, validator=wx.DefaultValidator,
                        name="DrawControl"):

                wx.Control.__init__(self, parent, id, pos, size, style, validator, name)

                self.parent = parent
                self.imageSize = imageSize
                self.image = wx.ImageFromBitmap(wx.EmptyBitmapRGBA(imageSize[0], imageSize[1], 255,255,255,255))
                self.color = color
                # todo make this dynamic
                self.scale = 16
                parent.SetVirtualSize((imageSize[0] * self.scale, imageSize[1] * self.scale))
                parent.SetScrollRate(1, 1)

                self.Bind(wx.EVT_PAINT, self.onPaint)
                self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
                self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)

                wsize = (imageSize[0] * self.scale, imageSize[1] * self.scale)
                self.SetSize(wsize)
                self.SetMinSize(wsize)
                self.SetMaxSize(wsize)

        def onPaint(self, event):
                (iw, ih) = self.imageSize
                sc = self.scale
                dc = wx.PaintDC(self)
                dc.DrawBitmap(wx.BitmapFromImage(self.image.Scale(iw * sc, ih * sc )), 0, 0)

        def onLeftClick(self, event):
                x = event.GetX()
                y = event.GetY()
                sc = self.scale
                nx = x / sc
                ny = y / sc
                (r, g, b, a) = self.parent.parent.colorpk.left
                self.image.SetRGB(nx, ny, r, g, b)
                self.image.SetAlpha(nx, ny, a)
                self.Refresh(False)

        def onRightClick(self, event):
                pass


class DrawWindow(wx.ScrolledWindow):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(800,600), 
            style=wx.ALWAYS_SHOW_SB, name="DrawWindow"):

        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent

        self.SetMinSize(size) # do we need this?
        sizerh = wx.BoxSizer(wx.HORIZONTAL)
        sizerv = wx.BoxSizer(wx.VERTICAL)
        sizerh.Add(sizerv, 1, wx.ALIGN_CENTER_VERTICAL)
        sizerv.Add(DrawControl(self), 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        self.SetSizer(sizerh)
        self.SetAutoLayout(1)
        sizerh.Fit(self)


class MainWindow(wx.Frame):
        def __init__(self, parent, title):
                self.dirname=''

                # A "-1" in the size parameter instructs wxWidgets to use the default size.
                # In this case, we select 200px width and the default height.
                wx.Frame.__init__(self, parent, title=title)
                #self.control = wx.TextCtrl(self, size=(300,200), style=wx.TE_MULTILINE)
                #self.control = DrawControl(self, size=(800, 600))
                self.drawWindow = DrawWindow(self)

                # create our custom color picker control
                self.colorpk = ColorPicker(self)
                self.CreateStatusBar() # A Statusbar in the bottom of the window

                # Setting up the menu.
                filemenu= wx.Menu()
                menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
                menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
                menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

                # Creating the menubar.
                menuBar = wx.MenuBar()
                menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
                self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

                # Events.
                self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
                self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
                self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

                # Use some sizers to see layout options
                self.sizer = wx.BoxSizer(wx.HORIZONTAL)
                self.sizer.Add(self.colorpk, 0, wx.SHAPED)
                self.sizer.Add(self.drawWindow, 1, wx.EXPAND)

                #Layout sizers
                self.SetSizer(self.sizer)
                self.SetAutoLayout(1)
                self.sizer.Fit(self)
                self.Show()

        def OnAbout(self,e):
                # Create a message dialog box
                dlg = wx.MessageDialog(self, " A sample editor \n in wxPython", "About Sample Editor", wx.OK)
                dlg.ShowModal() # Shows it
                dlg.Destroy() # finally destroy it when finished.

        def OnExit(self,e):
                self.Close(True)  # Close the frame.

        def OnOpen(self,e):
                """ Open a file"""
                dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
                if dlg.ShowModal() == wx.ID_OK:
                        self.filename = dlg.GetFilename()
                        self.dirname = dlg.GetDirectory()
                        f = open(os.path.join(self.dirname, self.filename), 'r')
                        self.control.SetValue(f.read())
                        f.close()
                dlg.Destroy()


def main():
    app = wx.App(False)
    frame = MainWindow(None, "Sample editor")
    app.MainLoop()

if __name__ == "__main__":
    main()
