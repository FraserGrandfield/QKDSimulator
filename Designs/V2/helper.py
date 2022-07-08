from email.mime import base
import importlib
from sre_parse import State
from turtle import color
import numpy as np
import qit
from Crypto.Random import random
import math
import matplotlib.pyplot as plt

def equivalentState(state1, state2):
    return np.array_equal(state1.prob(), state2.prob())

def getRandomBits(numberOfBits):
    bits = []
    for i in range(numberOfBits):
        bits.append(random.choice([True, False]))
    return bits

def calculateErrorRate(distance):
    errorRate = (distance * distance) / (1500 * 1500) 
    return (errorRate)

def addNoise(encodedKey, errorRate):
    sentEncodedKey = encodedKey.copy()
    for i in range(len(sentEncodedKey)):
        p = np.random.random_sample()
        if p < errorRate:
            if equivalentState(encodedKey[i], qit.state.State('0')) or equivalentState(sentEncodedKey[i], qit.state.State('1')):
                sentEncodedKey[i] = sentEncodedKey[i].u_propagate(qit.sx)
            else:
                sentEncodedKey[i] = sentEncodedKey[i].u_propagate(qit.sz)
    return sentEncodedKey

def calcualteQBER(qberCheckAlice, qberCheckBob):
    wrong = 0
    totalQubits = len(qberCheckAlice)
    if totalQubits < 1:
        return 0
    for i in range(totalQubits):
        if not bool(qberCheckAlice[i].measure()[1]) == qberCheckBob[i]:
            wrong += 1
    return ((wrong / totalQubits) * 100)
    
def drawGraph(x, y, keySize, type):
    plt.clf()
    plt.plot(x, y)
    plt.grid(True)
    plt.savefig(type + str(keySize) + ".png")

def drawComparisonGraphQBER(distances, e91Qbers, bb84Qbers, keySize, type):
    plt.clf()
    plt.plot(distances, e91Qbers)
    plt.plot(distances, bb84Qbers)
    plt.grid(True)
    plt.savefig(type + str(keySize) + ".png")