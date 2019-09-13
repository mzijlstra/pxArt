"""The main pixel art window, containing the DrawControl and MainWindow"""
import png
from array import array
import wx
import os
import tool
import color as clr
import command


class DrawControl(wx.Control):
    """ The DrawControl class contains the image which we are maniplulating  """

    def __init__(self, parent, window, imageSize=(64, 64), color=(255, 255, 255, 255),
                 wxid=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.BORDER_DEFAULT, validator=wx.DefaultValidator,
                 name="DrawControl"):
        """ Constructor for DrawControl """
        wx.Control.__init__(self, parent, wxid, pos, size,
                            style, validator, name)

        self.window = window
        self.imageSize = imageSize
        # TODO add the ability to add, remove, show, and hide layers
        self.layers = []
        layer = wx.Bitmap.ConvertToImage(wx.Bitmap.FromRGBA(
            imageSize[0], imageSize[1], 0, 0, 0, 0))
        self.layers.append(layer)
        self.activeLayer = layer
        self.color = color
        self.scale = sc = 1
        self.prev = None
        self.GetParent().SetVirtualSize((imageSize[0] * sc, imageSize[1] * sc))
        self.GetParent().SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnClick)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.OnClick)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        # self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))

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
                r = self.activeLayer.GetRed(x, y)
                g = self.activeLayer.GetGreen(x, y)
                b = self.activeLayer.GetBlue(x, y)
                a = self.activeLayer.GetAlpha(x, y)
                method = getattr(self, "_32to"+str(depth))
                r = method(r)
                g = method(g)
                b = method(b)
                a = method(a)
                self.activeLayer.SetRGB(x, y, r, g, b)
                self.activeLayer.SetAlpha(x, y, a)
        self.Refresh(False)

    def SetImage(self, img):
        """ Start using / displaying the provided image """
        self.layers = [img]
        self.activeLayer = img
        size = img.GetSize()
        self.imageSize = (size.x, size.y)
        self.lowerToBitDepth(8)
        self._resize()

    def SetZoom(self, n):
        """ Zoom in or out to the provided scale """
        self.scale = n
        self._resize()
        self.window.statusBar.SetStatusText("1:" + str(n), 1)

    #pylint: disable=unused-argument
    def OnPaint(self, event):
        """ The onPaint handler function """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        nonePen = gc.CreatePen(wx.Pen(wx.Colour(0, 0, 0, 0)))
        lightGreyBrush = gc.CreateBrush(wx.Brush((200, 200, 200, 255)))
        darkGreyBrush = gc.CreateBrush(wx.Brush((100, 100, 100, 255)))
        gc.SetPen(nonePen)

        (w, h) = self.GetClientSize()
        for x in range(0, w, 20):
            for y in range(0, h, 20):
                gc.SetBrush(lightGreyBrush)
                gc.DrawRectangle(x, y, 10, 10)
                gc.DrawRectangle(x+10, y+10, 10, 10)
                gc.SetBrush(darkGreyBrush)
                gc.DrawRectangle(x+10, y, 10, 10)
                gc.DrawRectangle(x, y+10, 10, 10)

        (iw, ih) = self.imageSize
        sc = self.scale
        dc = wx.PaintDC(self)
        dc.DrawBitmap(
            wx.Bitmap(self.activeLayer.Scale(iw * sc, ih * sc)), 0, 0)

    def OnClick(self, event):
        """ Generic event handler for left, right, middle """
        scale = self.scale
        pos = {"x": event.GetX() // scale, "y": event.GetY() // scale}
        btn = "left"
        if event.RightIsDown():
            btn = "right"
        self.window.tool.tool_down(self.activeLayer, pos, btn)
        self.Refresh(False)

    def OnMotion(self, event):
        """ The onMotion handler function """
        scale = self.scale
        pos = {"x": event.GetX() // scale, "y": event.GetY() // scale}
        status = str(pos["x"]) + "," + str(pos["y"])
        self.window.statusBar.SetStatusText(status, 2)
        if event.Dragging():
            btn = "left"
            if event.RightIsDown():
                btn = "right"
            self.window.tool.tool_dragged(self.activeLayer, pos, btn)
            self.Refresh(False)


class DrawWindow(wx.ScrolledCanvas):
    """ The DrawControl plus horizontal and vertical scrolbars when needed """

    def __init__(self, parent, wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.BORDER_DEFAULT, name="DrawWindow"):
        wx.ScrolledCanvas.__init__(self, parent, wxid, pos, size, style, name)

        self.drawControl = DrawControl(self, parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer()
        sizer.Add(self.drawControl, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)
        self.SetMinSize((800, 600))
        self.ShowScrollbars(wx.SHOW_SB_ALWAYS, wx.SHOW_SB_ALWAYS)


class NewImageDialog(wx.Dialog):
    """ Dialog window for creating a new image """

    def __init__(self, parent, wxid=wx.ID_ANY, title="New Image",
                 pos=wx.DefaultPosition, size=(250, 300), style=wx.BORDER_DEFAULT,
                 name="NewImageDialog"):
        wx.Dialog.__init__(self, parent, wxid, title, pos, size, style, name)

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
        img = wx.Bitmap.ConvertToImage(wx.Bitmap.FromRGBA(w, h, 0, 0, 0, 0))
        self.GetParent().drawWindow.drawControl.SetImage(img)
        self.Destroy()


class MainWindow(wx.Frame):
    """ The main window for the Pixel Art Editor """

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.activeColor = None
        self.FGPicker = None
        self.BGPicker = None
        self.spectrum = None

        self.filename = ''
        self.dirname = os.environ['HOME']
        # used placeholder to indicate beginning of linkedlist
        self.command = command.DrawCommand(self)
        self.zoom = 10
        # is set by ToolPane in its constructor
        self.tool = None

        # create our components
        toolPane = tool.ToolPane(self)
        activeColorPane = clr.ActiveColorPane(self)
        foreground = clr.ColorPicker(self, color=self.activeColor.foreground,
                                     ground="foreground", label="FG")
        background = clr.ColorPicker(self, color=self.activeColor.background,
                                     ground="background", label="BG")
        colorSpectrum = clr.ColorSpectrum(self)
        self.drawWindow = DrawWindow(self)

        # create a statusbar
        self.statusBar = self.CreateStatusBar(3)
        self.SetStatusWidths([-1, 50, 100])

        # Setting up the menu.
        filemenu = wx.Menu()
        menuNew = filemenu.Append(wx.ID_NEW, "&New", "Create a new image")
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", " Open a file to edit")
        menuSave = filemenu.Append(wx.ID_SAVE, "&Save", "Save to file")
        menuSaveAs = filemenu.Append(
            wx.ID_SAVEAS, "Save As", "Save to specified file")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About",
                                    " Information about this program")
        menuExit = filemenu.Append(
            wx.ID_EXIT, "E&xit", " Terminate the program")

        editMenu = wx.Menu()
        self.menuUndo = editMenu.Append(
            wx.ID_UNDO, "&Undo", "Undo an operation")
        self.menuRedo = editMenu.Append(
            wx.ID_REDO, "&Redo", "Redo an operation")
        self.menuUndo.Enable(False)
        self.menuRedo.Enable(False)

        # Create a view menu
        viewMenu = wx.Menu()
        self.zoomIn = viewMenu.Append(wx.ID_ZOOM_IN, "Zoom &In", "Zoom In")
        self.zoomOut = viewMenu.Append(wx.ID_ZOOM_OUT, "Zoom &Out", "Zoom Out")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(filemenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(viewMenu, "&View")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # create keyboard shortcuts
        entries = [wx.AcceleratorEntry() for i in range(4)]
        entries[0].Set(wx.ACCEL_CTRL, ord('Z'), wx.ID_UNDO, self.menuUndo)
        entries[1].Set(wx.ACCEL_CTRL, ord('Y'), wx.ID_REDO, self.menuRedo)
        entries[2].Set(wx.ACCEL_CTRL, ord('='), wx.ID_ZOOM_IN, self.zoomIn)
        entries[3].Set(wx.ACCEL_CTRL, ord('-'), wx.ID_ZOOM_OUT, self.zoomOut)
        self.menuUndo.SetAccel(entries[0])
        self.menuRedo.SetAccel(entries[1])
        self.zoomIn.SetAccel(entries[2])
        self.zoomOut.SetAccel(entries[3])

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
        self.Bind(wx.EVT_MENU, self.OnZoomIn, self.zoomIn)
        self.Bind(wx.EVT_MENU, self.OnZoomOut, self.zoomOut)

        # Use some sizers to see layout options
        vert1 = wx.BoxSizer(wx.VERTICAL)
        vert1.Add(toolPane, 0, wx.ALIGN_TOP)
        vert1.Add(activeColorPane, 0, wx.ALIGN_TOP)
        vert1.Add(foreground, 0, wx.ALIGN_TOP)
        vert1.Add(background, 0, wx.ALIGN_TOP)
        vert1.Add(colorSpectrum, 0, wx.ALIGN_TOP)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.drawWindow, 1, wx.EXPAND)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(vert1, 0)
        self.sizer.Add(sz, 1)

        # Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()
        # self.Maximize(True)

        # set starting zoom level
        self.drawWindow.drawControl.SetZoom(self.zoom)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.SetIcon(wx.Icon("test.ico"))

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
        # TODO use a wx.AboutBox instead, as shown: http://zetcode.com/wxpython/dialogs/
        """ The onAbout handler, shows the about dialog """
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A Pixel Art Editor \n in wxPython",
                               "About PXA Editor", wx.OK)
        dlg.ShowModal()  # Shows it
        dlg.Destroy()  # finally destroy it when finished.

    def _Save(self, filename):
        img = self.drawWindow.drawControl.activeLayer
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
        dlg = wx.FileDialog(self, message="Save file as ...",
                            defaultDir=self.dirname, defaultFile="",
                            wildcard="*.*",
                            style=wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
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
            self.command.revoke()
            self.command = self.command.parent
            if self.command.target == self:
                self.menuUndo.Enable(False)
            self.menuRedo.Enable(True)
            self.drawWindow.Refresh()

    def OnRedo(self, e):
        if len(self.command.children) >= 1:
            child = self.command.children[-1]
            child.invoke()
            self.command = child
            if len(child.children) == 0:
                self.menuRedo.Enable(False)
            self.menuUndo.Enable(True)
            self.drawWindow.Refresh()

    def OnZoomIn(self, e):
        if self.zoom < 10:
            self.zoom += 1
            self.drawWindow.drawControl.SetZoom(self.zoom)
            if self.zoom == 10:
                self.zoomIn.Enable(False)
            self.zoomOut.Enable(True)

    def OnZoomOut(self, e):
        if self.zoom > 1:
            self.zoom -= 1
            self.drawWindow.drawControl.SetZoom(self.zoom)
            if self.zoom == 1:
                self.zoomOut.Enable(False)
            self.zoomIn.Enable(True)

    def AddCommand(self, command):
        command.parent = self.command
        self.command.children.append(command)
        self.command = command
        self.menuUndo.Enable(True)
        self.menuRedo.Enable(False)

    def OnSize(self, event):
        (w, h) = self.GetClientSize()
        # FIXME magic number (size of other controls)
        self.drawWindow.SetSize((w - 80, h))

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
