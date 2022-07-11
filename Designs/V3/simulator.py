import argparse
import BB84_03
import helper_03
import E91_03

keySizes = []
distances = []

qberDict = {}
rawKeySizesDict = {}
secureKeySizesDict = {}

def main():

    parser = argparse.ArgumentParser(description="QKD simulator")
    parser.add_argument("-v", "--verbose", help="Print verbose", action="store_true")
    parser.add_argument("-d", "--distance", help="Max distance to inciment up too", type=int, default=2000)
    parser.add_argument("-ks", "--keySizes", help="Space seperated list of key sizes to simulate", nargs="+", type=int, default=[128, 256])
    parser.add_argument("-rt", "--runTimes", help="How many times to run the simulator to get an average", type=int, default=1)
    global args
    args = parser.parse_args()

    createDistances()
    addKeys()
    for i in range(args.runTimes):
        runBB84()
        runE91()
    analysisQBER()
    analysisRawKey()
    analysisSecureKey()

def runBB84():
    for keySize in keySizes:
        qbers = []
        rawKeySizes = []
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
            siftedRawKeyAlice, siftedRawKeyBob = BB84_03.matchKeys(aliceBases, bobsBases, alicesEncodedKey, bobsRawKey)
            #Alice chooses random k/2 qubits to check the QBER
            qberCheckAlice, qberCheckBob, secureKeyAlice, secureKeyBob = BB84_03.checkKeys(siftedRawKeyAlice, siftedRawKeyBob)
            #Calcualte QBER
            qber = BB84_03.calcualteQBER(qberCheckAlice, qberCheckBob)
            secureKey = BB84_03.errorCorrection(secureKeyAlice, secureKeyBob)
            print("Key size: " + str(keySize) + " Distance: " + str(distance) + " QBER: " + str(qber))
            print("Length: " + str(len(secureKey)))
            qbers.append(qber)
            rawKeySizes.append(len(siftedRawKeyAlice))
            secureKeySizes.append(len(secureKey))
        dictString = "BB84_" + str(keySize)
        helper_03.saveMeasurement(qberDict, qbers, dictString)
        helper_03.saveMeasurement(rawKeySizesDict, rawKeySizes, dictString)
        helper_03.saveMeasurement(secureKeySizesDict, secureKeySizes, dictString)

def runE91():
    for keySize in keySizes:
        qbers = []
        rawKeySizes = []
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
            rawKeySizes.append(len(rawKeyAlice) + len(checkKeyAlice))
            secureKeySizes.append(len(secureKey))
            print("length of secure key: " + str(len(secureKey)))
        dictString = "E91_" + str(keySize)
        helper_03.saveMeasurement(qberDict, qbers, dictString)
        helper_03.saveMeasurement(rawKeySizesDict, rawKeySizes, dictString)
        helper_03.saveMeasurement(secureKeySizesDict, secureKeySizes, dictString)

def analysisQBER():
    for keySize in keySizes:
        averageQBERBB84 = []
        averageQBERE91 = []
        for qber in qberDict["BB84_" + str(keySize)]:
            averageQBERBB84.append(qber / args.runTimes)
        for qber in qberDict["E91_" + str(keySize)]:
            averageQBERE91.append(qber / args.runTimes)
        helper_03.drawComparisonGraph(distances, averageQBERE91, averageQBERBB84, keySize, "QBER_Comparison", "Distance (M)", "QBER (%)")

def analysisRawKey():
    for keySize in keySizes:
        averageRawBB84 = []
        averageRawE91 = []
        for rawKeySize in rawKeySizesDict["BB84_" + str(keySize)]:
            averageRawBB84.append(rawKeySize / args.runTimes)
        for rawKeySize in rawKeySizesDict["E91_" + str(keySize)]:
            averageRawE91.append(rawKeySize / args.runTimes)
        helper_03.drawComparisonGraph(distances, averageRawE91, averageRawBB84, keySize, "Raw_Key_Size_Comparison", "Distance (M)", "Raw Key Size")

def analysisSecureKey():
    for keySize in keySizes:
        averageSecureBB84 = []
        averageSecureE91 = []
        for secureKeySize in secureKeySizesDict["BB84_" + str(keySize)]:
            averageSecureBB84.append(secureKeySize / args.runTimes)
        for secureKeySize in secureKeySizesDict["E91_" + str(keySize)]:
            averageSecureE91.append(secureKeySize / args.runTimes)
        helper_03.drawComparisonGraph(distances, averageSecureE91, averageSecureBB84, keySize, "Secure_Key_Size_Comparison", "Distance (M)", "Secure Key Size")

def createDistances():
    for i in range(20, args.distance, 20):
        distances.append(i)

def addKeys():
    for key in args.keySizes:
        keySizes.append(key)

if __name__ == '__main__':
    main()