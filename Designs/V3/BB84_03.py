import numpy as np
import qit
from Crypto.Random import random
import copy

#Alice prepaing qubits
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
    # p = []
    # for m in encodedKey:
    #     p.append(m.measure()[1])
    # print(p)
    # print(bobsBases)
    # print(keyB)
    return keyB

#Alice sends bob their bases so they can discared bits where the basis they chose were different
def matchKeys(aliceBases, bobsBases, encodedKey, bobsRawKey):
    match = np.logical_not(np.logical_xor(aliceBases, bobsBases))
    keyAlice = [encodedKey[i] for i in range(len(encodedKey)) if match[i]]
    keyBob = [bobsRawKey[i] for i in range(len(bobsRawKey)) if match[i]]
    return keyAlice, keyBob

#Alice chooses random k/2 qubits to check the QBER which will be discared by both Alice and Bob
def checkKeys(keyAlice, keyBob):
    chosenQubits = []
    secureKeyBob = []
    secureKeyAlice = []
    while len(chosenQubits) < len(keyAlice) / 2:
        qubit = random.randint(0, len(keyAlice) - 1)
        if qubit not in chosenQubits:
            chosenQubits.append(qubit)
    qberCheckAlice = []
    qberCheckBob = []
    for i in range(len(chosenQubits)):
        qberCheckAlice.append(keyAlice[chosenQubits[i]])
        qberCheckBob.append(keyBob[chosenQubits[i]])
    for i in range(len(keyAlice)):
        if i not in chosenQubits:
            secureKeyAlice.append(bool(keyAlice[i].measure()[1]))
            secureKeyBob.append(keyBob[i])
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
def calculateErrorRate(distance):
    #Channel loss due to distance
    #https://www.lasercalculator.com/gain-loss-calculator/
    #https://www.fields.utoronto.ca/programs/scientific/04-05/quantumIC/abstracts/lo.pdf
    powerIn = 0.2
    k = (1 - (10**(-0.21/10))) * powerIn
    k = k / powerIn
    errorRate = k * distance
    #Loss due to connectors
    k2 = (1 - (10**(-0.3/10))) * powerIn
    k2 = k2 / powerIn
    errorRate += k2 * 2
    #Loss due to dark count
    errorRate += 0.000000085
    return (0)

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
        if not bool(qberCheckAlice[i].measure()[1]) == qberCheckBob[i]:
            wrong += 1
    return (wrong / totalQubits)