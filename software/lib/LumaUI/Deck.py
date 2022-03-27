
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
        if not isinstance(value, int):
            raise ValueError('invalid card')
        self.setCard(value, 1)
        
    def setCard(self, value, dir):
        loops = len(self.children) + 1
        while loops > 0:
            loops -= 1
            if value < 0:
                value = len(self.children) - 1
            elif value >= len(self.children):
                value = 0
            if self.children[value].hidden:
                value += dir
            else:
                break;
            
        if loops == 0:
            raise ValueError('no visible cards available')
            
        self._card = value
        self.dirty = True
        
    def nextCard(self):
        if self._card is None:
            self.setCard(0, 1)
        else:
            self.setCard(self.card + 1, 1)
    
    def previousCard(self):
        if self._card is None:
            self.setCard(-1, -1)
        else:
            self.setCard(self.card - 1, -1)
    
    # override
    def paintContent(self, draw):
        if self._card is None: return
        child = self.children[self._card]
        child.paint()
        if child.image:
            box = (0, 0, *self.size)
            self.image.paste(child.image, box)
            