
class FloatCurve():

    def __init__(self):
        self.points = []
    
    def addPoint(self, valIn, valOut):
        self.points.append((valIn, valOut))
        self.points.sort(key = lambda x:x[0])
        
    def getValue(self, valIn):
        if valIn <= self.points[0][0]:
            return self.points[0][1]
        for i, p in enumerate(self.points[1:]):
            if valIn <= p[0]:
                p1 = self.points[i]
                p2 = p
                frac = (valIn - p1[0]) / (p2[0] - p1[0])
                return p1[1] + ((p2[1] - p1[1]) * frac)
        return self.points[-1][1]
