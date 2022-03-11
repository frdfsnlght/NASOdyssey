
from . import Widget

class Text(Widget):

    def __init__(self, text, font = None, color = 'white', halign = 'left', valign = 'top', spacing = 4):
        super().__init__()
        self.text = text
        self.font = font
        self.color = color
        self.halign = halign
        self.valign = valign
        self.spacing = spacing
        self.borderColor = None
        self.values = []
        
    def addValue(self, model, *names):
        self.values.append((model, *names))
        n = []
        for name in names:
            if isinstance(name, tuple):
                n.append(name[0])
            elif isinstance(name, str):
                n.append(name)
        if n:
            self.listenToModel(model, *n)
            
    def paintContent(self, draw):
        text = self.text
        if self.values:
            # get all the values from the models
            values = []
            for model, *names in self.values:
                for name in names:
                    if isinstance(name, tuple):
                        value = model.getValue(name[0])
                        value = name[1](value)
                    elif isinstance(name, str):
                        value = model.getValue(name)
                    values.append(value)
            text = text.format(*values)

        w, h = self.size
        
        if self.halign == 'right':
            x = w - 1
            anchor = 'r'
            if self.borderColor:
                x -= 1
        elif self.halign == 'center':
            x = int(w / 2)
            anchor = 'm'
        else:
            x = 0
            anchor = 'l'
            if self.borderColor:
                x += 1
            
        if self.valign == 'bottom':
            y = h - 1
            anchor += 'b'
            if self.borderColor:
                h -= 1
        elif self.valign == 'center':
            y = int(h / 2)
            anchor += 'm'
        else:
            y = 0
            anchor += 't'
            if self.borderColor:
                y += 1
        
        self.paintBackground()
        
        draw.text((x, y), text, fill = self.color, font = self.font, anchor = anchor, spacing = self.spacing)
        
        self.paintBorder()

