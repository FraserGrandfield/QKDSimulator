from email.mime import base
import importlib
from sre_parse import State
import numpy as np
import qit
from Crypto.Random import random
import math

def equivalentState(state1, state2):
    return np.array_equal(state1.prob(), state2.prob())

def getRandomBits(numberOfBits):
    bits = []
    for i in range(numberOfBits):
        bits.append(random.choice([True, False]))
    return bits

def calculateErrorRate(distance):
    return (math.sqrt(distance) / 100)

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
    for i in range(totalQubits):
        if not bool(qberCheckAlice[i].measure()[1]) == qberCheckBob[i]:
            wrong += 1
    return (wrong / totalQubits)
    
