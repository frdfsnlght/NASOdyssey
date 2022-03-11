
import time
import PeripheryGPIO as GPIO
from LumaUI import Model
from .Error import Error

class Fan(Model):

    def __init__(self, powerPin = None, sensePin = None, pwmPin = None, minDutyCycle = 20, maxDutyCycle = 100, polarity = 'normal', fanCurve = None, fanOnTemp = 50, historySize = 128):
        super().__init__()
        
        self.powerPin = powerPin
        self.sensePin = sensePin
        self.pwmPin = pwmPin
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
        self.pwm = None
        
        if self.powerPin:
            GPIO.setup(self.powerPin, GPIO.OUT)
        if self.pwmPin:
            self.pwm = GPIO.PWM(self.pwmPin, frequency = 20000, polarity = polarity)
        if self.sensePin:
            GPIO.setup(self.sensePin, GPIO.IN, GPIO.PUD_UP, edge = GPIO.FALLING)
            self.senseThread = threading.Thread(target = self.senseRun, name = 'fan.sense({})'.format(self.sensePin))
            self.senseThread.start()
        
    def addSensor(self, model, name):
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
            
            if s > 0:
                if self.powerPin:
                    GPIO.output(self.powerPin, GPIO.HIGH)
                if self.pwmPin:
                    dc = self.minDutyCycle + (s * (self.maxDutyCycle - self.minDutyCycle))
                    self.pwm.ChangeDutyCycle(dc)
            else:
                if self.powerPin:
                    GPIO.output(self.powerPin, GPIO.LOW)
                if self.pwmPin:
                    self.pwm.ChangeDutyCycle(0)
        
    # override
    def getValue(self, name, idx = 0):
        if name in ('speed', 'rpm', 'temperature'):
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

    def senseRun(self):
        lastCalcTime = time.time()
        pulseCount = 0
        while True:
            if GPIO.wait_for_edge(self.sensePin, GPIO.FALLING, timeout = 1):
                pulseCount += 1
            if time.time() - lastCalcTime >= 1:
                pps = pulseCount / (time.time() - lastCalcTime)
                lastCalcTime = time.time()
                pulseCount = 0
                # fans pulse 2 times per revolution
                rpm = int(30 * pps)
                if rpm != self.rpm:
                    self.rpm = rpm
                    self.notify('rpm')
            
