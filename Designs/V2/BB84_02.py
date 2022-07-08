import numpy as np
import qit
from Crypto.Random import random

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

#Bob measures each qubit using the basis
def measureQubits(encodedKey, bobsBases):
    keyB = []
    for i in range(len(encodedKey)):
        if bobsBases[i]:
            encodedKey[i] = encodedKey[i].u_propagate(qit.H)
        result = encodedKey[i].measure()
        keyB.append(bool(result[1]))
    return keyB

def matchKeys(aliceBases, bobsBases, encodedKey, bobsRawKey):
    match = np.logical_not(np.logical_xor(aliceBases, bobsBases))
    keyAlice = [encodedKey[i] for i in range(len(encodedKey)) if match[i]]
    keyBob = [bobsRawKey[i] for i in range(len(bobsRawKey)) if match[i]]
    return keyAlice, keyBob

def checkKeys(keyAlice, keyBob):
    chosenQubits = []
    secureKeyBob = []
    secureKeyAlice = []
    while len(chosenQubits) < len(keyAlice) / 5:
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
            secureKeyAlice.append(bool(keyAlice[i].measure()))
            secureKeyBob.append(keyBob[i])
    return qberCheckAlice, qberCheckBob, secureKeyAlice, secureKeyBob

def errorCorrection(secureKeyAlice, secureKeyBob):
    finalSecureKey = []
    for i in range(len(secureKeyAlice)):
        if secureKeyAlice[i] == secureKeyBob[i]:
            finalSecureKey.append(secureKeyAlice[i])
    return finalSecureKey