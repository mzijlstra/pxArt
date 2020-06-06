"""These are all the color selection and display related widgets"""

import wx

class ActiveColor(wx.Control):
    """ ActiveColors shows what color is connected to left and right button"""

    #pylint: disable-msg=too-many-arguments
    def __init__(self, parent, window, wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(80, 41), style=wx.NO_BORDER, validator=wx.DefaultValidator,
                 name="ActiveColor"):
        wx.Control.__init__(self, parent, wxid, pos, size,
                            style, validator, name)
        self.window = window
        self.foreground = [0, 0, 0, 255]
        self.background = [255, 255, 255, 255]
        self.Bind(wx.EVT_PAINT, self.on_paint)
        window.active_color = self

    #pylint: disable=unused-argument
    def on_paint(self, event):
        "The actions to take to repaint this area of the screen"
        paint_dc = wx.PaintDC(self)
        graphics = wx.GraphicsContext.Create(paint_dc)

        pen = graphics.CreatePen(wx.Pen(wx.Colour(0, 0, 0, 255)))
        fore = graphics.CreateBrush(wx.Brush(self.foreground))
        back = graphics.CreateBrush(wx.Brush(self.background))
        light_grey_brush = graphics.CreateBrush(wx.Brush((200, 200, 200, 255)))
        dark_grey_brush = graphics.CreateBrush(wx.Brush((100, 100, 100, 255)))

        graphics.SetBrush(dark_grey_brush)
        graphics.DrawRectangle(30, 10, 40, 30)
        graphics.DrawRectangle(10, 00, 40, 30)
        graphics.SetBrush(light_grey_brush)
        graphics.DrawRectangle(10, 00, 10, 10)
        graphics.DrawRectangle(30, 00, 10, 10)
        graphics.DrawRectangle(20, 10, 10, 10)
        graphics.DrawRectangle(40, 10, 10, 10)
        graphics.DrawRectangle(60, 10, 10, 10)
        graphics.DrawRectangle(10, 20, 10, 10)
        graphics.DrawRectangle(30, 20, 10, 10)
        graphics.DrawRectangle(50, 20, 10, 10)
        graphics.DrawRectangle(40, 30, 10, 10)
        graphics.DrawRectangle(60, 30, 10, 10)

        graphics.SetPen(pen)
        graphics.SetBrush(back)
        graphics.DrawRectangle(30, 10, 40, 30)
        graphics.SetBrush(fore)
        graphics.DrawRectangle(10, 00, 40, 30)

    def check_transparant(self, ground):
        """There is one color that we'll make fully transparant, that's
        full black (zero red, zero green, zero blue), 75% alpha"""
        ground = getattr(self, ground)
        if ground[0] + ground[1] + ground[2] == 0 and ground[3] <= 63:
            ground[3] = 0
        else:
            ground[3] = ground[3] | 63

    def set_color(self, ground, color):
        """sets the currently active foreground or background color
        more specifically the color the right and left mouse btn make"""
        clr = getattr(self, ground)
        clr[0] = color[0]
        clr[1] = color[1]
        clr[2] = color[2]
        clr[3] = color[3]
        self.check_transparant(ground)


class ActiveColorPane(wx.CollapsiblePane):
    """Allows the active color control to be collapsed"""

    #pylint: disable-msg=too-many-arguments
    def __init__(self, parent, wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name="ActiveColorPane"):
        wx.CollapsiblePane.__init__(self, parent, wxid, "FG / BG", pos, size,
                                    style, validator, name)

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_change)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(ActiveColor(self.GetPane(), parent))
        pane = self.GetPane()
        pane.SetSizer(sizer)
        sizer.SetSizeHints(pane)
        # don't start collapsed
        self.Expand()

    #pylint: disable=unused-argument
    def on_change(self, event):
        "The code to execute when collapsing or uncollapsing"
        self.GetParent().Layout()


class ColorControl(wx.Control):
    """ Color control class represents a clickable square where each instance
        represents one of 8 shades of the given color """

    #pylint: disable-msg=too-many-arguments
    def __init__(self, parent, owner, cname, color=(0, 0, 0), ground="foreground",
                 wxid=wx.ID_ANY, pos=wx.DefaultPosition, size=(20, 20),
                 style=wx.NO_BORDER, validator=wx.DefaultValidator,
                 name="ColorControl"):
        wx.Control.__init__(self, parent, wxid, pos, size,
                            style, validator, name)
        self.cname = cname
        self.owner = owner
        self.color = color
        self.ground = ground
        self.selected = False
        self.SetInitialSize(size)
        self.InheritAttributes()
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)

    #pylint: disable=unused-argument
    def on_paint(self, event):
        """ make the item look the way it should """
        paint_dc = wx.PaintDC(self)
        grahics = wx.GraphicsContext.Create(paint_dc)

        none_pen = grahics.CreatePen(wx.Pen(wx.Colour(0, 0, 0, 0)))
        none_brush = grahics.CreateBrush(wx.Brush((0, 0, 0, 0)))
        brush = grahics.CreateBrush(wx.Brush(self.color))
        # create an outline color that will contrast enough to see
        select_pen = grahics.CreatePen(wx.Pen(wx.Colour(255, 255, 255, 255)))

        grahics.SetPen(none_pen)
        grahics.SetBrush(brush)
        grahics.DrawRectangle(0, 0, 20, 20)

        if self.selected:
            grahics.SetBrush(none_brush)
            grahics.SetPen(select_pen)
            grahics.DrawRectangle(0, 0, 19, 19)

    #pylint: disable=unused-argument
    def on_left_click(self, event):
        """ Remove selection from all other ColorControls of this color and
            make this one selected """
        self.owner.clear_selection(self.cname)
        self.owner.select(self.cname, self.color)
        self.selected = True


class AlphaControl(ColorControl):
    """ The alpha control is a color control, but then for alpha values """
    #pylint: disable-msg=too-many-arguments
    def __init__(self, parent, owner, cname, color=(0, 0, 0),
                 ground="foreground", wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(20, 20), style=wx.NO_BORDER, validator=wx.DefaultValidator,
                 name="AlphaControl"):
        ColorControl.__init__(self, parent, owner, cname, color, ground, wxid,
                              pos, size, style, validator, name)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.window = owner.window

    #pylint: disable=unused-argument
    def on_paint(self, event):
        """ Paint is slightly different as it incorporates the selected color
            mixed with the desired amount of alpha """
        paint_dc = wx.PaintDC(self)
        graphics = wx.GraphicsContext.Create(paint_dc)
        none_pen = graphics.CreatePen(wx.Pen(wx.Colour(0, 0, 0, 0)))
        light_grey_brush = graphics.CreateBrush(wx.Brush((200, 200, 200, 255)))
        dark_grey_brush = graphics.CreateBrush(wx.Brush((100, 100, 100, 255)))

        graphics.SetPen(none_pen)
        graphics.SetBrush(dark_grey_brush)
        graphics.DrawRectangle(0, 0, 20, 20)
        graphics.SetBrush(light_grey_brush)
        graphics.DrawRectangle(0, 0, 10, 10)
        graphics.DrawRectangle(10, 10, 10, 10)

        clr = getattr(self.window.active_color, self.ground)
        color = (clr[0], clr[1], clr[2], (self.color[3] | 63))
        if clr[0] + clr[1] + clr[2] == 0 and self.color[3] == 63:
            color = (0, 0, 0, 0)
        graphics.SetBrush(wx.Brush(color))
        graphics.DrawRectangle(0, 0, 20, 20)

        if self.selected:
            sel = 0
            if (clr[0] + clr[1] + clr[2]) / 3 < 128:
                sel = 255
            select_pen = graphics.CreatePen(wx.Pen((sel, sel, sel, 255)))
            none_brush = graphics.CreateBrush(wx.Brush((0, 0, 0, 0)))
            graphics.SetBrush(none_brush)
            graphics.SetPen(select_pen)
            graphics.DrawRectangle(0, 0, 19, 19)


class ColorChooser(wx.CollapsiblePane):
    """ This is the combination of red, green, blue, alpha ColorControls"""

    #pylint: disable-msg=too-many-arguments
    #pylint: disable-msg=too-many-locals
    def __init__(self, parent, ground="foreground", wxid=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name="ColorPicker",
                 label="Foreground", color=(0, 0, 0, 255)):
        wx.CollapsiblePane.__init__(self, parent, wxid, label, pos, size, style,
                                    validator, name)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_change)
        self.window = parent
        self.ground = ground
        if ground == "foreground":
            self.window.fg_picker = self
        else:
            self.window.bg_picker = self

        self.reds = []
        self.greens = []
        self.blues = []
        self.alphas = []

        pane = self.GetPane()
        red_sizer = wx.BoxSizer(wx.VERTICAL)
        green_sizer = wx.BoxSizer(wx.VERTICAL)
        blue_sizer = wx.BoxSizer(wx.VERTICAL)
        alpha_sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(0, 8):
            val = (i << 5) + (i << 2) + (i >> 1)
            self.reds.append(ColorControl(
                pane, self, 'red', (val, 0, 0, 255), ground))
            self.greens.append(ColorControl(
                pane, self, 'green', (0, val, 0, 255), ground))
            self.blues.append(ColorControl(
                pane, self, 'blue', (0, 0, val, 255), ground))
            self.alphas.append(AlphaControl(
                pane, self, 'alpha', (0, 0, 0, val), ground))
            red_sizer.Add(self.reds[i], 1, wx.SHAPED)
            green_sizer.Add(self.greens[i], 1, wx.SHAPED)
            blue_sizer.Add(self.blues[i], 1, wx.SHAPED)
            alpha_sizer.Add(self.alphas[i], 1, wx.SHAPED)

        self.reds[(color[0] >> 5)].selected = True
        self.greens[(color[1] >> 5)].selected = True
        self.blues[(color[2] >> 5)].selected = True
        self.alphas[(color[3] >> 5)].selected = True

        colors = wx.BoxSizer(wx.HORIZONTAL)
        colors.Add(red_sizer)
        colors.Add(green_sizer)
        colors.Add(blue_sizer)
        colors.Add(alpha_sizer)

        pane.SetSizer(colors)
        self.Expand()

    #pylint: disable=unused-argument
    def on_change(self, event):
        "The code to execute when collapsing or uncollapsing"
        self.GetParent().Layout()

    def clear_selection(self, cname):
        """ Removes selection outline from all gradients of the cname color"""
        items = getattr(self, cname + 's')
        for item in items:
            setattr(item, 'selected', False)
            item.Refresh()
        self.window.active_color.Refresh()

        # When changing one of R,G,B the alphas column also needs updating
        if cname != 'alpha':
            for alpha in self.alphas:
                alpha.Refresh()

    def select(self, cname, color):
        """ Sets the selection outline on a gradient item
            cname: gives the name of the color (red, green, blue, alpha)
            color: gives the color value to get the intensity from in order to
            select the correct gradient for this cname
            """
        clr = getattr(self.window.active_color, self.ground)
        # this changes the value of ground inside active_color!
        if cname == 'red':
            clr[0] = color[0]
        elif cname == 'green':
            clr[1] = color[1]
        elif cname == 'blue':
            clr[2] = color[2]
        else:
            clr[3] = color[3]
        self.window.active_color.check_transparant(self.ground)

    def update_color(self, color):
        """Changes the color for either background or foreground """
        self.clear_selection("red")
        self.clear_selection("green")
        self.clear_selection("blue")
        self.clear_selection("alpha")
        self.reds[3 - (color[0] >> 6)].selected = True
        self.greens[3 - (color[1] >> 6)].selected = True
        self.blues[3 - (color[2] >> 6)].selected = True
        self.alphas[3 - (color[3] >> 6)].selected = True
        self.Refresh()
