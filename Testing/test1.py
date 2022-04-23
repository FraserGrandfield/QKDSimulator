from email.mime import base
import importlib
from sre_parse import State
import numpy as np
import qit
from Crypto.Random import random

numBits = 128
errorRate = 0.2

def equivalentState(state1, state2):
    return np.array_equal(state1.prob(), state2.prob())

def getRandomBits(numberOfBits):
    bits = []
    for i in range(numBits):
        bits.append(random.choice([True, False]))
    return bits

#Alice generates random bits to be encoded
rawKey = getRandomBits(numBits)
print("Alice generates random bits to be encoded")
print(rawKey)

#Alice chooses which basis to use
basesA = getRandomBits(numBits)
print("Alice chooses basis to use")
print(basesA)

#Alice prepaing qubits
encodedKey = []
for i in range(len(rawKey)):
    q = qit.state.State('0')
    if rawKey[i]:
        q = q.u_propagate(qit.sx)
    if basesA[i]:
        q = q.u_propagate(qit.H)
    encodedKey.append(q)
print("Alice prepares qubits")
print(encodedKey)

#Introduce error noise
for i in range(len(encodedKey)):
    p = np.random.random_sample()
    if p < errorRate:
        if equivalentState(encodedKey[i], qit.state.State('0')) or equivalentState(encodedKey[i], qit.state.State('1')):
            encodedKey[i] = encodedKey[i].u_propagate(qit.sx)
        else:
            encodedKey[i] = encodedKey[i].u_propagate(qit.sz)
print("Introducing noise")
print(encodedKey)

#Bob prepares random basis
basesB = getRandomBits(numBits)
print("Bob prepares random basis")
print(basesB)

#Bob measures each qubit using the basis
keyB = []
for i in range(numBits):
    if basesB[i]:
        encodedKey[i] = encodedKey[i].u_propagate(qit.H)
    result = encodedKey[i].measure()
    keyB.append(bool(result[1]))
print("Bob measures each qubit with basis")
print(keyB)

match = np.logical_not(np.logical_xor(basesA, basesB))
keyAlice = [encodedKey[i] for i in range(len(encodedKey)) if match[i]]
keyBob = [keyB[i] for i in range(len(keyB)) if match[i]]
print("Both alice and bob discard bits if they do not match the basis they used")
print(keyAlice)
print(keyBob)