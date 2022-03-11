
import time

class Model():

    def __init__(self):
        self.listeners = []
        self.updateInterval = 0
        self.lastUpdateTime = 0

    def addListener(self, listener):
        if not listener in self.listeners:
            self.listeners.append(listener)
            
    def removeListener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)
            
    def notify(self, *names):
        for listener in self.listeners:
            listener.modelUpdated(self, *names)
            
    def update(self):
        if self.updateInterval is None:
            return
        if self.updateInterval == 0:
            self.updateValues()
        elif time.time() - self.lastUpdateTime >= self.updateInterval:
            self.updateValues()
            self.lastUpdateTime = time.time()
        
    def updateValues(self):
        pass
            
    # Returns the value of 'name' at the specified index
    def getValue(self, name, idx = 0):
        return None
        
    # Returns the number of values for 'name' available
    def getValueSize(self, name):
        return 0
