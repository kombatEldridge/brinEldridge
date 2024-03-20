from pylab import *
import secrets
import matplotlib.pyplot as plt
import pymysql
import matplotlib
import pandas as pd
import sys
import warnings
warnings.filterwarnings('ignore')
print("\n|-----------------------------------------------------------------------------------------------|\n|------------------------------ Multilayer Database Visualization ------------------------------|\n|-----------------------------------------------------------------------------------------------|\n")

# --------------- connection --------------- #

hostdb = "localhost"
portdb = int(3306)
userdb = "root"
passworddb = "123456789"
namedb = "multilayer"

conn = pymysql.connect(host=hostdb, port=portdb,
                       user=userdb, passwd=passworddb, db=namedb)
dfConditions = pd.read_sql_query("SELECT * FROM conditions", conn)
dfResults = pd.read_sql_query("SELECT * FROM results", conn)

print("Server Connection Successful!\n\nConditions:")

for i in range(len(dfConditions.columns)):
    print("\t"+dfConditions.columns[i])
print()

numWhere = int(input("How many WHERE clauses do you want to add?\n> "))


# --------------- figure creation --------------- #
def displayCustom():
    print()
    whereClause = ["coreSize=20", "sio2Size=5", "shellSize=10"]
    dfString = "SELECT * FROM results NATURAL JOIN conditions WHERE {}".format(
        " AND ".join(whereClause))

    df = pd.read_sql_query(dfString, conn)
    # --------------- conditions entry --------------- #

    lamda = df["lambda"].unique()

    class xVar:
        def __init__(self, name):
            self.name = name
            self.dictionary = {}
            for expID in df["expID"].unique():
                self.dictionary[expID] = expVar(expID, name)

    class expVar:
        def __init__(self, expID, parent):
            self.expID = expID
            self.name = parent
            dfStringTemp = " ".join([dfString, "AND expID =", str(expID)])
            dfTemp = pd.read_sql_query(dfStringTemp, conn)
            self.data = dfTemp[self.name].to_numpy()
            self.lamda = dfTemp["lambda"].to_numpy()
            if (str(expID)[-1] == "0"):
                self.color = "red"
            else:
                self.color = "blue"
    
    series = {}
    series["series{}".format(0)] = xVar(dfResults.columns[2])
    series["series{}".format(1)] = xVar(dfResults.columns[3])
    series["series{}".format(2)] = xVar(dfResults.columns[4])
    series["series{}".format(3)] = xVar(dfResults.columns[5])
    
    expIDi = []
    expIDo = []
    for expID in df["expID"].unique():
        if (str(expID)[-1] == "0"):
            expIDi.append(expID)
        else:
            expIDo.append(expID)

    for ser in series:
        print(series[ser].name)
        for outer in expIDo:
            print("outer: "+str(outer))
            plt.plot(series[ser].dictionary[outer].lamda, series[ser].dictionary[outer].data, '-',
                    c=series[ser].dictionary[outer].color, label="Outer Sphere")

        for inner in expIDi:
            print("inner: "+str(inner))
            plt.plot(series[ser].dictionary[inner].lamda, series[ser].dictionary[inner].data, '-',
                    c=series[ser].dictionary[inner].color, label="Inner Sphere")

        plt.legend()
        plt.ylabel(series[ser].dictionary[outer].name, fontsize=20)
        plt.xlabel('Wavelength (nm)', fontsize=20)
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(9, 9)
        ax = plt.subplot(111)
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        plt.title(" AND ".join(whereClause))
        fig.savefig("".join(["/images/",series[ser].name, ".png"]), dpi=400)
        fig.clf()

if numWhere == 999:
    displayCustom()
    sys.exit()

print()
whereClause = []
for x in range(numWhere):
    whereClause.append(
        input("Please enter your WHERE clause (ex: \"coreSize = 5\"):\n> "))

dfString = "SELECT * FROM results NATURAL JOIN conditions WHERE {}".format(
    " AND ".join(whereClause))

df = pd.read_sql_query(dfString, conn)

print("Experiments found:")
print(df["expID"].unique())
print()

# --------------- conditions entry --------------- #

lamda = df["lambda"].unique()

class xVar:
    def __init__(self, name):
        self.name = name
        self.dictionary = {}
        for expID in df["expID"].unique():
            self.dictionary[expID] = expVar(expID, name)

class expVar:
    def __init__(self, expID, parent):
        self.expID = expID
        self.name = parent
        dfStringTemp = " ".join([dfString, "AND expID =", str(expID)])
        dfTemp = pd.read_sql_query(dfStringTemp, conn)
        self.data = dfTemp[self.name].to_numpy()
        self.lamda = dfTemp["lambda"].to_numpy()
        self.color = f"#{secrets.token_hex(3)}"
print("Series:")
for i in range(len(dfResults.columns)):
    print("".join(["\t[", str(i), "] ", dfResults.columns[i]]))
print()

numSeries = int(input("How many series do you want to map?\n(Note: Inner and Outer measurements will be displayed for any series selected by default. Type 0 to graph inner and outer together.)\n> "))
print()

# --------------- figure creation --------------- #
def displayTogether():
    series = {}
    for x in range(numSeries):
        index = int(input("Please select index of series:\n> "))
        series["series{}".format(x)] = xVar(dfResults.columns[index])

    for ser in series:
        for outer in df["expID"].unique():
            plt.plot(series[ser].dictionary[outer].lamda, series[ser].dictionary[outer].data, '-',
                    c=series[ser].dictionary[outer].color, label=series[ser].dictionary[outer].expID)
        plt.legend()
        plt.ylabel(series[ser].name, fontsize=20)
        plt.xlabel('Wavelength (nm)', fontsize=20)
        plt.title(" AND ".join(whereClause), fontsize=12)
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(9, 9)
        ax = plt.subplot(111)
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        fig.savefig("".join(["images/","_AND_".join(whereClause), ".png"]), dpi=500)
        fig.clf()


# --------------- figure creation --------------- #
def displaySeparate():
    series = {}
    for x in range(numSeries):
        index = int(input("Please select index of series:\n> "))
        series["series{}".format(x)] = xVar(dfResults.columns[index])
        
    expIDi = []
    expIDo = []
    for expID in df["expID"].unique():
        if (str(expID)[-1] == "0"):
            expIDi.append(expID)
        else:
            expIDo.append(expID)
        
    for ser in series:
        for outer in expIDo:
            print(outer)
            plt.plot(series[ser].dictionary[outer].lamda, series[ser].dictionary[outer].data, '-',
                    c=series[ser].dictionary[outer].color, 
                    label=series[ser].dictionary[outer].expID)
        
        plt.legend()
        plt.ylabel(series[ser].name, fontsize=20)
        plt.xlabel('Wavelength (nm)', fontsize=20)
        plt.title(" ".join([" AND ".join(whereClause), "(Outer Sphere)"]), fontsize=12)
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(9, 9)
        ax = plt.subplot(111)
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        fig.savefig("".join(["images/","_AND_".join(whereClause), "_", series[ser].name, "_(Outer Sphere)", ".png"]), dpi=500)
        fig.clf()

        for inner in expIDi:
            plt.plot(series[ser].dictionary[inner].lamda, series[ser].dictionary[inner].data, '-',
                    c=series[ser].dictionary[inner].color, 
                    label=series[ser].dictionary[inner].expID)

        plt.legend()
        plt.ylabel(series[ser].name, fontsize=20)
        plt.xlabel('Wavelength (nm)', fontsize=20)
        plt.title(" ".join([" AND ".join(whereClause), "(Inner Sphere)"]), fontsize=12)
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(9, 9)
        ax = plt.subplot(111)
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        fig.savefig("".join(["images/","_AND_".join(whereClause), "_", series[ser].name, "_(Inner Sphere)", ".png"]), dpi=500)
        fig.clf()


if numSeries == 0:
    numSeries = int(input("How many series do you want to map?\n> "))
    print()
    displayTogether()
else:
    displaySeparate()

