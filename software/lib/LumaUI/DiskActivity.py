
from . import Widget

class DiskActivity(Widget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        
        self.unavailableColor = (128, 128, 128)
        self.errorColor = (255, 0, 0)
        self.unhealthyColor = (255, 255, 0)
        self.readingColor = (0, 255, 0)
        self.writingColor = (0, 255, 0)
        self.borderColor = (32, 32, 32)
        self.label = None
        self.labelFont = None
        self.labelOffset = (3, 1)
        self.labelColor = (128, 128, 128)
        
        self.listenToModel(model, 'available', 'error', 'testResult', 'reading', 'writing')
        
    def paintContent(self, draw):
        available = self.model.getValue('available')
        error = self.model.getValue('error')
        testResult = self.model.getValue('testResult')
        reading = self.model.getValue('reading')
        writing = self.model.getValue('writing')
        
        w, h = self.size
        
        self.paintBackground()
        
        if available:
            if error:
                draw.rectangle((0, 0, w-1, h-1), fill = self.errorColor)
            if reading:
                color = self.readingColor
                if testResult and testResult != 'PASSED':
                    color = self.unhealthyColor
                draw.rectangle((0, 0, w-1, int(h/2)+1), fill = color)
            if writing:
                color = self.writingColor
                if testResult and testResult != 'PASSED':
                    color = self.unhealthyColor
                draw.rectangle((0, int(h/2)+1, w-1, h-1), fill = color)
        
        else:
            draw.line((1, 1, w-2, h-2), fill = self.unavailableColor)
            draw.line((w-2, 1, 1, h-2), fill = self.unavailableColor)

        self.paintBorder()
        
        if self.label and self.labelFont:
            draw.text(self.labelOffset, self.label, font = self.labelFont, fill = self.labelColor)

