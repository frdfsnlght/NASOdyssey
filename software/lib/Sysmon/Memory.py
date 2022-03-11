
import os, time, psutil
from LumaUI import Model

class Memory(Model):

    def __init__(self, utilizationHistorySize = 128):
        super().__init__()
        self.utilization = psutil.virtual_memory().percent / 100
        self.utilizationHistory = []
        self.utilizationHistorySize = utilizationHistorySize
        self.updateInterval = 1
    
    # override
    def updateValues(self):
        self.updateUtilization();
    
    def updateUtilization(self):
        u = psutil.virtual_memory().percent / 100
        if u != self.utilization:
            self.utilization = u
            self.notify('utilization')
        self.utilizationHistory.insert(0, self.utilization)
        del(self.utilizationHistory[self.utilizationHistorySize:])
        self.notify('utilizationHistory')
    
    # override
    def getValue(self, name, idx = 0):
        if name in ('utilization'):
            return getattr(self, name)
        if name == 'utilizationHistory':
            if idx < len(self.utilizationHistory):
                return self.utilizationHistory[idx]
            else:
                return None
        return None
        
    # override
    def getValueSize(self, name):
        if name in ('utilizationHistory'):
            return self.utilizationHistorySize
        return 0
