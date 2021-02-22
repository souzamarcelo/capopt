#!/usr/bin/python3
import os
import sys
import datetime
import time
from ast import literal_eval
import rpy2.robjects as robjects

from classes import Point
from classes import Trajectory

estimationRun = False

scenarioAttributes = [
    {'name':'executable',           'type':'str',       'default':None},
    {'name':'fixed-params',         'type':'str',       'default':''},
    {'name':'instance-command',     'type':'str',       'default':''},
    {'name':'seed-command',         'type':'str',       'default':''},
    {'name':'effort-limit-command', 'type':'str',       'default':''},
    {'name':'effort-limit',         'type':'int',       'default':60},
    {'name':'effort-type',          'type':'str',       'default':'time'},
    {'name':'capping',              'type':'boolean',   'default':True},
    {'name':'envelope',             'type':'str',       'default':'profile'},
    {'name':'strategy',             'type':'str',       'default':'elitist'},
    {'name':'penalty',              'type':'str',       'default':'best-so-far'},
    {'name':'sel-elites',           'type':'str',       'default':'elites'},
    {'name':'ag',                   'type':'float',     'default':0.4},
    {'name':'epsilon',              'type':'float',     'default':0.05},
    {'name':'ar',                   'type':'str',       'default':'exp'},
    {'name':'ac',                   'type':'str',       'default':'worst'},
    {'name':'p',                    'type':'float',     'default':0.1},
    {'name':'alpha',                'type':'int',       'default':10},
    {'name':'budget-type',          'type':'str',       'default':'executions'},
    {'name':'external-halt',        'type':'boolean',   'default':False}
]

executionAttributes = [
    {'name':'id',                       'type':'int'},
    {'name':'candidate-id',             'type':'int'},
    {'name':'candidate-desc',           'type':'str'},
    {'name':'instance-id',              'type':'int'},
    {'name':'instance-name',            'type':'str'},
    {'name':'seed',                     'type':'int'},
    {'name':'iteration',                'type':'int'},
    {'name':'start-datetime',           'type':'str'},
    {'name':'stop-datetime',            'type':'str'},
    {'name':'start-timestamp',          'type':'float'},
    {'name':'stop-timestamp',           'type':'float'},
    {'name':'execution-time',           'type':'float'},
    {'name':'total-time',               'type':'float'},
    {'name':'execution-effort',         'type':'float'},
    {'name':'total-effort',             'type':'float'},
    {'name':'status',                   'type':'str'},
    {'name':'irace-elites',             'type':'literal'},
    {'name':'trajectory',               'type':'trajectory'},
    {'name':'envelope',                 'type':'envelope'},
    {'name':'max-area',                 'type':'float'},
    {'name':'exec-area',                'type':'float'},
    {'name':'aggressiveness',           'type':'float'},
    {'name':'bkv',                      'type':'literal'}
]

class Data:
    def __init__(self, _candidateId, _candidateDesc, _instanceId, _instanceName, _seed, _estimationRun):
        self.estimationRun = _estimationRun
        self.previousExecutions = []
        self.execution = {}
        self.scenario = {}
        self.prepareScenario(_instanceName)
        if not self.estimationRun: self.prepareExecutions(_candidateId, _candidateDesc, _instanceId, _instanceName, _seed)
        else: self.prepareEstimationRun(_candidateId, _candidateDesc, _instanceId, _instanceName, _seed)


    def prepareExecutions(self, _candidateId, _candidateDesc, _instanceId, _instanceName, _seed):
        if not os.path.isfile("data.txt"):
            header = ""
            for item in executionAttributes:
                header += item['name'] + ";"
            header = header[:-1] + "\n"
            dataFile = open("data.txt", "w")
            dataFile.write(header)
            dataFile.close()

        dataFile = open("data.txt", "r")
        lines = dataFile.readlines()
        for i in range(len(lines)):
            line = lines[i].replace("\n", "")
            content = line.split(";")
            if i == 0: header = content
            else:
                execution = {}
                for j in range(len(header)):
                    item = next(attribute for attribute in executionAttributes if attribute['name'] == header[j])
                    value = content[j]
                    if item['type'] == 'int': value = (int(value) if value.isdigit() else value)
                    if item['type'] == 'float': value = (float(value) if self.isfloat(value) else value)
                    if item['type'] == 'literal': value = literal_eval(value)
                    if item['type'] == 'trajectory': value = self.getTrajectoryFromString(value, execution['instance-id'], execution['candidate-id'], execution['seed'])
                    if item['type'] == 'envelope': value = (self.getTrajectoryFromString(value, execution['instance-id'], 0, 0) if "[" in value else value)
                    execution[item['name']] = value
                self.previousExecutions.append(execution)

        _instanceName = self.cleanInstance(_instanceName)
        for item in executionAttributes:
            self.execution[item['name']] = None
        self.execution['id'] = (self.previousExecutions[-1]['id'] + 1 if len(self.previousExecutions) > 0 else 1)
        self.execution['candidate-id'] = _candidateId
        self.execution['candidate-desc'] = _candidateDesc
        self.execution['instance-id'] = _instanceId
        self.execution['instance-name'] = _instanceName
        self.execution['seed'] = _seed
        self.execution['iteration'] = self.readIteration()
        self.execution['start-datetime'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.execution['start-timestamp'] = time.time()
        self.execution['irace-elites'] = self.readLastIterationElites(self.execution['iteration'])
        self.execution['aggressiveness'] = (self.previousExecutions[-1]['aggressiveness'] if len(self.previousExecutions) > 0 else "NA")
        self.execution['bkv'] = (self.previousExecutions[-1]['bkv'] if len(self.previousExecutions) > 0 else {})
        if _instanceName not in self.execution['bkv']: self.execution['bkv'][_instanceName] = float("inf")

    
    def prepareScenario(self, instanceName):
        for item in scenarioAttributes:
            self.scenario[item['name']] = self.readParameter(item['name'], item['type'], item['default'])
        if self.scenario['effort-limit'] == 0: self.scenario['effort-limit'] = self.getDynamicEffortLimit(instanceName)


    def prepareEstimationRun(self, _candidateId, _candidateDesc, _instanceId, _instanceName, _seed):
        _instanceName = self.cleanInstance(_instanceName)
        for item in executionAttributes:
            self.execution[item['name']] = None
        self.execution['candidate-id'] = _candidateId
        self.execution['candidate-desc'] = _candidateDesc
        self.execution['instance-id'] = _instanceId
        self.execution['instance-name'] = _instanceName
        self.execution['seed'] = _seed
        self.scenario['capping'] = False
        
    
    def finish(self, executionEffort, status, trajectory, capping):
        if self.estimationRun: return

        self.execution['stop-datetime'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.execution['stop-timestamp'] = time.time()
        self.execution['execution-time'] = (self.execution['stop-timestamp'] - self.execution['start-timestamp'])
        self.execution['total-time'] = ((self.execution['stop-timestamp'] - self.previousExecutions[0]['start-timestamp']) if len(self.previousExecutions) > 0 else (self.execution['stop-timestamp'] - self.execution['start-timestamp']))
        self.execution['execution-effort'] = executionEffort
        self.execution['total-effort'] = (self.execution['execution-effort'] + self.previousExecutions[-1]['total-effort'] if len(self.previousExecutions) > 0 else self.execution['execution-effort'])
        self.execution['status'] = status
        self.execution['trajectory'] = trajectory

        values = capping.report(trajectory) if self.scenario['capping'] else {'envelope':'NA', 'max-area':'NA', 'exec-area':'NA'}
        self.execution['envelope'] = values['envelope']
        self.execution['max-area'] = values['max-area']
        self.execution['exec-area'] = values['exec-area']
        self.execution['bkv'][self.execution['instance-name']] = min(self.execution['bkv'][self.execution['instance-name']], trajectory.getResult())
        self.saveExecution()
        

    def saveExecution(self):
        content = ""
        for item in executionAttributes:
            content += str(self.execution[item['name']]) + ";"
        content = content[:-1] + "\n"
        dataFile = open("data.txt", "a")
        dataFile.write(content)
        dataFile.close()
    
    
    def getAmountExecutionsLastIteration(self):
        if self.execution['iteration'] == 1: return None
        nbExecutions = 0
        nbCapping = 0
        for exe in self.previousExecutions:
            if exe['status'] != "infeasible":
                if exe['iteration'] == self.execution['iteration'] - 1:
                    nbExecutions += 1
                    if exe['status'] == "capped":
                        nbCapping += 1
        return nbExecutions, nbCapping


    def getBkv(self, _instanceName = None):
        if _instanceName is None: _instanceName = self.execution['instance-name']
        return self.execution['bkv'][_instanceName]


    def isNewIteration(self):
        return (True if len(self.previousExecutions) == 0 else self.previousExecutions[-1]['iteration'] < self.execution['iteration'])


    def getExecutionsOfLastIteration(self, capped):
        resultList = []
        for exe in self.previousExecutions:
            if exe['iteration'] == self.execution['iteration'] - 1:
                if exe['status'] != "infeasible":
                    if (capped and exe['status'] == "capped") or ((not capped) and exe['status'] == "ok"):
                        resultList.append(exe)
        return resultList
    
    
    def getExecutions(self, _instanceId, capped, maxExecId = float("inf")):
        resultList = []
        for exe in self.previousExecutions:
            if exe['status'] != "infeasible":
                if exe['instance-id'] == _instanceId and exe['id'] <= maxExecId:
                    if (capped and exe['status'] == "capped") or ((not capped) and exe['status'] == "ok"):
                        resultList.append(exe)
        return resultList


    def readIteration(self):
        if not os.path.isfile("irace.Rdata"): return 0
        robjects.r['load']("irace.Rdata")
        iteration = robjects.r('iraceResults$state$indexIteration')
        iteration = int(iteration[0])
        return iteration


    def readLastIterationElites(self, iteration):
        lastIteration = iteration - 1
        if lastIteration >= 1:
            robjects.r['load']("irace.Rdata")
            elites = robjects.r('iraceResults$allElites[[' + str(lastIteration) + ']]')
            result = []
            for e in elites:
                result.append(int(e))
            return result    
        else:
            return []


    def getTrajectoryFromString(self, description, instanceId, candidateId, seed):
        points = []
        description = description[1:-1]
        if len(description) > 0:
            content = description.split("/")
            for point in content:
                parts = point.split(",")
                effort = float(parts[0])
                value = float(parts[1])
                points.append(Point(effort, value))
        
        return Trajectory(candidateId, instanceId, seed, points)


    def readParameter(self, key, type, default):
        result = None
        paramFile = open(sys.path[0] + "/../parameters-capopt.txt", "r")
        for line in paramFile.readlines():
            line = line.replace("\n", "").strip()
            if line != "" and line[0] != "#":
                content = line.split(":")
                if content[0].strip() == key:
                    result = str(content[1]).strip()
                    break
        paramFile.close()
        if result == "" or result is None: return default
        if result.upper() == "TRUE": return True
        if result.upper() == "FALSE": return False
        if type == "int": return int(result)
        if type == "float": return float(result)
        return result.lower() if key != "executable" else result


    def cleanInstance(self, instance):
        return instance[instance.rindex("/") + 1:instance.rindex(".") if "." in instance else len(instance)]

    
    def isfloat(self, str):
        try:
            float(str)
            return True
        except ValueError:
            return False

    
    def getDynamicEffortLimit(self, instanceName):
        instanceName = self.cleanInstance(instanceName)
        effortFile = open("effort.txt", "r")
        for line in effortFile:
            line = line.replace('\n', '')
            content = line.split(':')
            if content[0] == instanceName:
                return int(content[1])
        print('Dynamic effort (file effort.txt) not found!')
        exit(1)
