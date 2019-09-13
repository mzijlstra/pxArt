"Undo / Redo Command module"

# TODO remove this class, just use a map instead!
#pylint: disable-msg=too-few-public-methods
class PixelMod:
    """ Pixel modification class used by DrawCommand class """

    def __init__(self, pos, old_color, new_color):
        self.pos = pos
        self.old_color = old_color
        self.new_color = new_color


class DrawCommand:
    """ DrawCommand class as part of the command pattern for undo/redo """

    def __init__(self, target):
        self.pixel_mods = {}
        self.target = target #for a draw command this is an image
        self.children = []
        self.parent = None

    def add_pixel_mod(self, mod):
        "Adds a PixelMod to this DrawCommand"
        if (mod.pos["x"], mod.pos["y"]) not in self.pixel_mods:
            self.pixel_mods[(mod.pos["x"], mod.pos["y"])] = mod

    def invoke(self):
        "Apply all the pixel modifications"
        for mod in self.pixel_mods.values():
            self.set_pixel(mod.pos, mod.new_color)

    def revoke(self):
        "Remove all the pixel modifications"
        for mod in self.pixel_mods.values():
            self.set_pixel(mod.pos, mod.old_color)

    def set_pixel(self, pos, color):
        """ Helper function to change a single pixel in the image """
        (red, green, blue, alpha) = color
        width = self.target.GetWidth()
        height = self.target.GetHeight()
        if width > pos["x"] >= 0 and height > pos["y"] >= 0:
            self.target.SetRGB(pos["x"], pos["y"], red, green, blue)
            self.target.SetAlpha(pos["x"], pos["y"], alpha)
