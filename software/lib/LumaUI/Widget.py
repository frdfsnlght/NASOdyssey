
from PIL import Image, ImageDraw

class Widget():

    def __init__(self):
        self.parent = None
        self.image = None
        self._draw = None
        self._position = (0, 0)
        self._size = (0, 0)
        self._dirty = True
        self._hidden = False
        self.models = {}
        self.backgroundColor = (0, 0, 0)
        self.borderColor = (32, 32, 32)
        
    @property
    def position(self):
        return self._position
        
    @position.setter
    def position(self, value):
        self._position = value
        
    @property
    def size(self):
        return self._size
        
    @size.setter
    def size(self, value):
        self._size = value
        self.image = None
        self._draw = None
        self.dirty = True
        
    @property
    def hidden(self):
        return self._hidden
        
    @hidden.setter
    def hidden(self, value):
        self._hidden = value
        if not self._hidden:
            self.dirty = True
            
    @property
    def dirty(self):
        return self._dirty
        
    @dirty.setter
    def dirty(self, value):
        self._dirty = value
        if self._dirty and self.parent:
            self.parent.dirty = True
        
    def paint(self):
        if self._hidden: return
        if not self._draw:
            self.image = Image.new('RGB', self._size)
            self._draw = ImageDraw.Draw(self.image)
        if self._dirty:
            self.paintContent(self._draw)
            self._dirty = False
        
    def paintBackground(self):
        if self.backgroundColor:
            self.image.paste(self.backgroundColor, (0, 0, self.image.size[0], self.image.size[1]))
            
    def paintBorder(self):
        if self.borderColor:
            self._draw.rectangle((0, 0, self.image.size[0]-1, self.image.size[1]-1), outline = self.borderColor)
            
    def paintContent(self, draw):
        pass
        
    def listenToModel(self, model, *names):
        if not model in self.models:
            self.models[model] = []
        self.models[model].extend(names)
        model.addListener(self)
    
    def modelUpdated(self, model, *names):
        if model in self.models:
            for name in names:
                if name in self.models[model]:
                    self.dirty = True
                    return
        