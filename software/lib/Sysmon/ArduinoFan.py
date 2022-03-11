
import time, serial, threading
from LumaUI import Model
from .Error import Error

class ArduinoFan(Model):

    def __init__(self, port = '/dev/ttyACM0', bps = 115000, minDutyCycle = 20, maxDutyCycle = 100, fanCurve = None, fanOnTemp = 50, historySize = 128):
        super().__init__()

        self.port = port
        self.minDutyCycle = minDutyCycle
        self.maxDutyCycle = maxDutyCycle
        self.fanCurve = fanCurve
        self.fanOnTemp = fanOnTemp
        self.historySize = historySize
        
        self.speed = None
        self.rpm = None
        self.temperature = None
        self.temperatureHistory = []
        
        self.updateInterval = 1
        self.sensors = []
        
        self.serial = serial.Serial(self.port, bps, timeout = 1)
        self.rpmUpdated = threading.Event()
        self.threadStop = threading.Event()
        self.thread = threading.Thread(target = self.readLoop, name = 'ArduinoFan({})'.format(self.port), daemon = True)
        self.thread.start()
        
    def addSensor(self, model, name = 'temperature'):
        self.sensors.append((model, name))
        
    # override
    def updateValues(self):
        self.updateTemperature();
        self.updateSpeed()
        
    def updateTemperature(self):
        t = 0
        for sensor in self.sensors:
            t = max(t, sensor[0].getValue(sensor[1]))
        if t == 0: t = None
        if t != self.temperature:
            self.temperature = t
            self.notify('temperature')
        self.temperatureHistory.insert(0, self.temperature)
        del(self.temperatureHistory[self.historySize:])
        self.notify('temperatureHistory')
       
    def updateSpeed(self):
        if self.fanCurve:
            s = self.fanCurve.getValue(self.temperature)
        else:
            s = 1 if self.temperature >= self.fanOnTemp else 0
        if s != self.speed:
            self.speed = s
            self.notify('speed')
            dc = int(self.minDutyCycle + (s * (self.maxDutyCycle - self.minDutyCycle)))
            self.serial.write('DUTYCYCLE {}'.format(dc).encode('utf-8'))
        
        if self.rpmUpdated.is_set():
            self.rpmUpdated.clear()
            self.notify('rpm')
            
        
    # override
    def getValue(self, name, idx = 0):
        if name in ('speed', 'rpm', 'temperature'):
            return getattr(self, name)
        if name == 'temperatureHistory':
            if idx < len(self.temperatureHistory):
                return self.temperatureHistory[idx]
            else:
                return None
        return None
        
    # override
    def getValueSize(self, name):
        if name in ('temperatureHistory'):
            return self.historySize
        return 0

    def readLoop(self):
        while not self.threadStop.is_set():
            try:
                line = self.serial.readline()
            except:
                return
            if line:
                line = line.decode('utf-8').rstrip("\n")
                print('got line: {}'.format(line))
                if line.startswith('RPM '):
                    rpm = int(line[4:])
                    if rpm != self.rpm:
                        self.rpm = rpm
                        self.rpmUpdated.set()
            