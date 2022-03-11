
from . import Widget

class Gauge(Widget):

    def __init__(self, model, attr, minValue = 0, maxValue = 1, colorCurve = None, color = '#ffffff'):
        super().__init__()
        self.model = model
        self.attr = attr
        self.minValue = minValue
        self.maxValue = maxValue
        self.colorCurve = colorCurve
        self.color = color
        
        self.listenToModel(model, attr)
        
    def paintContent(self, draw):
        value = self.model.getValue(self.attr)
        if value is None: return
        if value < self.minValue:
            percent = 0
        elif value > self.maxValue:
            percent = 1
        else:
            percent = (value - self.minValue) / (self.maxValue - self.minValue)
            
        w, h = self.size
        barX, barY = int((w-1)*percent), h-1
        if self.colorCurve:
            color = self.colorCurve.getColor(percent)
        else:
            color = self.color
            
        self.paintBackground()
        
        # draw the bar
        draw.rectangle((0, 0, barX, barY), fill = color)

        self.paintBorder()

