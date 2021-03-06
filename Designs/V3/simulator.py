import argparse
import math
import BB84_03
import helper_03
import E91_03

#Store the key sizes to simulate
keySizes = []
#Store the distances to simulate
distances = []
#Dictionaries to store measurements
qberDict = {}
rawKeySizesDict = {}
secureKeySizesDict = {}

#Main function
def main():
    #Current % of simulation complete
    status = 0
    statusStep = 0
    #Argument parser that takes the distances, keysizes and how many times to run the simulator
    parser = argparse.ArgumentParser(description="QKD simulator")
    parser.add_argument("-d", "--distance", help="Max distance to inciment up too", type=int, default=200)
    parser.add_argument("-ks", "--keySizes", help="Space seperated list of key sizes to simulate", nargs="+", type=int, default=[128, 256])
    parser.add_argument("-rt", "--runTimes", help="How many times to run the simulator to get an average", type=int, default=1)
    global args
    args = parser.parse_args()
    
    createDistances()
    addKeys()
    statusStep = helper_03.calcualateStatusStep(len(keySizes), args.runTimes)
    #Run the simulation n amount of times
    for i in range(args.runTimes):
        status = runBB84(status, statusStep)
        status = runE91(status, statusStep)
    #Create graphs from results
    analysisQBER()
    analysisLogQBER()
    analysisRawKey()
    analysisSecureKey()
    print("Simulation complete")

#Run the BB84 simulation for each key size
def runBB84(status, statusStep):
    for keySize in keySizes:
        qbers = []
        rawKeySizes = []
        secureKeySizes = []
        for distance in distances:
            #Alice generates random bits to be encoded
            alicesRawKey = BB84_03.getRandomBits(keySize)
            #Alice randomly chooses which basis to use
            aliceBases = BB84_03.getRandomBits(keySize)
            #Alice preparing qubits
            alicesEncodedKey = BB84_03.encodeKey(alicesRawKey, aliceBases)
            alicesSentEncodedKey = BB84_03.encodeKey(alicesRawKey, aliceBases)
            #Calcualte the error rate depedning on the distance
            errorRate = BB84_03.calculateErrorRate(distance)
            #Add noise the the encoded key
            sentEncodedKey = BB84_03.addNoise(alicesSentEncodedKey, errorRate)
            #Bob randomly chooses which basis to use
            bobsBases = BB84_03.getRandomBits(keySize)
            #Bob measures the qubits sent by Alice
            bobsRawKey = BB84_03.measureQubits(sentEncodedKey, bobsBases)
            #Alice sends bob their bases so they can discared bits where the basis they chose were different
            siftedRawKeyAlice, siftedRawKeyBob = BB84_03.matchKeys(aliceBases, bobsBases, alicesEncodedKey, bobsRawKey)
            #Alice chooses random k/2 qubits to check the QBER which will be discared by both Alice and Bob
            qberCheckAlice, qberCheckBob, secureKeyAlice, secureKeyBob = BB84_03.checkKeys(siftedRawKeyAlice, siftedRawKeyBob)
            #Calcualte QBER
            qber = BB84_03.calcualteQBER(qberCheckAlice, qberCheckBob)
            #Perform error correction so they both have the same secure key
            secureKey = BB84_03.errorCorrection(secureKeyAlice, secureKeyBob)
            #print("Key size: " + str(keySize) + " Distance: " + str(distance) + " QBER: " + str(qber))
            #print("Length: " + str(len(secureKey)))
            #Save the measurements for the distance
            qbers.append(qber)
            rawKeySizes.append(len(siftedRawKeyAlice))
            secureKeySizes.append(len(secureKey))
        #Prepeare dictionary key
        dictString = "BB84_" + str(keySize)
        #Save all measurements in a dictonary
        helper_03.saveMeasurement(qberDict, qbers, dictString)
        helper_03.saveMeasurement(rawKeySizesDict, rawKeySizes, dictString)
        helper_03.saveMeasurement(secureKeySizesDict, secureKeySizes, dictString)
        status = status + statusStep
        print("Status: " + str(int(status)) + "%")
    return status

#Run the E91 simulation for each key size
def runE91(status, statusStep):
    for keySize in keySizes:
        qbers = []
        rawKeySizes = []
        secureKeySizes = []
        for distance in distances:
            #Alice and bob both randomly choose basis.
            aliceBasis, bobBasis, aliceChoices, bobChoices = E91_03.chooseBasis(keySize)
            #Alice prepares their basis
            aliceRotations = E91_03.prepareBasis(aliceBasis)
            #Bob prepares their basis
            bobRotations = E91_03.prepareBasis(bobBasis)
            #Alice and Bob measure the entangled particles to get their raw key and key to check qber
            rawKeyAlice, rawKeyBob, checkKeyAlice, checkKeyBob = E91_03.measure(aliceRotations, bobRotations, aliceChoices, bobChoices)
            #Simulate adding noise to keys
            rawKeyAliceNoise = E91_03.addNoise(rawKeyAlice, distance)
            checkKeyAliceNoise = E91_03.addNoise(checkKeyAlice, distance)
            #Calculate QBER
            qber = E91_03.calcualteQBER(checkKeyAliceNoise, checkKeyBob)
            #Perform error correction so they both have the same secure key
            secureKey = E91_03.errorCorrection(rawKeyAliceNoise, rawKeyBob)
            #Save the measurements for the distance
            qbers.append(qber)
            rawKeySizes.append(len(rawKeyAlice) + len(checkKeyAlice))
            secureKeySizes.append(len(secureKey))
            #print("length of secure key: " + str(len(secureKey)))
        dictString = "E91_" + str(keySize)
        #Save all measurements in a dictonary
        helper_03.saveMeasurement(qberDict, qbers, dictString)
        helper_03.saveMeasurement(rawKeySizesDict, rawKeySizes, dictString)
        helper_03.saveMeasurement(secureKeySizesDict, secureKeySizes, dictString)
        status = status + statusStep
        print("Status: " + str(status) + "%")
    return status

#Create the graph comparing QBER
def analysisQBER():
    for keySize in keySizes:
        averageQBERBB84 = []
        averageQBERE91 = []
        for qber in qberDict["BB84_" + str(keySize)]:
            averageQBERBB84.append(qber / args.runTimes)
        for qber in qberDict["E91_" + str(keySize)]:
            averageQBERE91.append(qber / args.runTimes)
        helper_03.drawComparisonGraph(distances, averageQBERE91, averageQBERBB84, keySize, "QBER_Comparison", "Distance (Km)", "QBER (%)")
        helper_03.createCSV(distances, averageQBERE91, averageQBERBB84, keySize, "QBER_Comparison")

#Create the graph comparing Log of QBER
def analysisLogQBER():
    for keySize in keySizes:
        averageQBERBB84 = []
        averageQBERE91 = []
        for qber in qberDict["BB84_" + str(keySize)]:
            if qber > 0:
                averageQBERBB84.append(math.log10(qber / args.runTimes))
            else:
                averageQBERBB84.append(0)
        for qber in qberDict["E91_" + str(keySize)]:
            if qber > 0:
                averageQBERE91.append(math.log10(qber / args.runTimes))
            else:
                averageQBERE91.append(0)
        helper_03.drawComparisonGraph(distances, averageQBERE91, averageQBERBB84, keySize, "QBER_Log_Comparison", "Distance (Km)", "Log(QBER) (%)")
        helper_03.createCSV(distances, averageQBERE91, averageQBERBB84, keySize, "QBER_Log_Comparison")

#Create the graph comparing the raw key sizes
def analysisRawKey():
    for keySize in keySizes:
        averageRawBB84 = []
        averageRawE91 = []
        for rawKeySize in rawKeySizesDict["BB84_" + str(keySize)]:
            averageRawBB84.append(rawKeySize / args.runTimes)
        for rawKeySize in rawKeySizesDict["E91_" + str(keySize)]:
            averageRawE91.append(rawKeySize / args.runTimes)
        helper_03.drawComparisonGraph(distances, averageRawE91, averageRawBB84, keySize, "Raw_Key_Size_Comparison", "Distance (Km)", "Raw Key Size (bits)")
        helper_03.createCSV(distances, averageRawE91, averageRawBB84, keySize, "Raw_Key_Size_Comparison")

#Create the graph comparing secure key sizes
def analysisSecureKey():
    for keySize in keySizes:
        averageSecureBB84 = []
        averageSecureE91 = []
        for secureKeySize in secureKeySizesDict["BB84_" + str(keySize)]:
            averageSecureBB84.append(secureKeySize / args.runTimes)
        for secureKeySize in secureKeySizesDict["E91_" + str(keySize)]:
            averageSecureE91.append(secureKeySize / args.runTimes)
        helper_03.drawComparisonGraph(distances, averageSecureE91, averageSecureBB84, keySize, "Secure_Key_Size_Comparison", "Distance (Km)", "Secure Key Size (bits)")
        helper_03.createCSV(distances, averageSecureE91, averageSecureBB84, keySize, "Secure_Key_Size_Comparison")

#create the array of distances from args
def createDistances():
    for i in range(1, args.distance + 1):
        distances.append(i)

#create the array of key sizes from args
def addKeys():
    for key in args.keySizes:
        keySizes.append(key)

if __name__ == '__main__':
    main()