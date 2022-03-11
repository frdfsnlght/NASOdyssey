
from luma.core.render import canvas
from . import Deck

class Device(Deck):

    def __init__(self, device):
        super().__init__()
        self.device = device
        self.size = device.size
        
    # override
    def paint(self):
        wasDirty = self._dirty
        Deck.paint(self)
        if wasDirty:
            with canvas(self.device) as draw:
                draw._image.paste(self.image, (0, 0, *self.device.size))
                    