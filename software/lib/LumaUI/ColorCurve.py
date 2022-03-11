
class ColorCurve():

    def __init__(self):
        self.points = []
    
    def addPoint(self, val, r, g, b):
        self.points.append((val, r, g, b))
        self.points.sort(key = lambda x:x[0])
        
    def getColor(self, val):
        if val <= self.points[0][0]:
            return self.points[0][1:]
        for i, p in enumerate(self.points[1:]):
            if val <= p[0]:
                p1 = self.points[i]
                p2 = p
                frac = (val - p1[0]) / (p2[0] - p1[0])
                return (
                    p1[1] + int((p2[1] - p1[1]) * frac),
                    p1[2] + int((p2[2] - p1[2]) * frac),
                    p1[3] + int((p2[3] - p1[3]) * frac)
                )
        return self.points[-1][1:]
