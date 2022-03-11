
from . import Container

class Deck(Container):

    def __init__(self):
        super().__init__()
        self._card = None

    # override
    def add(self, child):
        self.children.append(child)
        child.parent = self
        child.position = (0, 0)
        child.size = self.size
        if self._card is None:
            self._card = 0
            self.dirty = True
            
    # override
    def remove(self, child):
        if child in self.children:
            idx = self.children.index(child)
            Container.remove(self, child)
            if self._card == idx and idx == len(self.children):
                self._card -= 1
                if self._card == -1:
                    self._card = None
                self.dirty = True

    @property
    def card(self):
        return self._card
        
    @card.setter
    def card(self, value):
        if value in self.children:
            value = self.children.index(value)
        if isinstance(value, int):
            if value < 0 or value >= len(self.children):
                raise ValueError('card index out of range')
        else:
            raise ValueError('invalid card')
        self._card = value
        self.dirty = True
        
    def nextCard(self):
        if self._card is None:
            if len(self.children) > 0:
                self._card = 0
                self.dirty = True
            return
        self._card += 1
        if self._card >= len(self.children):
            self._card = 0
        self.dirty = True
    
    def previousCard(self):
        if self._card is None:
            if len(self.children) > 0:
                self._card = len(self.children) - 1
                self.dirty = True
            return
        self._card -= 1
        if self._card < 0:
            self._card = len(self.children) - 1
        self.dirty = True
    
    # override
    def paintContent(self, draw):
        if self._card is None: return
        child = self.children[self._card]
        child.paint()
        if child.image:
            box = (0, 0, *self.size)
            self.image.paste(child.image, box)
            