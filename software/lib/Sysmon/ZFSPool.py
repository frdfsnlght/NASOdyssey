
import time, subprocess, re
from LumaUI import Model
from .Error import Error

class ZFSPool(Model):

    def __init__(self, pool):
        super().__init__()
        self.pool = pool
        self.state = None
        self.disks = []
        self.updateInterval = 60
    
    def addDisk(self, disk):
        self.disks.append(disk)
        
    # override
    def updateValues(self):
        nscmd = ['nsenter', '-t', '1', '-m', '-u', '-n', '-i', 'zpool', 'status', self.pool]
        result = subprocess.run(nscmd, stdout = subprocess.PIPE)
        out = result.stdout.decode('utf-8')
    
        if re.search(r"no such pool", out):
            raise Error('unable to get status of pool "{}"'.format(self.pool))
            
        match = re.search(r"state:\s*([\w\-]+)", out)
        if match:
            if match.group(1) != self.state:
                self.state = match.group(1)
                self.notify('state')
        else:
            raise Error('unable to find state of pool "{}"'.format(self.pool))

        for disk in self.disks:
            serial = disk.serialNumber
            if serial is None: continue
            match = re.search(serial + r"\S*\s+(\S+)", out)
            if match:
                disk.setError(match.group(1) != 'ONLINE')
        
    # override
    def getValue(self, name, idx = 0):
        if name in ('state'):
            return getattr(self, name)
        return None
        