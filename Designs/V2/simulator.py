import BB84_02
import helper_02
import E91_02

keySizes = [64, 128, 256, 512, 1024]

distances = []
measurmentsBB84QBER = []
measurmentsE91QBER = []

def main():
    createDistances()
    runBB84()
    runE91()
    analysis()

def runBB84():
    for keySize in keySizes:
        qbers = []
        secureKeySizes = []
        for distance in distances:
            #Alice generates random bits to be encoded
            alicesRawKey = helper_02.getRandomBits(keySize)
            #Alice chooses which basis to use
            aliceBases = helper_02.getRandomBits(keySize)
            #Alice preparing qubits
            alicesEncodedKey = BB84_02.encodeKey(alicesRawKey, aliceBases)
            #Calcualte the error rate depedning on the distance
            errorRate = helper_02.calculateErrorRate(distance)
            #Add noise the the encoded key
            sentEncodedKey = helper_02.addNoise(alicesEncodedKey, errorRate)
            #Bob prepares random basis
            bobsBases = helper_02.getRandomBits(keySize)
            #Bob measures the qubits sent by Alice
            bobsRawKey = BB84_02.measureQubits(sentEncodedKey, bobsBases)
            #Alice sends bob their bases so they can discared basis they chose differently
            keyAlice, keyBob = BB84_02.matchKeys(aliceBases, bobsBases, alicesEncodedKey, bobsRawKey)
            #Alice chooses random k/2 qubits to check the QBER
            qberCheckAlice, qberCheckBob, secureKeyAlice, secureKeyBob = BB84_02.checkKeys(keyAlice, keyBob)
            #Calcualte QBER
            qber = helper_02.calcualteQBER(qberCheckAlice, qberCheckBob)
            secureKey = BB84_02.errorCorrection(secureKeyAlice, secureKeyBob)
            print("Key size: " + str(keySize) + " Distance: " + str(distance) + " QBER: " + str(qber))
            print("Length: " + str(len(secureKey)))
            qbers.append(qber)
            secureKeySizes.append(len(secureKey))
        helper_02.drawGraph(distances, secureKeySizes, keySize, "SecureKey_BB84_")
        helper_02.drawGraph(distances, qbers, keySize, "QBER_BB84_")
        measurmentsBB84QBER.append(qbers)

def runE91():
    for keySize in keySizes:
        qbers = []
        secureKeySizes = []
        for distance in distances:
            #Alice and Bob choose randomly choose basis used for measuring
            aliceBasis, bobBasis, aliceChoices, bobChoices = E91_02.chooseBasis(keySize)
            #Alice and Bob prepare their basis
            aliceRotations = E91_02.prepareBasis(aliceBasis)
            bobRotations = E91_02.prepareBasis(bobBasis)
            #Alice and bob measure the entangled particles
            rawKeyAlice, rawKeyBob, checkKeyAlice, checkKeyBob = E91_02.measure(aliceRotations, bobRotations, aliceChoices, bobChoices)
            #Simulate noise in the key
            rawKeyAliceNoise = E91_02.addNoiseV2(rawKeyAlice, distance)
            checkKeyAliceNoise = E91_02.addNoiseV2(checkKeyAlice, distance)
            #Calcualte QBER
            qber = E91_02.calcualteQBER(checkKeyAliceNoise, checkKeyBob)
            qbers.append(qber)
            secureKey = E91_02.errorCorrection(rawKeyAliceNoise, rawKeyBob)
            secureKeySizes.append(len(secureKey))
            print("length of secure key: " + str(len(secureKey)))
        helper_02.drawGraph(distances, secureKeySizes, keySize, "SecureKey_E91_")
        helper_02.drawGraph(distances, qbers, keySize, "QBER_E91_")
        measurmentsE91QBER.append(qbers)

def analysis():
    keySizeCounter = 0
    for i in range(len(measurmentsBB84QBER)):
        helper_02.drawComparisonGraphQBER(distances, measurmentsE91QBER[i], measurmentsBB84QBER[i], keySizeCounter, "QBER_comparison_")
        keySizeCounter += 1
        if keySizeCounter > 8:
            keySizeCounter = 0

def createDistances():
    for i in range(20, 1500, 20):
        distances.append(i)

if __name__ == '__main__':
    main()