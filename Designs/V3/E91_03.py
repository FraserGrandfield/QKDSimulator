import numpy as np
import qit
import numpy.random as npr
from math import pi
from numpy import *

#Alice and bob both randomly choose basis.
def chooseBasis(keySize):
    #Alice basis choices.
    choicesAlice = [0, pi/8, pi/4]
    #Bob baisis choices.
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
    #Identity matix
    identityOp = array([[1,0],[0,1]])
    rotations = []
    for base in basis:
        #One-qubit rotation by the angle defined by the base
        rotation = qit.utils.R_nmr(base, np.pi/2)
        #Calcualates the Kronecker product of two arrays.
        rotation = kron(rotation, identityOp)
        rotations.append(rotation)
    return rotations

#Alice and Bob measure the entangled particles to get their raw key and key to check qber. They also perfrom key sifting.
def measure(aliceRotations, bobRotations, aliceChoices, bobChoices):
    secureKeyAliceTemp = []
    secureKeyBobTemp = []
    for i in range(len(aliceRotations)):
        #Create a pair of entangled particles in Bell state 3
        collapsedState = qit.state.State('bell3')
        #Alice measures first of the entagled particles.
        aliceP, aliceRes, collapsedState = collapsedState.u_propagate(aliceRotations[i]).measure((0,), do = 'C')
        if (aliceChoices[i] == 0 & bobChoices[i] == 0) | (aliceChoices[i] == 1 & bobChoices[i] == 1):
            secureKeyAliceTemp.append(aliceRes)
        #Bob measures the second of the entagled particles.
        bobP, bobRes, finalState = collapsedState.u_propagate(bobRotations[i]).measure((1,), do = 'C')
        if (aliceChoices[i] == 0 & bobChoices[i] == 0) | (aliceChoices[i] == 1 & bobChoices[i] == 1):
            secureKeyBobTemp.append(bobRes)
    secureKeyAlice = []
    secureKeyBob = []
    checkKeyAlice = []
    checkKeybob = []
    #Alice and Bob decided to use every other bit to be used to calcualte the QBER.
    for i in range(len(secureKeyAliceTemp)):
        if i % 2 == 0:
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
        #Qubits are wrong if they are the same because the measurment resualts are anticorrelated.
        if secureAliceKey[i] == secureBobKey[i]:
            wrong += 1
    if len(secureAliceKey) > 0:
        return((wrong / len(secureAliceKey)) * 100)
    return(0)

#Calcualte the error rate depedning on the distance.
def calculateErrorRate(distance, fiberLoss):
    #Coincidence rate.
    c0 = 9000
    #Accidential coincidence rate.
    a0 = 240
    #Fiber losses [dB/km]
    a = fiberLoss
    #Dark count per InGaAs detector.
    d = 80
    cl = c0 * 10**((-a * distance) / 10)
    al = a0 * 10**((-a * distance) / 10)
    errorRate = ((al + d) / (((2 * cl) + al) + (al + d)))
    return (errorRate)

#Simulate adding noise to keys
def addNoise(key, errorRate):
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