from sre_parse import State
from turtle import distance
import numpy as np
import qit
import numpy.random as npr
from math import pi
from numpy import *

#Alice and bob both randomly choose basis.
def chooseBasis(keySize):
    choicesAlice = [0, pi/8, pi/4]
    choicesBob = [0, pi/8, -pi/8]
    aliceBasis = []
    bobBasis = []
    aliceChoices = npr.random_integers(0, 2, keySize)
    bobChoices = npr.random_integers(0, 2, keySize)
    for i in range(keySize):
        aliceBasis.append(choicesAlice[aliceChoices[i]])
        bobBasis.append(choicesBob[bobChoices[i]])
    return aliceBasis, bobBasis, aliceChoices, bobChoices

#Alice prepares their basis
def prepareBasis(basis):
    identityOp = array([[1,0],[0,1]])
    rotations = []
    for base in basis:
        rotation = qit.utils.R_nmr(base, np.pi/2)
        rotation = kron(rotation, identityOp)
        rotations.append(rotation)
    return rotations

#Alice and Bob measure the entangled particles to get their raw key and key to check qber
def measure(aliceRotations, bobRotations, aliceChoices, bobChoices):
    secureKeyAliceTemp = []
    secureKeyBobTemp = []
    for i in range(len(aliceRotations)):
        collapsedState = qit.state.State('bell3')
        aliceP, aliceRes, collapsedState = collapsedState.u_propagate(aliceRotations[i]).measure((0,), do = 'C')
        if (aliceChoices[i] == 1 & bobChoices[i] == 0) | (aliceChoices[i] == 2 & bobChoices[i] == 2):
            secureKeyAliceTemp.append(aliceRes)
        bobP, bobRes, finalState = collapsedState.u_propagate(bobRotations[i]).measure((1,), do = 'C')
        if (aliceChoices[i] == 1 & bobChoices[i] == 0) | (aliceChoices[i] == 2 & bobChoices[i] == 2):
            secureKeyBobTemp.append(bobRes)
    chosenIndex = []
    secureKeyAlice = []
    secureKeyBob = []
    checkKeyAlice = []
    checkKeybob = []
    while len(chosenIndex) < len(secureKeyAliceTemp) / 2:
        if len(secureKeyAliceTemp) > 1:
            qubit = random.randint(0, len(secureKeyAliceTemp) - 1)
            if qubit not in chosenIndex:
                chosenIndex.append(qubit)
        else:
            chosenIndex.append(0)
    for i in range(len(chosenIndex)):
        checkKeyAlice.append(secureKeyAliceTemp[chosenIndex[i]])
        checkKeybob.append(secureKeyBobTemp[chosenIndex[i]])
    for i in range(len(secureKeyAliceTemp)):
        if i not in chosenIndex:
            secureKeyAlice.append(secureKeyAliceTemp[i])
            secureKeyBob.append(secureKeyBobTemp[i])
    return secureKeyAlice, secureKeyBob, checkKeyAlice, checkKeybob

#Calculate QBER
def calcualteQBER(secureAliceKey, secureBobKey):
    wrong = 0
    for i in range(len(secureAliceKey)):
        if secureAliceKey[i] == secureBobKey[i]:
            wrong += 1
    if len(secureAliceKey) > 0:
        return((wrong / len(secureAliceKey)) * 100)
    return(0)

#Calcualte the error rate depedning on the distance
def calculateErrorRate(distance):
    #Loss due to distance
    errorRate = 0.02 * (distance / 30)
    #Loss due to connectors
    errorRate += 0.11 * 2
    #Loss due to dark count
    errorRate += 0.30
    return (errorRate)

#Simulate adding noise to keys
def addNoise(key, distance):
    errorRate = calculateErrorRate(distance)
    keyOut = []
    for qubit in key:
        p = np.random.random_sample()
        if p < errorRate:
            if qubit == 1:
                keyOut.append(0)
            else:
                keyOut.append(1)
        else:
            keyOut.append(qubit)
    return keyOut

#Perform error correction so they both have the same secure key
def errorCorrection(rawKeyAlice, rawKeyBob):
    secureKey = []
    for i in range(len(rawKeyAlice)):
        if not rawKeyAlice[i] == rawKeyBob[i]:
            secureKey.append(rawKeyAlice[i])
    return secureKey