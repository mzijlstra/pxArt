"""The main pixel art window, containing the DrawControl and MainWindow classes"""
from array import array
import os
import wx
import png
import tool
import color as clr
import command


class DrawControl(wx.Control):
    """ The DrawControl class contains the image which we are maniplulating  """

    #pylint: disable-msg=too-many-arguments
    def __init__(self, parent, window, image_size=(64, 64), color=(255, 255, 255, 255),
                 wxid=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.BORDER_DEFAULT, validator=wx.DefaultValidator,
                 name="DrawControl"):
        """ Constructor for DrawControl """
        wx.Control.__init__(self, parent, wxid, pos, size,
                            style, validator, name)
        self.window = window
        self.image_size = image_size
        # TODO add the ability to add, remove, show, and hide layers
        self.layers = []
        layer = wx.Bitmap.ConvertToImage(wx.Bitmap.FromRGBA(
            image_size[0], image_size[1], 0, 0, 0, 0))
        self.layers.append(layer)
        self.active_layer = layer
        self.color = color
        self.scale = scale = 1
        self.prev = None
        self.GetParent().SetVirtualSize(
            (image_size[0] * scale, image_size[1] * scale))
        self.GetParent().SetScrollRate(1, 1)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_click)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_click)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        # self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))

    def _resize(self):
        """ Helper function used when when zooming or loading a new image """
        image_size = self.image_size
        wsize = (image_size[0] * self.scale + 2,
                 image_size[1] * self.scale + 2)
        self.SetSize(wsize)
        self.SetMinSize(wsize)
        self.SetMaxSize(wsize)
        self.GetParent().SetVirtualSize(wsize)
        self.GetParent().SetScrollRate(1, 1)
        self.Refresh()

    @classmethod
    def _32to16(cls, val):
        """ Helper function used by lower_to_bit_depth """
        base = val >> 4
        return (base << 4) + base

    @classmethod
    def _32to12(cls, val):
        """ Helper function used by lower_to_bit_depth """
        base = val >> 5
        return (base << 5) + (base << 2) + (base >> 1)

    @classmethod
    def _32to8(cls, val):
        """ Helper function used by lower_to_bit_depth """
        base = val >> 6
        return (base << 6) + (base << 4) + (base << 2) + base

    def lower_to_bit_depth(self, depth):
        """ Makes the image look like 16bit RGBA """
        for x_pos in range(self.image_size[0]):
            for y_pos in range(self.image_size[1]):
                red = self.active_layer.GetRed(x_pos, y_pos)
                green = self.active_layer.GetGreen(x_pos, y_pos)
                blue = self.active_layer.GetBlue(x_pos, y_pos)
                alpha = self.active_layer.GetAlpha(x_pos, y_pos)
                method = getattr(self, "_32to"+str(depth))
                red = method(red)
                green = method(green)
                blue = method(blue)
                alpha = method(alpha)
                self.active_layer.SetRGB(x_pos, y_pos, red, green, blue)
                self.active_layer.SetAlpha(x_pos, y_pos, alpha)
        self.Refresh(False)

    def set_image(self, img):
        """ Start using / displaying the provided image """
        self.layers = [img]
        self.active_layer = img
        size = img.GetSize()
        self.image_size = (size.x, size.y)
        self.lower_to_bit_depth(12)
        self._resize()

    def set_zoom(self, num):
        """ Zoom in or out to the provided scale """
        self.scale = num
        self._resize()
        self.window.status_bar.SetStatusText("1:" + str(num), 1)

    #pylint: disable=unused-argument
    def on_paint(self, event):
        """ The onPaint handler function """
        paint_dc = wx.PaintDC(self)
        graphics = wx.GraphicsContext.Create(paint_dc)
        none_pen = graphics.CreatePen(wx.Pen(wx.Colour(0, 0, 0, 0)))
        light_grey_brush = graphics.CreateBrush(wx.Brush((200, 200, 200, 255)))
        dark_grey_brush = graphics.CreateBrush(wx.Brush((100, 100, 100, 255)))
        graphics.SetPen(none_pen)

        (width, height) = self.GetClientSize()
        for x_pos in range(0, width, 20):
            for y_pos in range(0, height, 20):
                graphics.SetBrush(light_grey_brush)
                graphics.DrawRectangle(x_pos, y_pos, 10, 10)
                graphics.DrawRectangle(x_pos+10, y_pos+10, 10, 10)
                graphics.SetBrush(dark_grey_brush)
                graphics.DrawRectangle(x_pos+10, y_pos, 10, 10)
                graphics.DrawRectangle(x_pos, y_pos+10, 10, 10)

        (i_w, i_h) = self.image_size
        paint_dc = wx.PaintDC(self)
        paint_dc.DrawBitmap(
            wx.Bitmap(self.active_layer.Scale(i_w * self.scale, i_h * self.scale)), 0, 0)

    def on_click(self, event):
        """ Generic event handler for left, right, middle """
        scale = self.scale
        pos = {"x": event.GetX() // scale, "y": event.GetY() // scale}
        btn = "left"
        if event.RightIsDown():
            btn = "right"
        self.window.tool.tool_down(self.active_layer, pos, btn)
        self.Refresh(False)

    def on_motion(self, event):
        """ The onMotion handler function """
        scale = self.scale
        pos = {"x": event.GetX() // scale, "y": event.GetY() // scale}
        status = str(pos["x"]) + "," + str(pos["y"])
        self.window.status_bar.SetStatusText(status, 2)
        if event.Dragging():
            btn = "left"
            if event.RightIsDown():
                btn = "right"
            self.window.tool.tool_dragged(self.active_layer, pos, btn)
            self.Refresh(False)


#pylint: disable=too-few-public-methods
class DrawWindow(wx.ScrolledCanvas):
    """ The DrawControl plus horizontal and vertical scrolbars when needed """

    #pylint: disable-msg=too-many-arguments
    def __init__(self, parent, wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.BORDER_DEFAULT, name="DrawWindow"):
        wx.ScrolledCanvas.__init__(self, parent, wxid, pos, size, style, name)

        self.draw_control = DrawControl(self, parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer()
        sizer.Add(self.draw_control, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)
        self.SetMinSize((800, 600))
        self.ShowScrollbars(wx.SHOW_SB_ALWAYS, wx.SHOW_SB_ALWAYS)


#pylint: disable=too-many-ancestors
class NewImageDialog(wx.Dialog):
    """ Dialog window for creating a new image """

    #pylint: disable-msg=too-many-arguments
    def __init__(self, parent, wxid=wx.ID_ANY, title="New Image",
                 pos=wx.DefaultPosition, size=(250, 300), style=wx.BORDER_DEFAULT,
                 name="NewImageDialog"):
        wx.Dialog.__init__(self, parent, wxid, title, pos, size, style, name)

        self.width = wx.TextCtrl(self)
        self.height = wx.TextCtrl(self)

        ok_button = wx.Button(self, label='Ok', id=wx.ID_OK)
        close_button = wx.Button(self, label='Close', id=wx.ID_CLOSE)

        ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        close_button.Bind(wx.EVT_BUTTON, self.on_close)

        self.width.SetValue("64")
        w_box = wx.BoxSizer(wx.HORIZONTAL)
        w_box.Add(wx.StaticText(self, label="Width", size=(60, 40)))
        w_box.Add(self.width)

        self.height.SetValue("64")
        h_box = wx.BoxSizer(wx.HORIZONTAL)
        h_box.Add(wx.StaticText(self, label="Height", size=(60, 40)))
        h_box.Add(self.height)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(ok_button)
        btn_sizer.Add(close_button)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(w_box)
        sizer.Add(h_box)
        sizer.Add(btn_sizer)
        sizer.Fit(self)

        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Show()

    #pylint: disable=unused-argument
    def on_close(self, event):
        "What to do when asked to close the dialog"
        self.Destroy()

    #pylint: disable=unused-argument
    def on_ok(self, event):
        "What to do when they say yes to making a new image"
        width = int(self.width.GetValue())
        height = int(self.height.GetValue())
        img = wx.Bitmap.ConvertToImage(
            wx.Bitmap.FromRGBA(width, height, 0, 0, 0, 0))
        self.GetParent().draw_window.draw_control.set_image(img)
        self.Destroy()


class MainWindow(wx.Frame):
    """ The main window for the Pixel Art Editor """

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.active_color = None

        self.filename = ''
        self.dirname = os.environ['HOME'] + "/Pictures/"
        # used placeholder to indicate beginning of linkedlist
        self.command = command.DrawCommand(self)
        self.saved_at = self.command
        self.zoom = 10

        # create our components
        self.tool_pane = tool.ToolPane(self)
        active_color_pane = clr.ActiveColorPane(self)
        self.fg_picker = clr.ColorChooser(self, color=self.active_color.foreground,
                                          ground="foreground", label="FG")
        self.bg_picker = clr.ColorChooser(self, color=self.active_color.background,
                                          ground="background", label="BG")
        self.draw_window = DrawWindow(self)

        # start with the pencil tool
        self.tool_pane.pencil.on_left_click(None)

        # create a statusbar
        self.status_bar = self.CreateStatusBar(3)
        self.SetStatusWidths([-1, 50, 100])

        # Setting up the menu.
        filemenu = wx.Menu()
        menu_new = filemenu.Append(wx.ID_NEW, "&New", "Create a new image")
        menu_open = filemenu.Append(
            wx.ID_OPEN, "&Open", " Open a file to edit")
        menu_save = filemenu.Append(wx.ID_SAVE, "&Save", "Save to file")
        menu_save_as = filemenu.Append(
            wx.ID_SAVEAS, "Save As", "Save to specified file")
        menu_about = filemenu.Append(wx.ID_ABOUT, "&About",
                                     " Information about this program")
        menu_exit = filemenu.Append(
            wx.ID_EXIT, "E&xit", " Terminate the program")

        edit_menu = wx.Menu()
        self.menu_undo = edit_menu.Append(
            wx.ID_UNDO, "&Undo", "Undo an operation")
        self.menu_redo = edit_menu.Append(
            wx.ID_REDO, "&Redo", "Redo an operation")
        self.menu_undo.Enable(False)
        self.menu_redo.Enable(False)

        # Create a view menu
        view_menu = wx.Menu()
        self.zoom_in = view_menu.Append(wx.ID_ZOOM_IN, "Zoom &In", "Zoom In")
        self.zoom_out = view_menu.Append(
            wx.ID_ZOOM_OUT, "Zoom &Out", "Zoom Out")

        # Create a tool menu
        tool_menu = wx.Menu()
        pencil_id = wx.Window.NewControlId()
        bucket_id = wx.Window.NewControlId()
        picker_id = wx.Window.NewControlId()
        tool_pencil = tool_menu.Append(pencil_id, "Pencil", "Pencil Tool")
        tool_bucket = tool_menu.Append(bucket_id, "Bucket", "Bucket Tool")
        tool_picker = tool_menu.Append(picker_id, "Picker", "Color Picker Tool")

        # Creating the menubar.
        menu_bar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        menu_bar.Append(filemenu, "&File")
        menu_bar.Append(edit_menu, "&Edit")
        menu_bar.Append(view_menu, "&View")
        menu_bar.Append(tool_menu, "&Tool")
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.

        # create keyboard shortcuts
        entries = [wx.AcceleratorEntry() for i in range(7)]
        entries[0].Set(wx.ACCEL_CTRL, ord('Z'), wx.ID_UNDO, self.menu_undo)
        entries[1].Set(wx.ACCEL_CTRL, ord('Y'), wx.ID_REDO, self.menu_redo)
        entries[2].Set(wx.ACCEL_CTRL, ord('='), wx.ID_ZOOM_IN, self.zoom_in)
        entries[3].Set(wx.ACCEL_CTRL, ord('-'), wx.ID_ZOOM_OUT, self.zoom_out)
        # TODO these don't work
        entries[4].Set(wx.ACCEL_CTRL, ord('1'), pencil_id, tool_pencil) 
        entries[5].Set(wx.ACCEL_CTRL, ord('2'), bucket_id, tool_bucket)
        entries[6].Set(wx.ACCEL_CTRL, ord('3'), picker_id, tool_picker)
        self.menu_undo.SetAccel(entries[0])
        self.menu_redo.SetAccel(entries[1])
        self.zoom_in.SetAccel(entries[2])
        self.zoom_out.SetAccel(entries[3])

        accel = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel)

        # Events.
        self.Bind(wx.EVT_MENU, self.on_new, menu_new)
        self.Bind(wx.EVT_MENU, self.on_open, menu_open)
        self.Bind(wx.EVT_MENU, self.on_save, menu_save)
        self.Bind(wx.EVT_MENU, self.on_save_as, menu_save_as)
        self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)
        self.Bind(wx.EVT_MENU, self.on_about, menu_about)
        self.Bind(wx.EVT_MENU, self.on_undo, self.menu_undo)
        self.Bind(wx.EVT_MENU, self.on_redo, self.menu_redo)
        self.Bind(wx.EVT_MENU, self.on_zoom_in, self.zoom_in)
        self.Bind(wx.EVT_MENU, self.on_zoom_out, self.zoom_out)
        self.Bind(wx.EVT_MENU, self.on_tool_pencil, tool_pencil)
        self.Bind(wx.EVT_MENU, self.on_tool_bucket, tool_bucket)
        self.Bind(wx.EVT_MENU, self.on_tool_picker, tool_picker)

        # Use some sizers to see layout options
        vert1 = wx.BoxSizer(wx.VERTICAL)
        vert1.Add(self.tool_pane, 0, wx.ALIGN_TOP)
        vert1.Add(active_color_pane, 0, wx.ALIGN_TOP)
        vert1.Add(self.fg_picker, 0, wx.ALIGN_TOP)
        vert1.Add(self.bg_picker, 0, wx.ALIGN_TOP)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.draw_window, 1, wx.EXPAND)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(vert1, 0)
        self.sizer.Add(sizer, 1)

        # Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()
        # self.Maximize(True)

        # set starting zoom level
        self.draw_window.draw_control.set_zoom(self.zoom)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.SetIcon(wx.Icon("icons/icon.png"))

    #pylint: disable=unused-argument
    def on_new(self, event):
        "What to do when the user wants to open the new image dialog"
        # TODO create a custom dialog, as shown at:http://zetcode.com/wxpython/dialogs/
        dlg = NewImageDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    #pylint: disable=unused-argument
    def on_open(self, event):
        """ Open an image file and display it """
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "",
                            "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            img = wx.Image(os.path.join(dirname, filename))
            if not img.HasAlpha():
                img.InitAlpha()
            self.draw_window.draw_control.set_image(img)
        dlg.Destroy()

    #pylint: disable=unused-argument
    def on_about(self, event):
        # TODO use a wx.AboutBox instead, as shown: http://zetcode.com/wxpython/dialogs/
        """ The onAbout handler, shows the about dialog """
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A Pixel Art Editor \n in wxPython",
                               "About PXA Editor", wx.OK)
        dlg.ShowModal()  # Shows it
        dlg.Destroy()  # finally destroy it when finished.

    def _save(self, filename):
        "general save handling code"
        img = self.draw_window.draw_control.active_layer
        data = list()

        for y_pos in range(img.GetHeight()):
            line = array("B")
            for x_pos in range(img.GetWidth()):
                line.append(img.GetRed(x_pos, y_pos))
                line.append(img.GetGreen(x_pos, y_pos))
                line.append(img.GetBlue(x_pos, y_pos))
                line.append(img.GetAlpha(x_pos, y_pos))
            data.append(line)

        png.from_array(data, "RGBA").save(filename)
        self.saved_at = self.command

    #pylint: disable=unused-argument
    def on_save(self, event):
        "on save handler"
        if not self.filename:
            return self.on_save_as(event)
        self._save(self.filename)

    #pylint: disable=unused-argument
    def on_save_as(self, event):
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
            self._save(self.filename)

    #pylint: disable=unused-argument
    def on_exit(self, event):
        """ The onExit handler """
        # check for unsaved changes
        # TODO this check is not working?
        if self.saved_at != self.command:
            #show a discard changes dialog
            # TODO make dialog
            print("Are you sure")
        self.Close(True)  # Close the frame.

    #pylint: disable=unused-argument
    def on_undo(self, event):
        "on undo handler"
        if self.command.target != self:
            self.command.revoke()
            self.command = self.command.parent
            if self.command.target == self:
                self.menu_undo.Enable(False)
            self.menu_redo.Enable(True)
            self.draw_window.Refresh()

    #pylint: disable=unused-argument
    def on_redo(self, event):
        "on redo handler"
        if len(self.command.children) >= 1:
            child = self.command.children[-1]
            child.invoke()
            self.command = child
            if not child.children:
                self.menu_redo.Enable(False)
            self.menu_undo.Enable(True)
            self.draw_window.Refresh()

    #pylint: disable=unused-argument
    def on_zoom_in(self, event):
        "on zoom in handler"
        if self.zoom < 10:
            self.zoom += 1
            self.draw_window.draw_control.set_zoom(self.zoom)
            if self.zoom == 10:
                self.zoom_in.Enable(False)
            self.zoom_out.Enable(True)

    #pylint: disable=unused-argument
    def on_zoom_out(self, event):
        "on zoom out handler"
        if self.zoom > 1:
            self.zoom -= 1
            self.draw_window.draw_control.set_zoom(self.zoom)
            if self.zoom == 1:
                self.zoom_out.Enable(False)
            self.zoom_in.Enable(True)

    #pylint: disable=unused-argument
    def on_tool_pencil(self, event):
        "select pencil tool"
        self.tool_pane.pencil.on_left_click(None)
    
    #pylint: disable=unused-argument
    def on_tool_bucket(self, event):
        "select bucket tool"
        self.tool_pane.bucket.on_left_click(None)

    #pylint: disable=unused-argument
    def on_tool_picker(self, event):
        "select picker tool"
        self.tool_pane.picker.on_left_click(None)

    #pylint: disable=unused-argument
    def add_command(self, cmd):
        "add a command to the undo / redo tree"
        cmd.parent = self.command
        self.command.children.append(cmd)
        self.command = cmd
        self.menu_undo.Enable(True)
        self.menu_redo.Enable(False)

    #pylint: disable=unused-argument
    def on_size(self, event):
        "on window resize handler"
        (width, height) = self.GetClientSize()
        # magic number 80 == (size of other controls)
        self.draw_window.SetSize((width - 80, height))

    def lower_to_bit_depth(self, depth):
        """ returns menu item handler to call lower_to_bit_depth of given value"""
        return lambda e: self.draw_window.draw_control.lower_to_bit_depth(depth)


def main():
    """ The main function, that starts the program """
    app = wx.App(False)
    MainWindow(None, "Pixel Art")
    app.MainLoop()


if __name__ == "__main__":
    main()
