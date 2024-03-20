import pandas as pd
import numpy as np
import os
import re


def makeOneTxt(txtFilePath):
    dataAlready = pd.read_csv(txtFilePath, sep=',',
                              header=None, skiprows=1).values.astype(str)
    masterPath = os.getcwd() + "/masterData.txt"
    masterFile = open(masterPath, "a")
    for rows in dataAlready:
        if(float(rows[0]) == 1000):
            continue
        txt = ",".join(rows)
        if(len(rows) == 5):
                txt = ",".join([txt, "null", "null", "null", "null", "null", "null"]) #for data not including new Esqu data
        txt = ",".join([txt, os.path.basename(txtFilePath)])
        masterFile.write(txt+"\n")
    masterFile.close()


def createCSV(masterPath):
    df = pd.read_csv(masterPath, sep=',', header=None, skiprows=1).astype(str)
    dataEsphere = df[df[1].str.contains("nan") == False].values

    lamda = dataEsphere[:, 0]
    qEXT = dataEsphere[:, 1]
    qSCA = dataEsphere[:, 2]
    qABS = dataEsphere[:, 3]
    eSQUARED = dataEsphere[:, 4]
    eSQUdev = dataEsphere[:, 5]
    Q1 = dataEsphere[:,6]
    Q3 = dataEsphere[:,7]
    avg = dataEsphere[:,8]
    MIN = dataEsphere[:,9]
    MAX = dataEsphere[:,10]

    for i in range(len(eSQUdev)):
        if eSQUdev[i] == "nan":
            eSQUdev[i] = "NULL"
    for i in range(len(Q1)):
        if Q1[i] == "nan":
            Q1[i] = "NULL"
    for i in range(len(Q3)):
        if Q3[i] == "nan":
            Q3[i] = "NULL"
    for i in range(len(avg)):
        if avg[i] == "nan":
            avg[i] = "NULL"
    for i in range(len(MIN)):
        if MIN[i] == "nan":
            MIN[i] = "NULL"
    for i in range(len(MAX)):
        if MAX[i] == "nan":
            MAX[i] = "NULL"

    fullFileName = dataEsphere[:, 11]
    primaryID = createID(fullFileName)
    core = []
    middle = []
    outer = []
    measurement = []

    # Example: 25core_10.5nm-Au_2nm-SiO2_outer_sphere
    for i in range(0, len(lamda)):
        componentList = fullFileName[i].split("_")
        core.append(re.findall(
            "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", componentList[0])[0])
        middle.append(re.findall(
            "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", componentList[2])[0])
        outer.append(re.findall(
            "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", componentList[1])[0])
        measurement.append(componentList[3])

    outputFileResults = os.getcwd()+"/Database Files/Results.csv"
    outputFileConditionsTemp = os.getcwd()+"/Database Files/ConditionsTemp.csv"

    file = open(outputFileResults, "w+")
    header = ",".join(["expID", "lambda", "qEXT", "qSCA", "qABS", "eSQU", "eSQUdev", "eSQUQ1", "eSQUQ3", "eSQUavg", "eSQUmin", "eSQUmax"])

    file.write(header)
    file.write("\n")

    for i in range(0, len(lamda)):
        text = ",".join([str(primaryID[i]),
                    str(lamda[i]),
                    str(qEXT[i]),
                    str(qSCA[i]),
                    str(qABS[i]),
                    str(eSQUARED[i]),
                    str(eSQUdev[i]),
                    str(Q1[i]),
                    str(Q3[i]),
                    str(avg[i]),
                    str(MIN[i]),
                    str(MAX[i])])
        file.write(text+"\n")
    file.close()

    file = open(outputFileConditionsTemp, "w+")
    header = ",".join(["expID", "coreSize", "sio2Size",
                      "shellSize", "outerBoolean"])

    file.write(header)
    file.write("\n")

    for i in range(0, len(primaryID)):
        text = ",".join([str(primaryID[i]),
                         str(core[i]),
                         str(middle[i]),
                         str(outer[i]),
                         str(measurement[i])])
        file.write(text+"\n")
    file.close()

    outputFileConditions = os.getcwd()+"/Database Files/Conditions.csv"
    df = pd.read_csv(outputFileConditionsTemp, sep=",")
    df.drop_duplicates(subset=None, inplace=True)
    df.to_csv(outputFileConditions, index=False)

    os.remove(masterPath)
    os.remove(outputFileConditionsTemp)
    print("Files created!")


def createID(expConditions):
    primaryID = []
    for i in range(len(expConditions)):
        componentList = expConditions[i].split("_")
        text = []
        for x in range(len(componentList)):
            if (re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", componentList[x]) != []):
                text.append(re.findall(
                    "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", componentList[x])[0])
                text[x] = text[x].replace(".", "")

        if (componentList[3] == "outer"):
            text.append("1")
        if (componentList[3] == "inner"):
            text.append("0")

        primaryID.append("".join(text))
    return primaryID


masterPath = os.getcwd() + "/masterData.txt"
masterFile = open(masterPath, "w")
# header = ",".join(["expID", "lambda", "qEXT", "qSCA", "qABS", "eSQU", "eSQUdev", "eSQUQ1", "eSQUQ3", "eSQUavg", "eSQUmin", "eSQUmax"])
masterFile.write("lambda,qEXT,qSCA,qABS,eSQU,eSQUdev,eSQUQ1,eSQUQ3,eSQUavg,eSQUmin,eSQUmax,fileName\n")
masterFile.close()

# To be run in folder with all text files
for txtFilePath in os.listdir(os.getcwd()+"/Unprocessed Data/"):
    if ".txt" in txtFilePath:
        print(txtFilePath)
        makeOneTxt(os.getcwd()+"/Unprocessed Data/"+txtFilePath)

# To be run in folder with masterData.txt
createCSV("masterData.txt")