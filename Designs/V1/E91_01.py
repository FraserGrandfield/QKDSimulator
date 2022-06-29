from email.mime import base
from math import pi, cos, sqrt
import importlib
from sre_parse import State
import numpy as np
import qit
from Crypto.Random import random

numBits = 128
#Introduce an error rate
errorRate = 0

#Trusted mediator generates pairs of entangled particles and sends one of each to Bob and Alice
#Alice randomly offsets her axis of measurmeent by one of the following [0, pi/8, pi/4]
#Bob randomly offsets her axis of measurmeent by one of the following [0, pi/8, -pi/4]
choicesA = [0, pi/8, pi/4]
choicesB = [0, pi/8, -pi/8]
basesA = []
basesB = []
for i in range(numBits):
    basesA.append(random.choice(choicesA))
    basesB.append(random.choice(choicesB))

keyA = []
keyB = []

#Alice and Bob's measurement results on a pair of entangled qubits
for i in range (numBits):
    #Alice measures either basis state with equal probability -1 will correspond to False (0) and +1 will correspond to True (1)
    resultA = random.choice([-1, 1])

    r = -1 * cos(2 * (basesA[i] - basesB[i]))
    r2 = r ** 2
    ve = 1 - r2
    SD = sqrt(ve)
    e = np.random.normal(0, SD)
    resultB = resultA * r + e

    resultA = False if resultA < 0 else True
    resultB = False if resultB < 0 else True

    if errorRate:
        samples = np.random.rand(2)
        if samples[0] < errorRate:
            resultA = not(resultA)
        if samples[1] < errorRate:
            resultB = not(resultB)

    keyA.append(resultA)
    keyB.append(resultB)

print("Alices chosen axies")
print(basesA)
print("Bobs chosen axies")
print(basesB)
print("Alices measurement results")
print(keyA)
print("Bobs measurement results")
print(keyB)

#Remove bits from raw key where Bob and Alice choose different axies
match = [True if basesA[i] == basesB[i] else False for i in range(len(basesA))]
finalKeyA = [keyA[i] for i in range(len(keyA)) if match[i]]
finalKeyB = [not(keyB[i]) for i in range(len(keyB)) if match[i]]

print("Alices final key")
print(finalKeyA)
print("Bobs final key")
print(finalKeyB)