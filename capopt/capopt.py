#!/usr/bin/python3
import sys
import os
import shutil
import subprocess
import psutil
import time

from classes import Point
from classes import Trajectory
from capping import Capping
from data import Data

capping = None
data = None

def main():
    global capping, data
    
    candidateId = int(sys.argv[1])
    instanceId = sys.argv[2]
    seed = int(sys.argv[3])
    instanceName = sys.argv[4]
    candidateDescList = sys.argv[5:]
    
    candidateDesc = ""
    for item in candidateDescList:
        candidateDesc += item + " "
    candidateDesc = candidateDesc[:-1]
    
    data = Data(candidateId, candidateDesc, instanceId, instanceName, seed, (not os.path.isfile("irace.Rdata")))
    
    if data.scenario['capping'] and "t" not in instanceId:
        capping = Capping(data)
    
    command = "stdbuf -oL -e0 " + sys.path[0] + "/../" + data.scenario['executable']
    command += " " + data.scenario['instance-command']
    command += " " + instanceName
    if data.scenario['seed-command'] != "":
        command += " " + data.scenario['seed-command']
        command += " " + str(data.execution['seed'])
    if data.scenario['effort-limit-command'] != "":
        command += " " + data.scenario['effort-limit-command']
        command += " " + str(data.scenario['effort-limit'])
    if data.scenario['fixed-params'] != "":
        command += " " + data.scenario['fixed-params']    
    command += " " + data.execution['candidate-desc']

    runAlgorithm(command)


def runAlgorithm(command):
    global capping, data
    trajectory = Trajectory(data.execution['candidate-id'], data.execution['instance-id'], data.execution['seed'], [])
    startTime = time.time()
    status = None
   
    directory = "execution-c" + str(data.execution['candidate-id']) + "-i" + str(data.execution['instance-id']) + "-s" + str(data.execution['seed'])
    os.mkdir(directory)
    fileOutput = open(directory + "/tempOut.dat", "w+")
    fileError = open(directory + "/tempErr.dat", "w+")
    readOutput = open(directory + "/tempOut.dat", "r")

    process = subprocess.Popen(command, stdout = fileOutput, stderr = fileError, env = os.environ, shell = True)
    executionEffort = 0
    while process.poll() is None:
        output = readOutput.readlines()
        point = None
        if len(output) > 0:
            point = parseOutput(output, time.time() - startTime)
            if point is not None:
                trajectory.addPoint(point, data.scenario['effort-limit'])
        executionEffort = max(executionEffort, (time.time() - startTime if data.scenario['effort-type'] == "time" else point.effort if point is not None else trajectory.getLastEffort() if not trajectory.isEmpty() else 0))
        executionEffort = min(executionEffort, data.scenario['effort-limit'])

        if data.scenario['external-halt'] and executionEffort == data.scenario['effort-limit']:
            killProcess(process.pid)
            status = 0
            break

        if data.scenario['capping']:
            if capping.cap(executionEffort, trajectory):
                trajectory.addCappedPoint(Point(min(data.scenario['effort-limit'], executionEffort), trajectory.getResult()))
                killProcess(process.pid)
                status = 11
                break

        if data.scenario['effort-type'] == "time": time.sleep(0.5)

    if status is None:
        status = process.poll()
    
    if status == 0:
        output = readOutput.readlines()
        if len(output) > 0:
            point = parseOutput(output, time.time() - startTime)
            if point is not None:
                trajectory.addPoint(point, data.scenario['effort-limit'])
                executionEffort = point.effort
        result = "ok" if checkFeasibility(fileOutput) else "infeasible"
        value = trajectory.getResult() if result != "infeasible" else sys.maxsize
        if data.scenario['budget-type'] == "timeout" or data.estimationRun: print(str(value) + ' ' + str(time.time() - startTime))
        else: print(value)
    elif status == 11:
        result = "capped" if checkFeasibility(fileOutput) else "infeasible"
        value = trajectory.getResult() if (result == "capped" and data.scenario['penalty'] == "best-so-far") else sys.maxsize
        if data.scenario['budget-type'] == "timeout": print(str(value) + ' ' + str(time.time() - startTime))
        else: print(value)
    else:
        exit(status)
    
    fileOutput.close()
    fileError.close()    
    readOutput.close()
    shutil.rmtree(directory)

    data.finish(executionEffort, result, trajectory, capping)
            

def killProcess(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive = True):
            child.kill()
        parent.kill()
    except:
        pass


def parseOutput(output, elapsedTime):
    return defaultParseOutput(output, elapsedTime)
    #return scipParseOutput(output, elapsedTime)
    #return lkhParseOutput(output, elapsedTime)


def defaultParseOutput(output, elapsedTime):
    isTime = (data.scenario['effort-type'] == "time")
    index = len(output)
    valid = False
    while (not valid) and (index > 0):
        index -= 1
        content = output[index]
        valid = checkOutput(content, isTime)
    if not valid: return None
    
    content = str(content.strip())
    content = content.replace("b'", "")
    content = content.replace("'", "")
    if isTime:
        pEffort = round(elapsedTime, 1)
        pValue = float(content)
    else:
        content = content.split(";")
        pEffort = round(float(content[0]), 1)
        pValue = float(content[1])
    
    point = Point(pEffort, pValue)
    return point


def scipParseOutput(output, elapsedTime):
    point = None
    bestValue = float('inf')
    for line in output:
        if 's|' in line and '\n' in line:
            line = line.replace('\n', '').replace('*', '').strip()
            content = line.split('|')
            if len(content) == 2:
                value = float(line.split('|')[1])
                value = value * -1
                bestValue = min(bestValue, value)
    return Point(round(elapsedTime, 1), bestValue) if bestValue != float('inf') else None


def lkhParseOutput(output, elapsedTime):
    bestSoFar = float('inf')
    for line in reversed(output):
        if 'Cost = ' in line and 'Time = ' in line:
            bestSoFar = min(bestSoFar, int(line[line.index('Cost = ') + 7: line.index(', Time')]))
    return Point(round(elapsedTime, 1), bestSoFar) if bestSoFar != float('inf') else None


def checkOutput(output, isTime):
    if "\n" not in output: return False
    output = output.replace("\n", "")
    if isTime:
        if len(output) <= 0: return False
    else:
        if ";" not in output: return False
        output = output.split(";")
        if len(output[0]) <= 0: return False
        if len(output[1]) <= 0: return False
    return True


def checkFeasibility(fileOutput):
    fileOutput.seek(0)
    content = fileOutput.read()
    return not ("solution is not feasible" in content)


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python capopt.py <candidateId> <instanceId> <seed> <instance> <candParams>")
        exit(1)
    main()
