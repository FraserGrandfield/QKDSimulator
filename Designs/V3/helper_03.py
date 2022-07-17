from email.mime import base
import importlib
from sre_parse import State
from turtle import color
import numpy as np
import qit
from Crypto.Random import random
import math
import matplotlib.pyplot as plt
import csv

def drawGraph(x, y, keySize, type):
    plt.clf()
    plt.plot(x, y)
    plt.grid(True)
    plt.savefig(type + str(keySize) + ".png")

def drawComparisonGraph(distances, e91Measurements, bb84Measurements, keySize, type, xAxis, yAxis):
    plt.clf()
    plt.plot(distances, e91Measurements, label="E91")
    plt.plot(distances, bb84Measurements, label="BB84")
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.grid(True)
    plt.legend()
    plt.savefig(type + str(keySize) + ".png")

def saveMeasurement(dic, measurments, key):
    if key in dic.keys():
        for i in range(len(measurments)):
            dic[key][i] = dic[key][i] + measurments[i]
    else:
        dic[key] = []
        for i in range(len(measurments)): 
            dic[key].append(measurments[i])

def calcualateStatusStep(noOfKeys, noOfRunTimes):
    total = noOfKeys * noOfRunTimes * 2
    return (100 / total)

def createCSV(distances, e91Measurements, bb84Measurements, keySize, type):
    with open(type + str(keySize) + ".csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(distances)
        writer.writerow(e91Measurements)
        writer.writerow(bb84Measurements)