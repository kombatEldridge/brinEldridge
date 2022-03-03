import subprocess
import numpy as np
import pandas as pd
import os
from pylab import *
import scipy.constants as sc
import scipy as scipy
from scipy import optimize
from colorama import Fore, Style

class ySeries:
    def __init__(self, values, name):
        self.values=values
        self.name=name

def processData(x, y, lamdaF, lamdaL, gam):
    h=sc.h #Plancks
    c=sc.c #Speed of light

    #We need to ensure the user puts in a reasonable guess
    if(gam<=0):
        return "Error! Gamma must be positive."

    #Fano function with scalar (to be done first)
    def sFano(x, gam, x0, q, a):
        return (((2*h*c*(1/(x*1e-9)-1/(x0*1e-9))/gam)+q)**2/((2*h*c*(1/(x*1e-9)-1/(x0*1e-9))/gam)**2+1)*a)

    #This is the definition of the Fano Eq. (without scalar)
    def nFano(x, gam, x0, q):
        return (((2*h*c*(1/(x*1e-9)-1/(x0*1e-9))/gam)+q)**2/((2*h*c*(1/(x*1e-9)-1/(x0*1e-9))/gam)**2+1))

    #We trim our data to the given interval
    #This process finds the index of the wavelength value in our data. set to easily snip the data at the indeces.
    lamdaFi = np.where(x==lamdaF)[0][0]
    lamdaLi = np.where(x==lamdaL)[0][0]
    #making a new data set, trimming off the edges and keeping the selected wavelength interval
    x = np.delete(x, slice(lamdaFi))
    y = np.delete(y, slice(lamdaFi))
    x = np.delete(x, slice(lamdaLi-lamdaFi+1, int(len(x))))
    y = np.delete(y, slice(lamdaLi-lamdaFi+1, int(len(y))))

    #Since the minimum of a Fano resonace goes exactly to zero, we shift the entire data set down to where its lowest point is also at zero
    y = y - min(y)

    #Again, we need to help the computer as much as we can by giving it a good guess for lambda0, q, and a
    xmax=x[np.where(y==max(y))[0][0]]
    xmin=x[np.where(y==min(y))[0][0]]
    x0=(xmax+xmin)/2 #this is the midpoint of the fano peaks and we will use it as a good guess for lambda0
    if(np.where(y==max(y))[0][0]>np.where(y==min(y))[0][0]): #this if statement to pick parity of q is off an observation of the nature of the order of the peaks
        q=-1
    else:
        q=1
    a = 0.3 #guess for scalar

    #We then run the data through the scaler Fano (sFano) to find the proper scaler to change our data by
    poptsFano, pcovsFano = scipy.optimize.curve_fit(sFano, x, y, p0=[gam, x0, q, a], maxfev=100000)

    #Scale the data since a*Fano=y then Fano=y/a
    y=y/(poptsFano[3])

    #We then run the scaled data thought the un-augmented Fano Eq
    popt_nfano, _ = scipy.optimize.curve_fit(nFano, x, y, p0=[gam, x0, q], maxfev=100000)

    #In an effort to create a measure of fitness for each Fano Fit, 
    #A higher fitness score, the better the fit (max = 1).
    #Although this particular calculation of R^2 is for linear models, it is sufficent for its ability to consider the average vertical distance between the data and the prediciton.
    SSE = sum((y - (nFano(x, *popt_nfano)))**2)
    SST = sum((y - average(y))**2)
    fitness = 1-(SSE/SST)

    #observation: negating both Gamma and q does nothing to Fano, but makes sure Gamma is positive
    #by giving a good guess, this shouldn't happen
    if(popt_nfano[0]<0):
        popt_nfano[0]=-popt_nfano[0]
        popt_nfano[2]=-popt_nfano[2]

    #outputs q, gamma, x0, fitness, nFano y values, a scalar, original x data, scaled y data (in that order)
    return(popt_nfano[2], popt_nfano[0], popt_nfano[1], fitness, nFano(x, *popt_nfano), poptsFano[3], x, y)

#Introductions. Comment this line if user wants to conserve screen space on command line.
#print("Fano Fitting processor\n\nPlease make sure your file is formatted as an output file from the following list:\n\tAverageEsphere\n\tAverageEXTABS\n\tOrientation\n")

files = []
fileCount = 0
print("The following text files have been detected:\n")
for file in os.listdir(os.getcwd()):
     # check the files which are end with specific extension
    if file.endswith(".txt"):
        # print path name of selected files
        print("[",fileCount,"] ",file)
        files.append(file)
        fileCount += 1
filename = int(input("\nPlease select file number:"))
path = os.getcwd() + "/" + files[filename] #path of the file
data = pd.read_csv(path, sep='\t', header=None, skiprows=1).values
columns = len(data[:][0])

# This just takes in the data and formats it into a usable array.
# NOTE: Make sure your file contains ONLY one tab between data points and NO space bars.
# TIP: Open all of your data text files into Visual Studio Code and let it do a system wide "find and replace" for any double tabs or additional sapce bars.
x = data[:,0] #Column 0 is always the wavelength #x1a
yData = []
for ii in range(1, columns):
    yData.append(ySeries(data[:, ii], "Column %d" % (ii)))

# Ask the user to identify the interval in which the user thinks the fano resonance is in
lamdaF = input("\nFirst wavelength of the interval (default: 350nm):")
if(lamdaF == ""):
    lamdaF = 350
else:
    lamdaF = int(lamdaF)
lamdaL = input("Last wavelength of the interval (default: 450nm):")
if(lamdaL == ""):
    lamdaL = 450
else:
    lamdaL = int(lamdaL)
gam = input("Guess for gamma (default: 5e-21):")
if(gam == ""):
    gam = 5e-21
else:
    gam = float(gam)

dataRequest = ""
yNumber = []
print("\nProgram has detected that your file has %d data sets\n" % (columns))
while(dataRequest != "x"):
    print("Please select which series to process (enter any other character to exit):")
    print("[ 0 ] ","Wavelength")
    for index in range(len(yData)):
        print("[",index+1,"] ",yData[index].name)
        if(index not in yNumber): yNumber.append(index)
    print("[",index+2,"] ","Print preview of text file for reference")
    yNumber.append(index+1)
    dataRequest = input()
    try:
        dataRequest = int(dataRequest)-1
    except ValueError:
        quit()
    if(dataRequest not in yNumber):
        quit()
    if(dataRequest == len(yData)):
        print("-"*(8*(len(yData)+1)))
        for i in range(len(yData)+1): print(i, end = '\t')
        print()
        print("-"*(8*(len(yData)+1)))
        cmd = subprocess.run(["head", "-10", path], capture_output=True)
        print(cmd.stdout.decode())
    else:
        fano = processData(x, yData[dataRequest].values, lamdaF, lamdaL, gam)
        print(Fore.YELLOW + "\nq = %0.5f\ngamma = %.3e\nx0 = %0.5f\na scalar = %0.5f\nFitness = %0.5f\n" % (fano[0], fano[1], fano[2], fano[5], fano[3]) + Style.RESET_ALL)
