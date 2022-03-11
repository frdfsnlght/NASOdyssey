
import os, time, psutil, socket
from LumaUI import Model
from .Error import Error

class NetInterface(Model):

    def __init__(self, intName, utilizationHistorySize = 128, addressType = socket.AF_INET):
        super().__init__()
        self.intName = intName
        self.addressType = addressType
        
        stats = psutil.net_if_stats()[self.intName]
        self.maxSpeed = stats.speed * 118000 # convert to bytes per second taking into account overhead

        self.rxBytes = 0
        self.txBytes = 0
        self.receiving = False
        self.transmitting = False
        self.rxTxThreshold = 1000

        self.rxBytesUtil = None
        self.txBytesUtil = None
        
        self.rxUtilization = 0
        self.rxUtilizationHistory = []
        self.txUtilization = 0
        self.txUtilizationHistory = []
        self.utilizationHistorySize = utilizationHistorySize
        self.utilizationTime = 0
        self.utilizationInterval = 1

        self.address = None
        self.addressTime = 0
        self.addressInterval = 30
        
    # override
    def updateValues(self):
        self.updateActivity();
        if time.time() - self.utilizationTime >= self.utilizationInterval:
            self.updateUtilization()
            self.utilizationTime = time.time()
        if time.time() - self.addressTime >= self.addressInterval:
            self.updateAddress()
            self.addressTime = time.time()
            
    def updateActivity(self):
        counters = psutil.net_io_counters(pernic = True)[self.intName]
        rx = counters.bytes_recv
        tx = counters.bytes_sent
        
        if rx - self.rxBytes < self.rxTxThreshold:
            if self.receiving:
                self.receiving = False
                self.notify('receiving')
        else:
            if not self.receiving:
                self.receiving = True
                self.notify('receiving')
        if tx - self.txBytes < self.rxTxThreshold:
            if self.transmitting:
                self.transmitting = False
                self.notify('transmitting')
        else:
            if not self.transmitting:
                self.transmitting = True
                self.notify('transmitting')
        self.rxBytes = rx
        self.txBytes = tx

    def updateUtilization(self):
        if not self.rxBytesUtil:
            self.rxBytesUtil = self.rxBytes
            self.txBytesUtil = self.txBytes
            return;
            
        seconds = time.time() - self.utilizationTime;
        rxBytes = self.rxBytes - self.rxBytesUtil
        txBytes = self.txBytes - self.txBytesUtil

        rxu = min(rxBytes / (self.maxSpeed * seconds), 1)
        if rxu != self.rxUtilization:
            self.rxUtilization = rxu
            self.notify('rxUtilization')
        self.rxUtilizationHistory.insert(0, self.rxUtilization)
        del(self.rxUtilizationHistory[self.utilizationHistorySize:])
            
        txu = min(rxBytes / (self.maxSpeed * seconds), 1)
        if txu != self.txUtilization:
            self.txUtilization = txu
            self.notify('txUtilization')
        self.txUtilizationHistory.insert(0, self.txUtilization)
        del(self.txUtilizationHistory[self.utilizationHistorySize:])
        self.notify('rxUtilizationHistory', 'txUtilizationHistory')
        
        self.rxBytesUtil = self.rxBytes
        self.txBytesUtil = self.txBytes
        
    def updateAddress(self):
        addresses = psutil.net_if_addrs()[self.intName]
        for address in addresses:
            if address.family == self.addressType:
                if address.address != self.address:
                    self.address = address.address
                    self.notify('address')
                return
        if not self.address is None:
            self.address = None
            self.notify('address')
        
    # override
    def getValue(self, name, idx = 0):
        if name in ('receiving', 'transmitting', 'rxUtilization', 'txUtilization', 'address'):
            return getattr(self, name)
        if name == 'rxUtilizationHistory':
            if idx < len(self.rxUtilizationHistory):
                return self.rxUtilizationHistory[idx]
            else:
                return None
        if name == 'txUtilizationHistory':
            if idx < len(self.txUtilizationHistory):
                return self.txUtilizationHistory[idx]
            else:
                return None
        return None
        
    # override
    def getValueSize(self, name):
        if name in ('rxUtilizationHistory', 'txUtilizationHistory'):
            return self.utilizationHistorySize
        return 0
