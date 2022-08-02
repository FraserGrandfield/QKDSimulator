from email.mime import base
import importlib
from sre_parse import State
from turtle import color
import numpy as np
import qit
import math
import matplotlib.pyplot as plt
import csv

#Draw a graph comparing meausrments from both protocols
def drawComparisonGraph(distances, e91Measurements, bb84Measurements, keySize, type, xAxis, yAxis):
    plt.clf()
    plt.plot(distances, e91Measurements, label="E91")
    plt.plot(distances, bb84Measurements, label="BB84")
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.grid(True)
    plt.legend()
    plt.savefig(type + str(keySize) + ".png")

#Save a measurement
def saveMeasurement(dic, measurments, key):
    if key in dic.keys():
        for i in range(len(measurments)):
            dic[key][i] = dic[key][i] + measurments[i]
    else:
        dic[key] = []
        for i in range(len(measurments)): 
            dic[key].append(measurments[i])

#Calculate what percentage to step up the status of how much progress the simulator has completed
def calcualateStatusStep(noOfKeys, noOfRunTimes):
    total = noOfKeys * noOfRunTimes * 2
    return (100 / total)

#Create a csv file to display the measurement values
def createCSV(distances, e91Measurements, bb84Measurements, keySize, type):
    header = ["distance", "BB84", "E91"]
    with open(type + str(keySize) + ".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range(len(distances)):
            row = []
            row.append(distances[i])
            row.append(bb84Measurements[i])
            row.append(e91Measurements[i])
            writer.writerow(row)