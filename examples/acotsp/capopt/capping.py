#!/usr/bin/python3
import math
import statistics
from math import log
from math import ceil
from math import floor
from classes import Trajectory
from classes import Point

class Capping:
    def __init__(self, _data):
        self.data = _data
        self.cappingMechanism = (AreaCapping(_data) if self.data.scenario['envelope'] == "area" else ProfileCapping(_data))

    def cap(self, effort, trajectory):
        if trajectory.isEmpty() or effort > self.data.scenario['effort-limit'] or self.data.execution['iteration'] <= 1:
            return False
        return self.cappingMechanism.cap(effort, trajectory)

    def report(self, trajectory):
        return self.cappingMechanism.report(trajectory)
            


class ProfileCapping:
    def __init__(self, _data):
        self.data = _data
        self.bestSoFar = float("inf")
        self.envelope = None

        if self.data.scenario['strategy'] == "adaptive" and self.data.isNewIteration():
            self.data.execution['aggressiveness'] = self.updateAggressiveness()
        self.envelope = self.getEnvelope()


    def cap(self, effort, trajectory):
        if (isinstance(self.envelope, str) or effort < self.envelope.points[0].effort):
            return False
        self.bestSoFar = min(self.bestSoFar, trajectory.getResult())
        return (self.bestSoFar > self.envelope.getValue(effort))


    def report(self, trajectory):
        result = {}
        result['envelope'] = self.envelope
        result['max-area'] = "NA"
        result['exec-area'] = "NA"
        return result


    def getEnvelope(self):
        if self.data.execution['iteration'] <= 1: return "<first iteration>"
        if self.data.scenario['strategy'] == "elitist":
            if self.data.execution['candidate-id'] in self.data.execution['irace-elites']: return "<evaluating elite candidate>"
            elites = self.selectElites()
            aggregatedReplications = self.aggregateReplications(elites)
            if len(aggregatedReplications) == 0: return "<no previous executions>"
            envelope = self.aggregateConfigurations(aggregatedReplications)
            envelope.clean()
            return envelope
        if self.data.scenario['strategy'] == "adaptive":
            executions = self.data.getExecutions(self.data.execution['instance-id'], False)
            if len(executions) == 0: return "<no previous execution>"
            executions.sort(key = lambda x : x['trajectory'].getResult())
            index = max(1, ceil((1 - self.data.execution['aggressiveness']) * len(executions)))
            executions = executions[:index]
            efforts = []
            [efforts.extend([point.effort for point in execution['trajectory'].points if point.effort not in efforts]) for execution in executions]
            efforts.sort()
            envelope = Trajectory(0, 0, 0, [])
            for effort in efforts:
                envelope.addPoint(Point(effort, max([execution['trajectory'].getValue(effort) for execution in executions])), self.data.scenario['effort-limit'])
            return envelope
        return "<no strategy defined>"


    def selectElites(self):
        if self.data.scenario['sel-elites'] == "elites":
            return self.data.execution['irace-elites']


    def aggregateReplications(self, elites):
        aggregatedReplications = []
        executions = self.data.getExecutions(self.data.execution['instance-id'], False)
        replications = [rep for rep in [[execution['trajectory'] for execution in executions if execution['candidate-id'] == elite] for elite in elites] if len(rep) > 0]
        aggregatedReplications.extend([self.aggregate(rep) for rep in replications])
        return aggregatedReplications


    def aggregate(self, replications):
        result = Trajectory(0, 0, 0, [])
        if self.data.scenario['ar'] == "exp":
            return self.exponentialModel(replications)
        efforts = []
        [efforts.extend([point.effort for point in replication.points if point.effort not in efforts]) for replication in replications]
        efforts.sort()
        for effort in efforts:
            if self.data.scenario['ar'] == "best":
                result.points.append(Point(effort, min([replication.getValue(effort) for replication in replications])))
            elif self.data.scenario['ar'] == "worst":
                result.points.append(Point(effort, max([replication.getValue(effort) for replication in replications])))
        return result
        
    
    def exponentialModel(self, replications):
        result = Trajectory(0, 0, 0, [])
        values = []
        for replication in replications:
            for point in replication.points:
                value = point.value
                if value not in values:
                    values.append(value)
        values.sort(reverse = True)
        for value in values:
            meanEffort = 0
            for replication in replications:
                penaltyValue = self.data.scenario['effort-limit'] * self.data.scenario['alpha']
                meanEffort += replication.getEffort(value, penaltyValue)
            meanEffort = meanEffort / len(replications)
            effort = -log(1 - (1 - self.data.scenario['p'])) * meanEffort
            point = Point(effort, value)
            result.points.append(point)
        return result


    def aggregateConfigurations(self, trajectories):
        envelope = Trajectory(0, 0, 0, [])
        efforts = []
        [efforts.extend([point.effort for point in trajectory.points if point.effort not in efforts]) for trajectory in trajectories]
        efforts.sort()
        for effort in efforts:
            if self.data.scenario['ac'] == "best":
                envelope.points.append(Point(effort, min([trajectory.getValue(effort) for trajectory in trajectories])))
            if self.data.scenario['ac'] == "worst":
                envelope.points.append(Point(effort, max([trajectory.getValue(effort) for trajectory in trajectories])))
        return envelope


    def updateAggressiveness(self):
        lastAggressiveness = (self.data.previousExecutions[-1]['aggressiveness'] if len(self.data.previousExecutions) > 0 else "NA")
        if self.data.execution['iteration'] <= 1: return lastAggressiveness
        nbExecutions, nbCapping = self.data.getAmountExecutionsLastIteration()
        amountCapping = nbCapping / nbExecutions

        if amountCapping < self.data.scenario['ag'] - self.data.scenario['epsilon']:
            executions = self.data.getExecutionsOfLastIteration(False)
            nbToCap = floor((self.data.scenario['ag'] * nbExecutions)) - nbCapping
            aggList = []
            for exe in executions:
                agg = self.aggressivenessToCap(exe)
                if agg is not None: aggList.append(agg)
            aggList.sort()
            nbToCap = max(min(nbToCap, len(aggList)), 0)
            return aggList[nbToCap - 1]

        elif amountCapping > self.data.scenario['ag'] + self.data.scenario['epsilon']:
            executions = self.data.getExecutionsOfLastIteration(True)
            nbToKeep = nbCapping - floor((self.data.scenario['ag'] * nbExecutions))
            aggList = []
            for exe in executions:
                agg = self.aggressivenessToKeep(exe)
                if agg is not None: aggList.append(agg)
            aggList.sort(reverse = True)
            nbToKeep = max(min(nbToKeep, len(aggList)), 0)
            return aggList[nbToKeep - 1]

        return lastAggressiveness


    def aggressivenessToCap(self, refExecution):
        executions = self.data.getExecutions(refExecution['instance-id'], False, refExecution['id'] - 1)
        if len(executions) == 0: return None
        executions.sort(key = lambda x : x['trajectory'].getResult())
        amount = 0
        for i in range(len(executions)):
            bound = i + 1
            efforts = []
            [efforts.extend([point.effort for point in exe['trajectory'].points if point.effort not in efforts]) for exe in executions[:bound]]
            efforts.sort()
            envelope = Trajectory(0, 0, 0, [])
            for effort in efforts:
                envelope.addPoint(Point(effort, max([exe['trajectory'].getValue(effort) for exe in executions[:bound]])), self.data.scenario['effort-limit'])
            efforts = efforts + [point.effort for point in refExecution['trajectory'].points if point.effort not in efforts]
            cap = False
            for effort in efforts:
                if refExecution['trajectory'].getValue(effort) > envelope.getValue(effort):
                    cap = True
                    break
            if cap:
                amount += 1
            else:
                break
        return 1 - (amount / len(executions))
        

    def aggressivenessToKeep(self, refExecution):
        effortCap = refExecution['trajectory'].getLastEffort()
        valueCap = refExecution['trajectory'].getResult()
        executions = self.data.getExecutions(refExecution['instance-id'], False, refExecution['id'] - 1)
        if len(executions) == 0: return None

        steps = []
        ratios = []
        for exe in executions:
            steps.append(len([point for point in exe['trajectory'].points if point.effort >= effortCap]))
            if exe['trajectory'].getValue(effortCap) != 0:
                ratios.append(exe['trajectory'].getResult() / exe['trajectory'].getValue(effortCap))
        medianSteps = ceil(statistics.median(steps))
        medianRatio = statistics.median(ratios)

        trajectory = Trajectory(0, 0, 0, [])
        trajectory.points = refExecution['trajectory'].points
        if medianSteps > 0:
            effortStep = (self.data.scenario['effort-limit'] - effortCap) / (medianSteps + 1)
            finalValue = valueCap * medianRatio
            valueStep = (valueCap - finalValue) / medianSteps
            
            lastEffort = effortCap
            lastValue = valueCap
            for i in range(medianSteps):
                lastEffort += effortStep
                lastValue -= valueStep
                trajectory.points.append(Point(lastEffort, lastValue))

        executions.sort(key = lambda x : x['trajectory'].getResult())
        amount = 0
        for i in range(len(executions)):
            bound = i + 1
            efforts = []
            [efforts.extend([point.effort for point in exe['trajectory'].points if point.effort not in efforts]) for exe in executions[:bound]]
            efforts.sort()
            envelope = Trajectory(0, 0, 0, [])
            for effort in efforts:
                envelope.addPoint(Point(effort, max([exe['trajectory'].getValue(effort) for exe in executions[:bound]])), self.data.scenario['effort-limit'])
            efforts = efforts + [point.effort for point in trajectory.points if point.effort not in efforts]
            cap = False
            for effort in efforts:
                if trajectory.getValue(effort) > envelope.getValue(effort):
                    cap = True
                    break
            if cap:
                amount += 1
            else:
                amount += 1
                break
        return 1 - (amount / len(executions))



class AreaCapping:
    def __init__(self, _data):
        self.data = _data
        self.maxArea = None

        if self.data.scenario['strategy'] == "adaptive" and self.data.isNewIteration():
            self.data.execution['aggressiveness'] = self.updateAggressiveness()
        self.maxArea = self.getMaxArea()
    

    def cap(self, effort, trajectory):
        if isinstance(self.maxArea, str):
            return False
        areaExecution = self.calculateArea(trajectory, effort)
        return areaExecution > self.maxArea

    
    def report(self, trajectory):
        result = {}
        result['envelope'] = "NA"
        result['max-area'] = self.maxArea
        result['exec-area'] = self.calculateArea(trajectory, self.data.scenario['effort-limit'])
        return result


    def getMaxArea(self):
        if self.data.execution['iteration'] <= 1: return "<first iteration>"
        if self.data.scenario['strategy'] == "adaptive":
            executions = self.data.getExecutions(self.data.execution['instance-id'], False)
            if len(executions) == 0: return "<no previous execution>"
            areas = []
            for exe in executions:
                areas.append(self.calculateArea(exe['trajectory'], self.data.scenario['effort-limit']))
            areas.sort()
            index = max(0, ceil((1 - self.data.execution['aggressiveness']) * len(areas)) - 1)
            return areas[index]
        
        if self.data.scenario['strategy'] == "elitist":
            if self.data.execution['candidate-id'] in self.data.execution['irace-elites']: return "<evaluating elite candidate>"
            elites = self.selectElites()
            aggregatedReplications = self.aggregateReplications(elites)
            if len(aggregatedReplications) == 0: return "<no previous execution>"
            area = self.aggregateConfigurations(aggregatedReplications)
            return area

        return "<no strategy defined>"
        

    def selectElites(self):
        if self.data.scenario['sel-elites'] == "elites":
            return self.data.execution['irace-elites']


    def aggregateReplications(self, elites):
        aggregatedReplications = []
        executions = self.data.getExecutions(self.data.execution['instance-id'], False)
        replications = [rep for rep in [[execution['trajectory'] for execution in executions if execution['candidate-id'] == elite] for elite in elites] if len(rep) > 0]
        aggregatedReplications.extend([self.aggregate(rep) for rep in replications])
        return aggregatedReplications


    def aggregate(self, replications):
        if self.data.scenario['ar'] == "best":
            return min(replications, key = lambda x: self.calculateArea(x, self.data.scenario['effort-limit']))
        elif self.data.scenario['ar'] == "worst":
            return max(replications, key = lambda x: self.calculateArea(x, self.data.scenario['effort-limit']))


    def aggregateConfigurations(self, trajectories):
        if self.data.scenario['ac'] == "best":
            return min([self.calculateArea(trajectory, self.data.scenario['effort-limit']) for trajectory in trajectories])
        elif self.data.scenario['ac'] == "worst":
            return max([self.calculateArea(trajectory, self.data.scenario['effort-limit']) for trajectory in trajectories])


    def updateAggressiveness(self):
        lastAggressiveness = (self.data.previousExecutions[-1]['aggressiveness'] if len(self.data.previousExecutions) > 0 else "NA")
        if self.data.execution['iteration'] <= 1: return lastAggressiveness
        nbExecutions, nbCapping = self.data.getAmountExecutionsLastIteration()
        amountCapping = nbCapping / nbExecutions

        if amountCapping < self.data.scenario['ag'] - self.data.scenario['epsilon']:
            executions = self.data.getExecutionsOfLastIteration(False)
            nbToCap = floor((self.data.scenario['ag'] * nbExecutions)) - nbCapping
            aggList = []
            for exe in executions:
                agg = self.aggressivenessToCap(exe)
                if agg is not None: aggList.append(agg)
            aggList.sort()
            nbToCap = max(min(nbToCap, len(aggList)), 0)
            return aggList[nbToCap - 1]

        elif amountCapping > self.data.scenario['ag'] + self.data.scenario['epsilon']:
            executions = self.data.getExecutionsOfLastIteration(True)
            nbToKeep = nbCapping - floor((self.data.scenario['ag'] * nbExecutions))
            aggList = []
            for exe in executions:
                agg = self.aggressivenessToKeep(exe)
                if agg is not None: aggList.append(agg)
            aggList.sort(reverse = True)
            nbToKeep = max(min(nbToKeep, len(aggList)), 0)
            return aggList[nbToKeep - 1]

        return lastAggressiveness
    
    
    def aggressivenessToCap(self, refExecution):
        executions = self.data.getExecutions(refExecution['instance-id'], False, refExecution['id'] - 1)
        if len(executions) == 0: return None
        shift = -refExecution['bkv'][refExecution['instance-name']]
        refArea = self.calculateArea(refExecution['trajectory'], self.data.scenario['effort-limit'], shift)
        areas = []
        for exe in executions:
            areas.append(self.calculateArea(exe['trajectory'], self.data.scenario['effort-limit'], shift))
        areas.sort()

        amount = 0
        for area in areas:
            if refArea > area: amount += 1
            else: break

        return 1 - (amount / len(executions))


    def aggressivenessToKeep(self, refExecution):
        effortCap = refExecution['trajectory'].getLastEffort()
        valueCap = refExecution['trajectory'].getResult()
        shift = -refExecution['bkv'][refExecution['instance-name']]
        maxArea = (self.data.scenario['effort-limit'] - effortCap) * (valueCap + shift)
        executions = self.data.getExecutions(refExecution['instance-id'], False, refExecution['id'] - 1)
        
        ratios = []
        for exe in executions:
            value = exe['trajectory'].getValue(effortCap)
            eMaxArea = (self.data.scenario['effort-limit'] - effortCap) * (value + shift)
            eRealArea = self.calculateArea(exe['trajectory'], self.data.scenario['effort-limit'], shift) - self.calculateArea(exe['trajectory'], effortCap, shift)
            if eMaxArea > 0: ratios.append(eRealArea / eMaxArea)
            else: ratios.append(1)
        medianRatio = statistics.median(ratios)
        estimatedArea = maxArea * medianRatio
        refArea = self.calculateArea(refExecution['trajectory'], effortCap, shift)
        refArea += estimatedArea
        
        if len(executions) == 0: return None
        areas = []
        for exe in executions:
            areas.append(self.calculateArea(exe['trajectory'], self.data.scenario['effort-limit'], shift))
        areas.sort()

        amount = 0
        for area in areas:
            amount += 1
            if area >= refArea: break

        return 1 - (amount / len(executions))


    def calculateArea(self, trajectory, finalEffort, shift = None):
        finalEffort = min(finalEffort, self.data.scenario['effort-limit'])
        if shift is None:
            shift = -self.data.getBkv()
        lastEffort = trajectory.points[0].effort
        lastValue = trajectory.points[0].value
        area = 0
        for point in trajectory.points[1:]:
            if point.effort <= finalEffort:
                x = point.effort - lastEffort
                y = (lastValue + shift)
                area += (x * y)
                lastEffort = point.effort
                lastValue = point.value
        x = finalEffort - lastEffort
        y = (lastValue + shift)
        area += (x * y)
        return area
