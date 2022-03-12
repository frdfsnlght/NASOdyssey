#!/usr/local/bin/python

import sys, os, time
from luma.core.interface.serial import spi
from luma.oled.device import ssd1351
from PIL import ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import Sysmon, LumaUI
import PeripheryGPIO as GPIO

LOOP_INTERVAL = 0.2
BUTTON_PIN = 21 # 21 BCM, 40 board

#serial = spi(port = 1, device = 0, gpio = GPIO, gpio_RST = 23)
serial = spi(port = 1, device = 0, gpio = GPIO)
device = ssd1351(serial, bgr = True, rotate = 0)

font12 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts', 'AltonaSans-Regular.ttf'), 12)
font16 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts', 'AltonaSans-Regular.ttf'), 16)

disk1 = Sysmon.Disk('/dev/sda', smart = True)
disk2 = Sysmon.Disk('/dev/sdb', smart = True)
disk3 = Sysmon.Disk('/dev/sdc', smart = True)
diskE = Sysmon.Disk('/dev/sdd')
net1 = Sysmon.NetInterface('enp2s0')
net2 = Sysmon.NetInterface('enp3s0')
cpu = Sysmon.CPU()
memory = Sysmon.Memory()
zfs = Sysmon.ZFSPool('pool')
zfs.addDisk(disk1)
zfs.addDisk(disk2)
zfs.addDisk(disk3)
fanCurve = LumaUI.FloatCurve()
fanCurve.addPoint(30, 0)
fanCurve.addPoint(60, 1)
fan = Sysmon.ArduinoFan(fanCurve = fanCurve)
fan.addSensor(disk1)
fan.addSensor(disk2)
fan.addSensor(disk3)
fs = Sysmon.FileSystem('/sysmon')

ui = LumaUI.Device(device)

# special Text subcalss to change background to red if ZFS isn't 'ONLINE'
class ZFSStatus(LumaUI.Text):
    # override
    def modelUpdated(self, model, *names):
        LumaUI.Text.modelUpdated(self, model, *names)
        if model == zfs and 'state' in names:
            state = model.getValue('state')
            if state == 'ONLINE':
                self.backgroundColor = (0, 0, 0)
            else:
                self.backgroundColor = (255, 0, 0)
            self.dirty = True

def createUI():
    
    # =========
    # First card
    
    card = LumaUI.Container()
    ui.add(card)
    
    x, num = 0, 1
    for d in (disk1, disk2, disk3, diskE):
        w = LumaUI.DiskActivity(d)
        w.position = (x, 0)
        w.size = (20, 20)
        if w == diskE:
            w.label = 'E'
        else:
            w.label = str(num)
        w.labelFont = font12
        card.add(w)
        num += 1
        x += 21

    x, num = 87, 1
    for n in (net1, net2):
        w = LumaUI.NetActivity(n)
        w.position = (x, 0)
        w.size = (20, 20)
        w.label = str(num)
        w.labelFont = font12
        card.add(w)
        num += 1
        x += 21

    colorCurve = LumaUI.ColorCurve()
    colorCurve.addPoint(0.1, 0, 255, 0)
    colorCurve.addPoint(0.9, 255, 0, 0)
    
    w = LumaUI.HistoryGraph(cpu, 'utilizationHistory', colorCurve = colorCurve)
    w.position = (0, 22)
    w.size = (128, 40)
    w.label = 'CPU'
    w.labelFont = font12
    card.add(w)
    
    w = LumaUI.HistoryGraph(memory, 'utilizationHistory', colorCurve = colorCurve)
    w.position = (0, 63)
    w.size = (128, 40)
    w.label = 'MEM'
    w.labelFont = font12
    card.add(w)

    w = ZFSStatus('ZFS {}', font = font16, halign = 'center', valign = 'center')
    w.addValue(zfs, 'state')
    w.position = (0, 105)
    w.size = (128, 23)
    card.add(w)
    
    # =========
    # Second card
    
    card = LumaUI.Container()
    ui.add(card)
    y = 0
    h = 11
    incr = h + 2
    
    w = LumaUI.Text('Net 1: {}', font = font12, valign = 'center')
    w.addValue(net1, 'address')
    w.position = (0, y)
    w.size = (128, h)
    card.add(w)
    y += incr
    
    w = LumaUI.Text('Net 2: {}', font = font12, valign = 'center')
    w.addValue(net2, 'address')
    w.position = (0, y)
    w.size = (128, h)
    card.add(w)
    y += incr
 
    w = LumaUI.Text('CPU Temp: {:.0f}' + u"\N{DEGREE SIGN}", font = font12, valign = 'center')
    w.addValue(cpu, 'temperature')
    w.position = (0, y)
    w.size = (128, h)
    card.add(w)
    y += incr

    w = LumaUI.Text('Disk 1 Temp: {:.0f}' + u"\N{DEGREE SIGN}", font = font12, valign = 'center')
    w.addValue(disk1, 'temperature')
    w.position = (0, y)
    w.size = (128, h)
    card.add(w)
    y += incr

    w = LumaUI.Text('Disk 2 Temp: {:.0f}' + u"\N{DEGREE SIGN}", font = font12, valign = 'center')
    w.addValue(disk2, 'temperature')
    w.position = (0, y)
    w.size = (128, h)
    card.add(w)
    y += incr

    w = LumaUI.Text('Disk 3 Temp: {:.0f}' + u"\N{DEGREE SIGN}", font = font12, valign = 'center')
    w.addValue(disk3, 'temperature')
    w.position = (0, y)
    w.size = (128, h)
    card.add(w)
    y += incr

    w = LumaUI.Text('Fan: {:.0f}%  {}rpm', font = font12, valign = 'center')
    w.addValue(fan, ('speed', lambda s:s*100), ('rpm', lambda r:r if not r is None else 0))
    w.position = (0, y)
    w.size = (128, h)
    card.add(w)
    y += incr
    
    w = LumaUI.Text('FS:', font = font12, valign = 'center')
    w.position = (0, y)
    w.size = (18, h)
    card.add(w)
    
    w = LumaUI.Gauge(fs, 'utilization', colorCurve = colorCurve)
    w.position = (18, y)
    w.size = (110, h)
    card.add(w)


if __name__ == '__main__':
    createUI()

    GPIO.setup(BUTTON_PIN, direction = GPIO.IN, pull_up_down = GPIO.PUD_UP)
    buttonUp = True
    
    try:
        while True:
            for model in (disk1, disk2, disk3, diskE, net1, net2, cpu, memory, zfs, fs, fan):
                model.update()
            ui.paint()
            
            if GPIO.input(BUTTON_PIN):
                if not buttonUp:
                    buttonUp = True
            elif buttonUp:
                buttonUp = False
                ui.nextCard()
            
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        print()
        sys.exit(0)
        