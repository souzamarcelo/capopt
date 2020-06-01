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
    instanceId = int(sys.argv[2])
    seed = int(sys.argv[3])
    instanceName = sys.argv[4]
    candidateDescList = sys.argv[5:]
    
    candidateDesc = ""
    for item in candidateDescList:
        candidateDesc += item + " "
    candidateDesc = candidateDesc[:-1]
    
    data = Data(candidateId, candidateDesc, instanceId, instanceName, seed)
    
    if data.scenario['capping']:
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
            point = parseOutput(output, time.time() - startTime, readOutput)
            if point is not None:
                trajectory.addPoint(point, data.scenario['effort-limit'])
        executionEffort = max(executionEffort, (time.time() - startTime if data.scenario['effort-type'] == "time" else point.effort if point is not None else trajectory.getLastEffort() if not trajectory.isEmpty() else 0))
        executionEffort = min(executionEffort, data.scenario['effort-limit'])

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
            point = parseOutput(output, time.time() - startTime, readOutput)
            if point is not None:
                trajectory.addPoint(point, data.scenario['effort-limit'])
                executionEffort = point.effort
        
        if data.scenario['budget-type'] == "timeout": print(str(trajectory.getResult()) + ' ' + str(time.time() - startTime))
        else: print(trajectory.getResult())
        result = "ok"
    elif status == 11:
        result = "capped"
        if data.scenario['penalty'] == "biggest":
            if data.scenario['budget-type'] == "timeout": print(str(sys.maxsize) + ' ' + str(time.time() - startTime))
            else: print(sys.maxsize)
        elif data.scenario['penalty'] == "best-so-far":
            if data.scenario['budget-type'] == "timeout": print(str(trajectory.getResult()) + ' ' + str(time.time() - startTime))
            else: print(trajectory.getResult())
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


def parseOutput(output, elapsedTime, readOutput):
    return defaultParseOutput(output, elapsedTime)
    #return spearParseOutput(readOutput)


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


def spearParseOutput(readOutput):
    readOutput.seek(0)
    content = readOutput.read()
    if "runtime" in content:
        if "UNKNOWN" in content:
            return Point(1000, 1000)
        else:
            runtime = float(content[content.index('runtime') + 8 : content.index('[s]') - 1])
            return Point(runtime, runtime)
    return None


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


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python target-runner.py <candidateId> <instanceId> <seed> <instance> <candParams>")
        exit(1)
    main()
