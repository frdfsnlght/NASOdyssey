
import time, threading
from periphery import GPIO

IN = 'in'
OUT = 'out'
PUD_UP = 'pull_up'
PUD_DOWN = 'pull_down'
LOW = False
HIGH = True
BOARD = 'board'
BCM = 'bcm'
RISING = 'rising'
FALLING = 'falling'
BOTH = 'both'

# maps to BIOS line, cdev path, cdev line, sysfs line
BOARD_PINS = {
    3: (110, "/dev/gpiochip1", 34, 386),
    5: (111, "/dev/gpiochip1", 35, 387),
    7: (161, "/dev/gpiochip2", 5, 337),
    8: (61, "/dev/gpiochip0", 61, 493),
    10: (60, "/dev/gpiochip0", 60, 492),
    11: (88, "/dev/gpiochip1", 12, 364),
    12: (162, "/dev/gpiochip2", 6, 338),
    13: (136, "/dev/gpiochip1", 60, 412),
    15: (137, "/dev/gpiochip1", 61, 413),
    16: (145, "/dev/gpiochip1", 69, 421),
    18: (146, "/dev/gpiochip1", 70, 422),
    19: (83, "/dev/gpiochip1", 7, 359),
    21: (82, "/dev/gpiochip1", 6, 358),
    22: (114, "/dev/gpiochip1", 38, 390),
    23: (79, "/dev/gpiochip1", 3, 355),
    24: (80, "/dev/gpiochip1", 4, 356),
    26: (81, "/dev/gpiochip1", 5, 357),
    27: (112, "/dev/gpiochip1", 36, 388),
    28: (113, "/dev/gpiochip1", 37, 389),
    29: (139, "/dev/gpiochip1", 63, 415),
    31: (140, "/dev/gpiochip1", 64, 416),
    32: (115, "/dev/gpiochip1", 39, 391),
    33: (141, "/dev/gpiochip1", 65, 417),
    35: (163, "/dev/gpiochip2", 7, 339),
    36: (134, "/dev/gpiochip1", 58, 410),
    37: (143, "/dev/gpiochip1", 67, 419),
    38: (164, "/dev/gpiochip2", 8, 340),
    40: (165, "/dev/gpiochip2", 9, 341)
}

# maps to BIOS line, cdev path, cdev line, sysfs line
BCM_PINS = {
    2: (110, "/dev/gpiochip1", 34, 386),
    3: (111, "/dev/gpiochip1", 35, 387),
    4: (161, "/dev/gpiochip2", 5, 337),
    14: (61, "/dev/gpiochip0", 61, 493),
    15: (60, "/dev/gpiochip0", 60, 492),
    17: (88, "/dev/gpiochip1", 12, 364),
    18: (162, "/dev/gpiochip2", 6, 338),
    27: (136, "/dev/gpiochip1", 60, 412),
    22: (137, "/dev/gpiochip1", 61, 413),
    23: (145, "/dev/gpiochip1", 69, 421),
    24: (146, "/dev/gpiochip1", 70, 422),
    10: (83, "/dev/gpiochip1", 7, 359),
    9: (82, "/dev/gpiochip1", 6, 358),
    25: (114, "/dev/gpiochip1", 38, 390),
    11: (79, "/dev/gpiochip1", 3, 355),
    8: (80, "/dev/gpiochip1", 4, 356),
    7: (81, "/dev/gpiochip1", 5, 357),
    0: (112, "/dev/gpiochip1", 36, 388),
    1: (113, "/dev/gpiochip1", 37, 389),
    5: (139, "/dev/gpiochip1", 63, 415),
    6: (140, "/dev/gpiochip1", 64, 416),
    12: (115, "/dev/gpiochip1", 39, 391),
    13: (141, "/dev/gpiochip1", 65, 417),
    19: (163, "/dev/gpiochip2", 7, 339),
    16: (134, "/dev/gpiochip1", 58, 410),
    26: (143, "/dev/gpiochip1", 67, 419),
    20: (164, "/dev/gpiochip2", 8, 340),
    21: (165, "/dev/gpiochip2", 9, 341)
}

pinMode = BCM
pins = {}
edgeDetectThreads = {}

def setmode(mode):
    global pinMode
    pinModde = mode

def pinToDev(pin):
    if pinMode == BOARD:
        return BOARD_PINS[pin]
    elif pinMode == BCM:
        return BCM_PINS[pin]
    else:
        raise ValueError('invalid pin mode: {}'.format(pinMode))

def cleanup():
    global pins
    for dev, p in pins.items():
        p.close()
    pins = {}

def setup(pin, direction, pull_up_down = 'default'):
    dev = pinToDev(pin)
    #print('setting up pin {}: {}'.format(pin, dev))
    #p = GPIO(dev[3], direction) # using sysfs
    p = GPIO(dev[1], dev[2], direction, bias = pull_up_down) # using character device
    pins[dev] = p

def input(pin):
    dev = pinToDev(pin)
    if not dev in pins:
        raise ValueError('pin {} has not been setup'.format(pin))
    return pins[dev].read()

def output(pin, val):
    dev = pinToDev(pin)
    if not dev in pins:
        raise ValueError('pin {} has not been setup'.format(pin))
    pins[dev].write(val)

"""
# block for up to timeout milliseconds or forever
def wait_for_edge(pin, edge, timeout = None):
    dev = pinToDev(pin)
    if not dev in pins:
        raise ValueError('pin {} has not been setup'.format(pin))
    gpio = pins[dev]
    #gpio._set_edge = edge
    print(gpio)
    gpio.edge = edge
    gpio.read() # clear it
    print('waiting...')
    if gpio.poll():
        print('done')
#    if gpio.poll(timeout = (timeout / 1000) if timeout else None):
        #up = gpio.read()
        #event = gpio.read_event()
        # guess we ignore the event data?
        return True
    else:
        return False
   
def add_event_detect(pin, edge, callback = None, bouncetime = None):
    dev = pinToDev(pin)
    if not dev in pins:
        raise ValueError('pin {} has not been setup'.format(pin))
    gpio = pins[dev]
    #gpio.edge = edge
    stop = threading.Event()
    detected = threading.Event()
    thread = threading.Thread(target = _detectEdge, args = (gpio, pin, detected, stop, callback, bouncetime))
    edgeDetectThreads[dev] = (thread, detected, stop)
    thread.start()
    
def remove_event_detect(pin):
    dev = pinToDev(pin)
    if dev in edgeDetectThreads:
        thread, detected, stop = edgeDetectThreads[dev]
        del(edgeDetectThreads[dev])
        stop.set()
        thread.join()
        
# returns True when event is detected
def event_detected(pin):
    dev = pinToDev(pin)
    if dev in edgeDetectThreads:
        thread, detected, stop = edgeDetectThreads[dev]
        if detected.is_set():
            detected.clear();
            return True
        else:
            return False

def _detectEdge(gpio, pin, detected, stop, callback, bouncetime):
    lastEdgeTime = 0
    while not stop.is_set():
        if gpio.poll(1):
            event = gpio.read_event()
            # guess we ignore the event data?
            if bounceTime is None or (time.time() - lastEdgeTime) >= (bouncetime / 1000):
                detected.set()
                if not callback is None:
                    callback(pin)
        
"""

class PWM:

    def __init__(self, pin, frequency = 1000, polarity = 'normal'):
        self.pin = pin
        dev = pinToDev(pin)
        self.gpio = GPIO(dev[3], OUT) # using sysfs
        #self.gpio = GPIO(dev[1], dev[2], OUT)
        self.gpio.write(LOW)
        pins[dev] = self.gpio
        
        self.onTime = 0
        self.offTime = 0
        self.frequency = frequency
        self.polarity = polarity
        self.dutyCycle = 100
        self.running = False
        
        self.ChangeFrequency(self.frequency)
        self.ChangeDutyCycle(self.dutyCycle)
        self.thread = threading.Thread(target = self._pulse, name = 'pwm({})'.format(pin))

    def ChangeFrequency(self, frequency):
        if frequency < 1:
            raise ValueError('pwm frequency must be more than 1Hz for pin {}'.format(self.pin))
        self.frequency = frequency
        self.calculatePulseTimes()

    def ChangeDutyCycle(self, dutyCycle):
        if dutyCycle < 0 or dutyCycle > 100:
            raise ValueError('pwm duty cycle must be between 0 and 100 inclusive for pin {}'.format(self.pin))
        self.dutyCycle = dutyCycle
        self.calculatePulseTimes()

    def calculatePulseTimes(self):
        period = 1 / self.frequency
        if self.polarity == 'normal':
            self.onTime = period * self.dutyCycle / 100
        else:
            self.onTime = period * (100 - self.dutyCycle) / 100
        self.offTime = period - self.onTime

    def start(self, dutyCycle):
        if not self.running:
            self.ChangeDutyCycle(dutyCycle)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
            self.gpio.write(LOW)

    def _pulse(self):
        self.running = True
        while self.running:
            self.gpio.write(HIGH)
            time.sleep(self.onTime)
            self.gpio.write(LOW)
            time.sleep(self.offTime)

        