
import os, time
from LumaUI import Model
from .Error import Error

class NetInterface(Model):

    def __init__(self, intName, maxBps = 118000000, utilizationHistorySize = 128):
        super().__init__()
        self.intName = intName
        self.maxBps = maxBps
        self.path = '/sys/class/net/{}/statistics/'.format(self.intName)

        if not os.path.isdir(self.path):
            raise Error('unable to find network statistics for {}'.format(self.intName))
            
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
    
    # override
    def updateValues(self):
        self.updateActivity();
        if time.time() - self.utilizationTime >= self.utilizationInterval:
            self.updateUtilization()
            self.utilizationTime = time.time()
            
    def updateActivity(self):
        try:
            rx = int(open(self.path + 'rx_bytes').read())
            tx = int(open(self.path + 'tx_bytes').read())
        except:
            return
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

        rxu = rxBytes / (self.maxBps * seconds)
        if rxu != self.rxUtilization:
            self.rxUtilization = rxu
            self.notify('rxUtilization')
        self.rxUtilizationHistory.insert(0, self.rxUtilization)
        del(self.rxUtilizationHistory[self.utilizationHistorySize:])
            
        txu = rxBytes / (self.maxBps * seconds)
        if txu != self.txUtilization:
            self.txUtilization = txu
            self.notify('txUtilization')
        self.txUtilizationHistory.insert(0, self.txUtilization)
        del(self.txUtilizationHistory[self.utilizationHistorySize:])
        self.notify('rxUtilizationHistory', 'txUtilizationHistory')
        
        self.rxBytesUtil = self.rxBytes
        self.txBytesUtil = self.txBytes
        
    # override
    def getValue(self, name, idx = 0):
        if name in ('receiving', 'transmitting', 'rxUtilization', 'txUtilization'):
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
