
from . import Widget

class NetActivity(Widget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        
        self.receivingColor = '#00ff00'
        self.transmittingColor = '#00ff00'
        self.label = None
        self.labelFont = None
        self.labelOffset = (3, 1)
        self.labelColor = '#808080'

        self.listenToModel(model, 'receiving', 'transmitting')
        
    def paintContent(self, draw):
        receiving = self.model.getValue('receiving')
        transmitting = self.model.getValue('transmitting')
        
        w, h = self.size

        self.paintBackground()
        
        if receiving:
            draw.rectangle((0, 0, w-1, int(h/2)+1), fill = self.receivingColor)
        if transmitting:
            draw.rectangle((0, int(h/2)+1, w-1, h-1), fill = self.transmittingColor)

        self.paintBorder()
        
        if self.label and self.labelFont:
            draw.text(self.labelOffset, self.label, font = self.labelFont, fill = self.labelColor)

