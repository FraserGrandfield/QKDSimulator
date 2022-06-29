from email.mime import base
import importlib
from sre_parse import State
import numpy as np
import qit
from Crypto.Random import random

def equivalentState(state1, state2):
    return np.array_equal(state1.prob(), state2.prob())

def getRandomBits(numberOfBits):
    bits = []
    for i in range(numberOfBits):
        bits.append(random.choice([True, False]))
    return bits

def AddNoise(encodedKey, errorRate):
    for i in range(len(encodedKey)):
        p = np.random.random_sample()
        if p < errorRate:
            if equivalentState(encodedKey[i], qit.state.State('0')) or equivalentState(encodedKey[i], qit.state.State('1')):
                encodedKey[i] = encodedKey[i].u_propagate(qit.sx)
            else:
                encodedKey[i] = encodedKey[i].u_propagate(qit.sz)
    print("Introducing noise")
    print(encodedKey)