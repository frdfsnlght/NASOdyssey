
from . import Widget

class Container(Widget):

    def __init__(self):
        super().__init__()
        self.children = []
        
    def add(self, child):
        self.children.append(child)
        child.parent = self
        self.size = (
            max(self.size[0], child.position[0] + child.size[0]),
            max(self.size[1], child.position[1] + child.size[1])
        )
        self.dirty = True
        
    def remove(self, child):
        if child in self.children:
            self.children.remove(child)
        self.dirty = True
            
    # override
    def paintContent(self, draw):
        for child in self.children:
            child.paint()
            if child.image:
                box = (child._position[0], child._position[1], child._position[0] + child._size[0], child._position[1] + child._size[1])
                self.image.paste(child.image, box)
            