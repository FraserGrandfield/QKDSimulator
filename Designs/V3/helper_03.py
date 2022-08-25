import matplotlib.pyplot as plt
import csv

#Draw a graph comparing meausrments from both protocols.
def drawComparisonGraph(distances, e91Measurements01, bb84Measurements01, e91Measurements02, bb84Measurements02, keySize, type, xAxis, yAxis):
    plt.clf()
    plt.plot(distances, e91Measurements01, label="E91 \u03B1 = 0.2")
    plt.plot(distances, bb84Measurements01, label="BB84 \u03B1 = 0.2")
    plt.plot(distances, e91Measurements02, label="E91 \u03B1 = 0.25", linestyle='dashed')
    plt.plot(distances, bb84Measurements02, label="BB84 \u03B1 = 0.25", linestyle='dashed')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.grid(True)
    plt.legend()
    plt.title("Keysize " + str(keySize))
    plt.savefig(type + str(keySize) + ".png")

#Draw a graph comparing meausrments from both protocols.
def drawComparisonGraphSemilogy(distances, e91Measurements01, bb84Measurements01, e91Measurements02, bb84Measurements02, keySize, type, xAxis, yAxis):
    plt.clf()
    plt.semilogy(distances, e91Measurements01, label="E91 \u03B1 = 0.2")
    plt.semilogy(distances, bb84Measurements01, label="BB84 \u03B1 = 0.2")
    plt.semilogy(distances, e91Measurements02, label="E91 \u03B1 = 0.25", linestyle='dashed')
    plt.semilogy(distances, bb84Measurements02, label="BB84 \u03B1 = 0.25", linestyle='dashed')
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.grid(True)
    plt.legend()
    plt.title("Keysize " + str(keySize))
    plt.savefig(type + str(keySize) + ".png")

#Save a measurement.
def saveMeasurement(dic, measurments, key):
    if key in dic.keys():
        for i in range(len(measurments)):
            dic[key][i] = dic[key][i] + measurments[i]
    else:
        dic[key] = []
        for i in range(len(measurments)): 
            dic[key].append(measurments[i])

#Calculate what percentage to step up the status of how much progress the simulator has completed.
def calcualateStatusStep(noOfKeys, noOfRunTimes, noFiberLossParams):
    total = noOfKeys * noOfRunTimes * noFiberLossParams * 2
    return (100 / total)

#Create a csv file to display the measurement values.
def createCSV(distances, e91Measurements01, bb84Measurements01, e91Measurements02, bb84Measurements02, keySize, type):
    header = ["distance", "BB8401", "E9101", "BB8402", "E9102"]
    with open(type + str(keySize) + ".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range(len(distances)):
            row = []
            row.append(distances[i])
            row.append(bb84Measurements01[i])
            row.append(e91Measurements01[i])
            row.append(e91Measurements02[i])
            row.append(bb84Measurements02[i])
            writer.writerow(row)

#Print current status of simulator.
def printStatus(status, statusStep):
    status = status + statusStep
    print(f"Status: {status}%")
    return status