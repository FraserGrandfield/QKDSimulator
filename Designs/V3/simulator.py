import argparse
import BB84_03
import helper_03
import E91_03

keySizes = []

distances = []
measurmentsBB84QBER = []
measurmentsE91QBER = []

def main():

    parser = argparse.ArgumentParser(description="QKD simulator")
    parser.add_argument("-v", "--verbose", help="Print verbose", action="store_true")
    parser.add_argument("-d", "--distance", help="Max distance to inciment up too", type=int, default=2000)
    parser.add_argument("-ks", "--keySizes", help="Space seperated list of key sizes to simulate", nargs="+", type=int, default=[128, 256])
    global args
    args = parser.parse_args()

    createDistances()
    addKeys()
    runBB84()
    runE91()
    analysis()

def runBB84():
    for keySize in keySizes:
        qbers = []
        secureKeySizes = []
        for distance in distances:
            #Alice generates random bits to be encoded
            alicesRawKey = BB84_03.getRandomBits(keySize)
            #Alice chooses which basis to use
            aliceBases = BB84_03.getRandomBits(keySize)
            #Alice preparing qubits
            alicesEncodedKey = BB84_03.encodeKey(alicesRawKey, aliceBases)
            #Calcualte the error rate depedning on the distance
            errorRate = BB84_03.calculateErrorRate(distance)
            #Add noise the the encoded key
            sentEncodedKey = BB84_03.addNoise(alicesEncodedKey, errorRate)
            #Bob prepares random basis
            bobsBases = BB84_03.getRandomBits(keySize)
            #Bob measures the qubits sent by Alice
            bobsRawKey = BB84_03.measureQubits(sentEncodedKey, bobsBases)
            #Alice sends bob their bases so they can discared basis they chose differently
            keyAlice, keyBob = BB84_03.matchKeys(aliceBases, bobsBases, alicesEncodedKey, bobsRawKey)
            #Alice chooses random k/2 qubits to check the QBER
            qberCheckAlice, qberCheckBob, secureKeyAlice, secureKeyBob = BB84_03.checkKeys(keyAlice, keyBob)
            #Calcualte QBER
            qber = BB84_03.calcualteQBER(qberCheckAlice, qberCheckBob)
            secureKey = BB84_03.errorCorrection(secureKeyAlice, secureKeyBob)
            print("Key size: " + str(keySize) + " Distance: " + str(distance) + " QBER: " + str(qber))
            print("Length: " + str(len(secureKey)))
            qbers.append(qber)
            secureKeySizes.append(len(secureKey))
        helper_03.drawGraph(distances, secureKeySizes, keySize, "SecureKey_BB84_")
        helper_03.drawGraph(distances, qbers, keySize, "QBER_BB84_")
        measurmentsBB84QBER.append(qbers)

def runE91():
    for keySize in keySizes:
        qbers = []
        secureKeySizes = []
        for distance in distances:
            aliceBasis, bobBasis, aliceChoices, bobChoices = E91_03.chooseBasis(keySize)
            aliceRotations = E91_03.prepareBasis(aliceBasis)
            bobRotations = E91_03.prepareBasis(bobBasis)
            rawKeyAlice, rawKeyBob, checkKeyAlice, checkKeyBob = E91_03.measure(aliceRotations, bobRotations, aliceChoices, bobChoices)
            rawKeyAliceNoise = E91_03.addNoise(rawKeyAlice, distance)
            checkKeyAliceNoise = E91_03.addNoise(checkKeyAlice, distance)
            qber = E91_03.calcualteQBER(checkKeyAliceNoise, checkKeyBob)
            qbers.append(qber)
            secureKey = E91_03.errorCorrection(rawKeyAliceNoise, rawKeyBob)
            secureKeySizes.append(len(secureKey))
            print("length of secure key: " + str(len(secureKey)))
        helper_03.drawGraph(distances, secureKeySizes, keySize, "SecureKey_E91_")
        helper_03.drawGraph(distances, qbers, keySize, "QBER_E91_")
        measurmentsE91QBER.append(qbers)

def analysis():
    keySizeCounter = 0
    for i in range(len(measurmentsBB84QBER)):
        helper_03.drawComparisonGraphQBER(distances, measurmentsE91QBER[i], measurmentsBB84QBER[i], keySizeCounter, "QBER_comparison_")
        keySizeCounter += 1
        if keySizeCounter > 8:
            keySizeCounter = 0

def createDistances():
    for i in range(20, args.distance, 20):
        distances.append(i)

def addKeys():
    for key in args.keySizes:
        keySizes.append(key)

if __name__ == '__main__':
    main()