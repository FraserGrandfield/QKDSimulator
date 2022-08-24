import numpy as np
import qit
import random
import copy

#Alice prepaing qubits
#Propagate the state a finite step in time using a propagator which is either a unitary Hilbert space or Liouville space propagator.
def encodeKey(rawKey, bases):
    encodedKey = []
    for i in range(len(rawKey)):
        q = qit.state.State('0')
        if rawKey[i]:
            q = q.u_propagate(qit.sx)
        if bases[i]:
            q = q.u_propagate(qit.H)
        encodedKey.append(q)
    return encodedKey

#Bob measures the qubits sent by Alice
def measureQubits(encodedKey, bobsBases):
    keyB = []
    for i in range(len(encodedKey)):
        if bobsBases[i]:
            encodedKey[i] = encodedKey[i].u_propagate(qit.H)
        result = encodedKey[i].measure()
        keyB.append(bool(result[1]))
    return keyB

#Alice sends bob their bases so they can discared bits where the basis they chose were different
def matchKeys(aliceBases, bobsBases, encodedKey, bobsRawKey):
    match = np.logical_not(np.logical_xor(aliceBases, bobsBases))
    keyAlice = [encodedKey[i] for i in range(len(encodedKey)) if match[i]]
    keyBob = [bobsRawKey[i] for i in range(len(bobsRawKey)) if match[i]]
    return keyAlice, keyBob

#Alice and Bob decided to use every other bit to be used to calcualte the QBER.
def checkKeys(keyAlice, keyBob):
    secureKeyBob = []
    secureKeyAlice = []
    qberCheckAlice = []
    qberCheckBob = []
    for i in range(len(keyAlice)):
        if i % 2 == 0:
            secureKeyAlice.append(keyAlice[i])
            secureKeyBob.append(keyBob[i])
        else:
            qberCheckAlice.append(keyAlice[i])
            qberCheckBob.append(keyBob[i])
    return qberCheckAlice, qberCheckBob, secureKeyAlice, secureKeyBob

#Perform error correction so they both have the same secure key
def errorCorrection(secureKeyAlice, secureKeyBob):
    finalSecureKey = []
    for i in range(len(secureKeyAlice)):
        if secureKeyAlice[i] == secureKeyBob[i]:
            finalSecureKey.append(secureKeyAlice[i])
    return finalSecureKey

#Checks if two states are the same
def equivalentState(state1, state2):
    return np.array_equal(state1.prob(), state2.prob())

#Gets random bits for the size of key or basis
def getRandomBits(numberOfBits):
    bits = []
    for i in range(numberOfBits):
        bits.append(random.choice([True, False]))
    return bits

#Calcualte the error rate depedning on the distance
def calculateErrorRate(distance, fiberloss):
    #Number of photons per pulse
    u = 0.1
    #Fiber losses [dB/km]
    a = fiberloss
    #Quantum efficiency of the single-photon detectors
    n = 0.07
    #Dark count probability
    pDark = 0.000005
    #Visability
    v = 0.98
    tlink = 10**((-a*distance)/10)
    popt = (1 - v) / 2
    errorRate = popt + (pDark / (2 * tlink * n * u))
    return (errorRate)

#Add noise the the encoded key
def addNoise(encodedKey, errorRate):
    sentEncodedKey = copy.deepcopy(encodedKey)
    for i in range(len(sentEncodedKey)):
        p = np.random.random_sample()
        if p < errorRate:
            if equivalentState(sentEncodedKey[i], qit.state.State('0')) or equivalentState(sentEncodedKey[i], qit.state.State('1')):
                sentEncodedKey[i] = sentEncodedKey[i].u_propagate(qit.sx)
            else:
                sentEncodedKey[i] = sentEncodedKey[i].u_propagate(qit.sz)
    return sentEncodedKey

#Calcualte QBER
def calcualteQBER(qberCheckAlice, qberCheckBob):
    wrong = 0
    totalQubits = len(qberCheckAlice)
    if totalQubits < 1:
        return 0
    for i in range(totalQubits):
        if not bool(qberCheckAlice[i]) == qberCheckBob[i]:
            wrong += 1
    return ((wrong / totalQubits) * 100)