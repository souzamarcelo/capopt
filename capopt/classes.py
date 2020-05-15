#!/usr/bin/python3

class Point:
    def __init__(self, _effort, _value):
        self.effort = _effort
        self.value = _value
        
    def __str__(self):
        return str(self.effort) + "," + str(self.value)


class Trajectory:
    def __init__(self, _candidateId, _instanceId, _seed, _points):
        self.candidateId = _candidateId
        self.instanceId = _instanceId
        self.seed = _seed
        self.points = _points
        
    def getResult(self):
        if len(self.points) == 0:
            return "<empty trajectory>"
        return self.points[-1].value
    
    def getLastEffort(self):
        if len(self.points) == 0:
            return None
        return self.points[-1].effort    
    
    def isEmpty(self):
        return (len(self.points) == 0)

    def addPoint(self, point, effortLimit):
        if point.effort > effortLimit and len(self.points) > 0: return
        elif point.effort > effortLimit: point.effort = effortLimit
        if len(self.points) == 0:
            self.points.append(point)
        else:
            if point.value < self.points[-1].value:
                if point.effort == self.points[-1].effort:
                    self.points[-1].value = point.value
                else:
                    self.points.append(point)
    
    def addCappedPoint(self, point):
        if len(self.points) == 0:
            self.points.append(point)
        else:
            if self.points[-1].effort != point.effort or self.points[-1].value != point.value:
                self.points.append(point)
    
    def clean(self):
        newPoints = []
        for point in self.points:
            if point.value != float("inf"):
                newPoints.append(point)
        self.points = newPoints
    
    def getValue(self, effort):
        result = float("inf")
        for point in self.points:
            if effort >= point.effort:
                result = point.value
            else:
                break
        return result    
    
    def getEffort(self, value, penaltyValue):
        result = penaltyValue
        for point in self.points:
            if point.value <= value:
                result = point.effort
                break
        return result
    
    def __str__(self):
        if len(self.points) == 0:
            return "[]"
        result = "["
        for point in self.points:
            result += str(point) + "/"
        result = result[:-1]
        result += "]"
        return result