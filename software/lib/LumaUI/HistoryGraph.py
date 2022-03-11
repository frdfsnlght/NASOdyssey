
from . import Widget

class HistoryGraph(Widget):

    def __init__(self, model, attr, minValue = 0, maxValue = 1, direction = 'rtl', colorCurve = None, color = 'white'):
        super().__init__()
        self.model = model
        self.attr = attr
        self.minValue = minValue
        self.maxValue = maxValue
        self.direction = direction
        self.colorCurve = colorCurve
        self.color = color

        self.listenToModel(model, attr)
        
        self.label = None
        self.labelFont = None
        self.labelOffset = (3, 1)
        self.labelColor = '#808080'
        
    def paintContent(self, draw):
        historySize = self.model.getValueSize(self.attr)

        w, h = self.size
        gw, gh = w, h
        if self.borderColor:
            gw -= 2
            gh -= 2

        self.paintBackground()
        
        for i in range(0, gw):
            value = self.model.getValue(self.attr, int(i * historySize / gw))
            if value is None or value < self.minValue: continue
            if self.colorCurve:
                color = self.colorCurve.getColor(value)
            else:
                color = self.color
            if self.direction == 'rtl':
                x = gw - i - 1
            else:
                x = i
            if value >= self.maxValue:
                y1 = 0
            else:
                y1 = gh - int(gh * (value - self.minValue) / (self.maxValue - self.minValue)) - 1
            y2 = h - 1
            if self.borderColor:
                x += 1
                y1 += 1
                y2 -= 1
            draw.line((x, y1, x, y2), fill = color)
            
        self.paintBorder()
        
        if self.label and self.labelFont:
            draw.text(self.labelOffset, self.label, font = self.labelFont, fill = self.labelColor)

