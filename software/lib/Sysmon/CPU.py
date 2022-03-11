
import os, time, psutil
from LumaUI import Model

class CPU(Model):

    def __init__(self, tempName = 'coretemp', historySize = 128):
        super().__init__()
        self.tempName = tempName
        self.historySize = historySize
        
        self.utilization = psutil.cpu_percent()
        self.utilizationHistory = []
    
        self.temperature = None
        self.temperatureHistory = []
        
        self.updateInterval = 1
        
    # override
    def updateValues(self):
        self.updateUtilization();
        self.updateTemperature();
    
    def updateUtilization(self):
        u = psutil.cpu_percent() / 100
        if u != self.utilization:
            self.utilization = u
            self.notify('utilization')
        self.utilizationHistory.insert(0, self.utilization)
        del(self.utilizationHistory[self.historySize:])
        self.notify('utilizationHistory')

    def updateTemperature(self):
        t = psutil.sensors_temperatures()[self.tempName][0].current
        if t != self.temperature:
            self.temperature = t
            self.notify('temperature')
        self.temperatureHistory.insert(0, self.temperature)
        del(self.temperatureHistory[self.historySize:])
        self.notify('temperatureHistory')
            
    # override
    def getValue(self, name, idx = 0):
        if name in ('utilization', 'temperature'):
            return getattr(self, name)
        if name == 'utilizationHistory':
            if idx < len(self.utilizationHistory):
                return self.utilizationHistory[idx]
            else:
                return None
        if name == 'temperatureHistory':
            if idx < len(self.temperatureHistory):
                return self.temperatureHistory[idx]
            else:
                return None
        return None
        
    # override
    def getValueSize(self, name):
        if name in ('utilizationHistory', 'temperatureHistory'):
            return self.historySize
        return 0
