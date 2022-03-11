
import time, subprocess, re
from LumaUI import Model
from .Error import Error

class Disk(Model):

    def __init__(self, dev, smart = False, temperatureHistorySize = 128):
        super().__init__()
        self.dev = dev
        self.smart = smart
        self.name = dev.split('/')[2]
        self.error = False
        self.available = False
        self.testResult = None
        self.temperature = None
        self.temperatureHistory = []
        self.temperatureHistorySize = temperatureHistorySize
        self.smartTime = 0
        self.smartInterval = 30

        self.reads = 0
        self.writes = 0
        self.reading = False
        self.writing = False
        self.serialNumber = None
    
    # override
    def updateValues(self):
        self.updateActivity();
        if self.smart and time.time() - self.smartTime >= self.smartInterval:
            self.updateSmart()
            self.smartTime = time.time()
            
    def updateActivity(self):
        try:
            f = open('/sys/block/{}/stat'.format(self.name)).read().split()
        except:
            if self.available:
                self.available = False
                self.notify('available')
            return
        if not self.available:
            self.available = True
            self.notify('available')
        reads = f[0]
        writes = f[4]
        if reads == self.reads:
            if self.reading:
                self.reading = False
                self.notify('reading')
        else:
            self.reads = reads
            if not self.reading:
                self.reading = True
                self.notify('reading')
        if writes == self.writes:
            if self.writing:
                self.writing = False
                self.notify('writing')
        else:
            self.writes = writes
            if not self.writing:
                self.writing = True
                self.notify('writing')
                
    def updateSmart(self):
        nscmd = ['nsenter', '-t', '1', '-m', '-u', '-n', '-i', 'smartctl', '-iHA', self.dev]
        result = subprocess.run(nscmd, stdout = subprocess.PIPE)
        out = result.stdout.decode('utf-8')
    
        if re.search(r"No such device", out):
            if self.available:
                self.available = False
                self.notify('available')
            return
            
        match = re.search(r"Serial Number:\s*([\w\-]+)", out)
        if match:
            if match.group(1) != self.serialNumber:
                self.serialNumber = match.group(1)
                self.notify('serialNumber')
        else:
            raise Error('unable to identify serial number for {}'.format(self.dev))

        match = re.search(r"self-assessment test result:\s*([\S]+)", out)
        if match:
            if match.group(1) != self.testResult:
                self.testResult = match.group(1)
                self.notify('testResult')
        else:
            raise Error('unable to identify test result for {}'.format(self.dev))

        match = re.search(r"(?m)Temperature_Celsius.+?(\d+)$", out)
        if match:
            t = int(match.group(1))
            if t != self.temperature:
                self.temperature = int(match.group(1))
                self.notify('temperature')
            self.temperatureHistory.insert(0, self.temperature)
            del(self.temperatureHistory[self.temperatureHistorySize:])
            self.notify('temperatureHistory')
        else:
            raise Error('unable to read temperature for {}'.format(self.dev))
            
    def setError(self, error):
        if error == self.error: return
        self.error = error
        self.notify('error')
        
    # override
    def getValue(self, name, idx = 0):
        if name in ('available', 'error', 'testResult', 'reading', 'writing', 'temperature'):
            return getattr(self, name)
        if name == 'temperatureHistory':
            if idx < len(self.temperatureHistory):
                return self.temperatureHistory[idx]
        return None
        
    # override
    def getValueSize(self, name):
        if name == 'temperatureHistory':
            return self.temperatureHistorySize
        return 0
