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

#Prepare basis
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
    secureKeyAlice = []
    secureKeyBob = []
    checkKeyAlice = []
    checkKeybob = []
    for i in range(len(secureKeyAliceTemp)):
        if i % 2==0:
            secureKeyAlice.append(secureKeyAliceTemp[i])
            secureKeyBob.append(secureKeyBobTemp[i])
        else:
            checkKeyAlice.append(secureKeyAliceTemp[i])
            checkKeybob.append(secureKeyBobTemp[i])
    return secureKeyAlice, secureKeyBob, checkKeyAlice, checkKeybob

#Calculate QBER
def calcualteQBER(secureAliceKey, secureBobKey):
    wrong = 0
    for i in range(len(secureAliceKey)):
        if secureAliceKey[i] == secureBobKey[i]:
            wrong += 1
    if len(secureAliceKey) > 0:
        return(wrong / len(secureAliceKey))
    return(0)

#Calcualte the error rate depedning on the distance
def calculateErrorRate(distance):
    #Loss due to distance
    powerIn = 0.2
    k = (1 - (10**(-0.21/10))) * powerIn
    k = k / powerIn
    errorRate = k * distance
    #Loss due to connectors
    k2 = (1 - (10**(-0.3/10))) * powerIn
    k2 = k2 / powerIn
    errorRate += k2 * 2
    #Splice loss ever 4km
    if distance % 4 == 0:
        k3 = (1 - (10**(-0.03/10))) * powerIn
        k3 = k3 / powerIn
        errorRate += k3
    #Loss due to dark count
    errorRate += 0.000000085
    return (errorRate)
    #Loss due to dark count
    #https://www.science.org/doi/10.1126/sciadv.1500793
    errorRate += 0.00005
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