"""These are the different tools used to manipulate an image,
currently including a Pencil and Bucketfill"""

import wx
import command


class Pencil(wx.Control):
    "The Pencil Tool for used for drawing"

    # pylint: disable-msg=too-many-arguments
    def __init__(self, parent, window, wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(40, 40), style=wx.NO_BORDER, validator=wx.DefaultValidator,
                 name="Pencil"):
        wx.Control.__init__(self, parent, wxid, pos, size,
                            style, validator, name)
        # wx.StaticText(self, label="Pen", pos=(0, 0))
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)
        self.window = window
        self.icon = wx.Bitmap(wx.Image("icons/pencil2.png"))
        self.prev = None
        self.command = None

    # pylint: disable=unused-argument
    def on_paint(self, event):
        "What this control should look like"
        paint_dc = wx.PaintDC(self)
        paint_dc.DrawBitmap(self.icon, 4, 4)

    # pylint: disable=unused-argument
    def on_left_click(self, event):
        "handles left clicks on the tool"
        print("pen time!")
        self.window.tool = self

    def tool_down(self, image, pos, btn):
        "adds a pixel to the image and creates an undo command"
        if btn == "left":
            color = self.window.active_color.foreground
        elif btn == "right":
            color = self.window.active_color.background
        self.prev = pos
        # a new command everytime we click
        self.command = command.DrawCommand(image)
        c_r = image.GetRed(pos["x"], pos["y"])
        c_g = image.GetGreen(pos["x"], pos["y"])
        c_b = image.GetBlue(pos["x"], pos["y"])
        c_a = image.GetAlpha(pos["x"], pos["y"])
        self.command.add_pixel_mod(
            command.PixelMod(pos, (c_r, c_g, c_b, c_a), color))
        self.window.add_command(self.command)
        self.command.invoke()

    def tool_dragged(self, image, pos, btn):
        "draws a line when on the image, adds to the exisiting undo command"
        if btn == "left":
            color = self.window.active_color.foreground
        elif btn == "right":
            color = self.window.active_color.background
        self.plot_line(image, color, self.prev, pos)
        self.prev = pos

    def plot_line(self, image, color, pos0, pos1):
        "Bresenham's line plotting algorithm as found on wikipedia"
        if abs(pos1["y"] - pos0["y"]) < abs(pos1["x"] - pos0["x"]):
            if pos0["x"] > pos1["x"]:
                self.plot_line_low(image, color, pos1, pos0)
            else:
                self.plot_line_low(image, color, pos0, pos1)
        else:
            if pos0["y"] > pos1["y"]:
                self.plot_line_high(image, color, pos1, pos0)
            else:
                self.plot_line_high(image, color, pos0, pos1)
        # redraws the entire line so far (opportunity for optimization)
        self.command.invoke()

    def plot_line_low(self, image, color, pos0, pos1):
        "helper function for plot_line"
        delta_x = pos1["x"] - pos0["x"]
        delta_y = pos1["y"] - pos0["y"]
        y_increment = 1
        if delta_y < 0:
            y_increment = -1
            delta_y = -delta_y
        d_delta = 2*delta_y - delta_x
        y_pos = pos0["y"]
        width = image.GetWidth()
        height = image.GetHeight()

        for x_pos in range(pos0["x"], pos1["x"] + 1):
            if x_pos < 0 or x_pos >= width or y_pos < 0 or y_pos >= height:
                continue
            pos = {"x": x_pos, "y": y_pos}
            self.command.add_pixel_mod(
                command.PixelMod(pos, (image.GetRed(x_pos, y_pos),
                                       image.GetGreen(x_pos, y_pos),
                                       image.GetBlue(x_pos, y_pos),
                                       image.GetAlpha(x_pos, y_pos)), color))
            if d_delta > 0:
                y_pos = y_pos + y_increment
                d_delta = d_delta - 2*delta_x
            d_delta = d_delta + 2*delta_y

    def plot_line_high(self, image, color, pos0, pos1):
        "helper function for plot_line"
        delta_x = pos1["x"] - pos0["x"]
        delta_y = pos1["y"] - pos0["y"]
        x_increment = 1
        if delta_x < 0:
            x_increment = -1
            delta_x = -delta_x
        d_delta = 2*delta_x - delta_y
        x_pos = pos0["x"]
        width = image.GetWidth()
        height = image.GetHeight()

        for y_pos in range(pos0["y"], pos1["y"] + 1):
            if x_pos < 0 or x_pos >= width or y_pos < 0 or y_pos >= height:
                continue
            pos = {"x": x_pos, "y": y_pos}
            self.command.add_pixel_mod(
                command.PixelMod(pos, (image.GetRed(x_pos, y_pos),
                                       image.GetGreen(x_pos, y_pos),
                                       image.GetBlue(x_pos, y_pos),
                                       image.GetAlpha(x_pos, y_pos)), color))
            if d_delta > 0:
                x_pos = x_pos + x_increment
                d_delta = d_delta - 2*delta_y
            d_delta = d_delta + 2*delta_x


class BucketFill(wx.Control):
    """The bucket fill tool, allowing you to flood fill an area"""

    # pylint: disable-msg=too-many-arguments
    def __init__(self, parent, window, wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=(40, 40), style=wx.NO_BORDER, validator=wx.DefaultValidator,
                 name="BucketFill"):
        wx.Control.__init__(self, parent, wxid, pos,
                            size, style, validator, name)
        #wx.StaticText(self, label="Fill", pos=(0, 0))
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)
        self.window = window
        self.icon = wx.Bitmap(wx.Image("icons/bucket4.png"))
        self.command = None

    # pylint: disable=unused-argument
    def on_paint(self, event):
        "What this control should look like"
        paint_dc = wx.PaintDC(self)
        paint_dc.DrawBitmap(self.icon, 4, 4)

    # pylint: disable=unused-argument
    def on_left_click(self, event):
        "on left click handler onto tool icon"
        print("bucket fill time!")
        self.window.tool = self

    # pylint: disable=too-many-locals
    def tool_down(self, image, pos, btn):
        """bucket fill when image is clicked,
           breadth first search fill all pixels of the same color"""
        if btn == "left":
            color = self.window.active_color.foreground
        elif btn == "right":
            color = self.window.active_color.background
        # a new command everytime we click
        self.command = command.DrawCommand(image)
        red = image.GetRed(pos["x"], pos["y"])
        green = image.GetGreen(pos["x"], pos["y"])
        blue = image.GetBlue(pos["x"], pos["y"])
        alpha = image.GetAlpha(pos["x"], pos["y"])
        self.window.add_command(self.command)
        # breath first search replacing all surrounding pixels with the same color
        width = image.GetWidth()
        height = image.GetHeight()
        from collections import deque
        queue = deque([(pos["x"], pos["y"])])
        done = {}
        while queue:
            lookat = queue.popleft()
            (x_pos, y_pos) = lookat
            pos = {"x": x_pos, "y": y_pos}
            self.command.add_pixel_mod(
                command.PixelMod(pos, (red, green, blue, alpha), color))
            done[lookat] = True
            # check pixel above
            if ((x_pos, y_pos - 1) not in done
                    and width > x_pos >= 0
                    and height > y_pos - 1 >= 0
                    and red == image.GetRed(x_pos, y_pos - 1)
                    and green == image.GetGreen(x_pos, y_pos - 1)
                    and blue == image.GetBlue(x_pos, y_pos - 1)
                    and alpha == image.GetAlpha(x_pos, y_pos - 1)):
                queue.append((x_pos, y_pos - 1))
                done[(x_pos, y_pos - 1)] = True
            # check pixel to the right
            if ((x_pos + 1, y_pos) not in done
                    and width > x_pos + 1 >= 0
                    and height > y_pos >= 0
                    and red == image.GetRed(x_pos + 1, y_pos)
                    and green == image.GetGreen(x_pos + 1, y_pos)
                    and blue == image.GetBlue(x_pos + 1, y_pos)
                    and alpha == image.GetAlpha(x_pos + 1, y_pos)):
                queue.append((x_pos + 1, y_pos))
                done[(x_pos + 1, y_pos)] = True
            # check pixel below
            if ((x_pos, y_pos + 1) not in done
                    and width > x_pos >= 0
                    and height > y_pos + 1 >= 0
                    and red == image.GetRed(x_pos, y_pos + 1)
                    and green == image.GetGreen(x_pos, y_pos + 1)
                    and blue == image.GetBlue(x_pos, y_pos + 1)
                    and alpha == image.GetAlpha(x_pos, y_pos + 1)):
                queue.append((x_pos, y_pos + 1))
                done[(x_pos, y_pos + 1)] = True
            # check pixel to the left
            if ((x_pos - 1, y_pos) not in done
                    and width > x_pos - 1 >= 0
                    and height > y_pos >= 0
                    and red == image.GetRed(x_pos - 1, y_pos)
                    and green == image.GetGreen(x_pos - 1, y_pos)
                    and blue == image.GetBlue(x_pos - 1, y_pos)
                    and alpha == image.GetAlpha(x_pos - 1, y_pos)):
                queue.append((x_pos - 1, y_pos))
                done[(x_pos - 1, y_pos)] = True
        self.command.invoke()

    def tool_dragged(self, image, pos, btn):
        "no functionality for dragging bucket fill"


# pylint: disable=too-few-public-methods
class ToolPane(wx.CollapsiblePane):
    "The panel that displays all the tool icons"

    # pylint: disable-msg=too-many-arguments
    def __init__(self, parent, wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name="ToolPane"):
        wx.CollapsiblePane.__init__(self, parent, wxid, "Tools", pos, size,
                                    style, validator, name)

        self.parent = parent
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_change)
        self.pencil = Pencil(self.GetPane(), parent)
        self.bucket_fill = BucketFill(self.GetPane(), parent)
        parent.tool = self.pencil

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.pencil)
        sizer.Add(self.bucket_fill)
        pane = self.GetPane()
        pane.SetSizer(sizer)
        sizer.SetSizeHints(pane)
        # don't start collapsed
        self.Expand()

    # pylint: disable=unused-argument
    def on_change(self, event):
        "Called when switching between collapsed and non-collapsed state"
        self.GetParent().Layout()
