import argparse
import BB84_03
import helper_03
import E91_03

#Store the key sizes to simulate
keySizes = []
#Store the distances to simulate
distances = []
#Dictionaries to store measurements
qberDict = {}
siftedKeySizesDict = {}
secureKeySizesDict = {}

#Main function
def main():
    #Current % of simulation complete
    status = 0
    statusStep = 0
    #Argument parser that takes the distances, keysizes and how many times to run the simulator
    parser = argparse.ArgumentParser(description="QKD simulator")
    parser.add_argument("-d", "--distance", help="Max distance to inciment up too", type=int, default=100)
    parser.add_argument("-ks", "--keySizes", help="Space seperated list of key sizes to simulate", nargs="+", type=int, default=[128, 256])
    parser.add_argument("-rt", "--runTimes", help="How many times to run the simulator to get an average", type=int, default=1)
    global args
    #Check if arguments inputed are valid
    args = parser.parse_args()
    if args.runTimes < 1:
        parser.error("Error: runTimes must be greater than 0.")
    if args.distance < 1:
        parser.error("Error: distance must be greater than 0.")
    for arg in args.keySizes:
        if arg < 1:
            parser.error("Error: runTimes must be greater than 0.")     
    createDistances()
    addKeys()
    statusStep = helper_03.calcualateStatusStep(len(keySizes), args.runTimes)
    #Run the simulation n amount of times
    for i in range(args.runTimes):
        status = runBB84(status, statusStep)
        status = runE91(status, statusStep)
    #Create graphs from results
    analysisQBER()
    analysisSiftedKey()
    analysisSecureKey()
    print("Simulation complete")

#Run the BB84 simulation for each key size
def runBB84(status, statusStep):
    for keySize in keySizes:
        qbers = []
        siftedKeySizes = []
        secureKeySizes = []
        for distance in distances:
            #Alice generates random bits to be encoded
            alicesRawKey = BB84_03.getRandomBits(keySize)
            #Alice randomly chooses which basis to use
            aliceBases = BB84_03.getRandomBits(keySize)
            #Alice preparing qubits
            alicesEncodedKey = BB84_03.encodeKey(alicesRawKey, aliceBases)
            #Calcualte the error rate depedning on the distance
            errorRate = BB84_03.calculateErrorRate(distance)
            #Add noise the the encoded key
            sentEncodedKey = BB84_03.addNoise(alicesEncodedKey, errorRate)
            #Bob randomly chooses which basis to use
            bobsBases = BB84_03.getRandomBits(keySize)
            #Bob measures the qubits sent by Alice
            bobsRawKey = BB84_03.measureQubits(sentEncodedKey, bobsBases)
            #Alice sends bob their bases so they can discared bits where the basis they chose were different
            siftedRawKeyAlice, siftedRawKeyBob = BB84_03.matchKeys(aliceBases, bobsBases, alicesRawKey, bobsRawKey)
            #Alice chooses random k/2 qubits to check the QBER which will be discared by both Alice and Bob
            qberCheckAlice, qberCheckBob, secureKeyAlice, secureKeyBob = BB84_03.checkKeys(siftedRawKeyAlice, siftedRawKeyBob)
            #Calcualte QBER
            qber = BB84_03.calcualteQBER(qberCheckAlice, qberCheckBob)
            #Perform error correction so they both have the same secure key
            secureKey = BB84_03.errorCorrection(secureKeyAlice, secureKeyBob)
            #Save the measurements for the distance
            qbers.append(qber)
            siftedKeySizes.append(len(siftedRawKeyAlice))
            secureKeySizes.append(len(secureKey))
        #Prepeare dictionary key
        dictString = "BB84_" + str(keySize)
        #Save all measurements in a dictonary
        helper_03.saveMeasurement(qberDict, qbers, dictString)
        helper_03.saveMeasurement(siftedKeySizesDict, siftedKeySizes, dictString)
        helper_03.saveMeasurement(secureKeySizesDict, secureKeySizes, dictString)
        status = helper_03.printStatus(status, statusStep)
    return status

#Run the E91 simulation for each key size
def runE91(status, statusStep):
    for keySize in keySizes:
        qbers = []
        siftedKeySizes = []
        secureKeySizes = []
        for distance in distances:
            #Alice and bob both randomly choose basis.
            aliceBasis, bobBasis, aliceChoices, bobChoices = E91_03.chooseBasis(keySize)
            #Alice prepares their basis
            aliceRotations = E91_03.prepareBasis(aliceBasis)
            #Bob prepares their basis
            bobRotations = E91_03.prepareBasis(bobBasis)
            #Alice and Bob measure the entangled particles and siftis their key.
            siftedKeyAlice, siftedKeyBob, checkKeyAlice, checkKeyBob = E91_03.measure(aliceRotations, bobRotations, aliceChoices, bobChoices)
            #Simulate adding noise to keys
            siftedKeyAliceNoise = E91_03.addNoise(siftedKeyAlice, distance)
            siftedKeyAliceNoiseCheck = E91_03.addNoise(checkKeyAlice, distance)
            #Calculate QBER
            qber = E91_03.calcualteQBER(siftedKeyAliceNoiseCheck, checkKeyBob)
            #Perform error correction so they both have the same secure key
            secureKey = E91_03.errorCorrection(siftedKeyAliceNoise, siftedKeyBob)
            #Save the measurements for the distance
            qbers.append(qber)
            siftedKeySizes.append(len(siftedKeyAlice) + len(checkKeyAlice))
            secureKeySizes.append(len(secureKey))
            #print("length of secure key: " + str(len(secureKey)))
        dictString = "E91_" + str(keySize)
        #Save all measurements in a dictonary
        helper_03.saveMeasurement(qberDict, qbers, dictString)
        helper_03.saveMeasurement(siftedKeySizesDict, siftedKeySizes, dictString)
        helper_03.saveMeasurement(secureKeySizesDict, secureKeySizes, dictString)
        status = helper_03.printStatus(status, statusStep)
    return status

#Create the graph comparing QBER
def analysisQBER():
    for keySize in keySizes:
        averageQBERBB84 = []
        averageQBERE91 = []
        averageQBERBB84Log = []
        averageQBERE91Log = []
        for qber in qberDict["BB84_" + str(keySize)]:
            averageQBERBB84.append(qber / args.runTimes)
            averageQBERBB84Log.append((qber / args.runTimes) / 100)
        for qber in qberDict["E91_" + str(keySize)]:
            averageQBERE91.append(qber / args.runTimes)
            averageQBERE91Log.append((qber / args.runTimes) / 100)
        helper_03.drawComparisonGraph(distances, averageQBERE91, averageQBERBB84, keySize, "QBER_Comparison", "Distance (Km)", "QBER (%)")
        helper_03.drawComparisonGraphSemilogy(distances, averageQBERE91Log, averageQBERBB84Log, keySize, "QBER_Log_Comparison", "Distance (Km)", "QBER")
        helper_03.createCSV(distances, averageQBERE91, averageQBERBB84, keySize, "QBER_Comparison")

#Create the graph comparing the sifted key sizes
def analysisSiftedKey():
    for keySize in keySizes:
        averageRawBB84 = []
        averageRawE91 = []
        for rawKeySize in siftedKeySizesDict["BB84_" + str(keySize)]:
            averageRawBB84.append(rawKeySize / args.runTimes)
        for rawKeySize in siftedKeySizesDict["E91_" + str(keySize)]:
            averageRawE91.append(rawKeySize / args.runTimes)
        helper_03.drawComparisonGraph(distances, averageRawE91, averageRawBB84, keySize, "Sifted_Key_Size_Comparison", "Distance (Km)", "Sifted Key Size (bits)")
        helper_03.createCSV(distances, averageRawE91, averageRawBB84, keySize, "Sifted_Key_Size_Comparison")

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