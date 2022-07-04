import BB84_02
import helper

def main():
    runBB84()

def runBB84():
    keySizes = [8, 16, 32, 64, 128, 256, 512, 1024]
    distances = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]

    for keySize in keySizes:
        qbers = []
        for distance in distances:
            #Alice generates random bits to be encoded
            alicesRawKey = helper.getRandomBits(keySize)
            #Alice chooses which basis to use
            aliceBases = helper.getRandomBits(keySize)
            #Alice preparing qubits
            alicesEncodedKey = BB84_02.encodeKey(alicesRawKey, aliceBases)
            #Calcualte the error rate depedning on the distance
            errorRate = helper.calculateErrorRate(distance)
            #Add noise the the encoded key
            sentEncodedKey = helper.addNoise(alicesEncodedKey, errorRate)
            #Bob prepares random basis
            bobsBases = helper.getRandomBits(keySize)
            #Bob measures the qubits sent by Alice
            bobsRawKey = BB84_02.measureQubits(sentEncodedKey, bobsBases)
            #Alice sends bob their bases so they can discared basis they chose differently
            keyAlice, keyBob = BB84_02.matchKeys(aliceBases, bobsBases, alicesEncodedKey, bobsRawKey)
            #Alice chooses random k/2 qubits to check the QBER
            qberCheckAlice, qberCheckBob, secureKeyAlice, secureKeyBob = BB84_02.checkKeys(keyAlice, keyBob)
            #Calcualte QBER
            qber = helper.calcualteQBER(qberCheckAlice, qberCheckBob)
            print("Key size: " + str(keySize) + " Distance: " + str(distance) + " QBER: " + str(qber))
            print("Length: " + str(len(secureKeyAlice)))
            print("Length: " + str(len(secureKeyBob)))
            qbers.append(qber)
        helper.drawGraphQBER(distances, qbers, keySize)

if __name__ == '__main__':
    main()