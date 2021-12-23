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
    popt_nfano, pcov_nfano = scipy.optimize.curve_fit(nFano, x, y, p0=[gam, x0, q], maxfev=100000)

    #In an effort to create a measure of fitness for each Fano Fit, 
    #we just take the vertical distance between the data point and its position on the fit curve. 
    #Their average is the fitness.
    #A lower fitness score, the better the fit.
    residual = (y - (nFano(x, *popt_nfano)))**2
    fitness = sqrt(average(residual))

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
if(columns == 21):
    fileType = 0 #AverageEspheres
    fileTypeName = "AverageEspheres"
    columnAmount = 4
elif(columns == 13):
    fileType = 1 #AverageEXTABS
    fileTypeName = "AverageEXTABS"
    columnAmount = 8
elif(columns == 10):
    fileType = 2 #Orientation
    fileTypeName = "Orientation"
    columnAmount = 6
else:
    print("Error: File type not supported. Please make sure you are inputting a file of type: AverageEspheres, AverageEXTABS, or Orientation")
    quit()

# This just takes in the data and formats it into a usable array.
# If someone wants to add data that isn't formatted this way, just find which columns from the .txt give the y data and manually add that elif option.
# NOTE: Make sure your file contains ONLY one tab between data points and NO space bars.
# TIP: Open all of your data text files into Visual Studio Code and let it do a system wide "find and replace" for any double tabs or additional sapce bars.
if(fileType == 0):
    x = data[:,0] #Column 0 is always the wavelength #x1a
    yData = []
    yData.append(ySeries(data[:,6], "E^2 on the 1st nanoparticle measured longitudinally"))
    yData.append(ySeries(data[:,10], "E^2 on the 2nd nanoparticle measured longitudinally"))
    yData.append(ySeries(data[:,14], "E^2 on the 1st nanoparticle measured transversely"))
    yData.append(ySeries(data[:,18], "E^2 on the 2nd nanoparticle measured transversely"))
elif(fileType == 1):
    x = data[:,0]  #Column 0 is always the wavelength #x2a
    yData = []
    yData.append(ySeries(data[:,5], "Qext on the 1st nanoparticle measured longitudinally"))
    yData.append(ySeries(data[:,6], "Qabs on the 1st nanoparticle measured longitudinally"))
    yData.append(ySeries(data[:,7], "Qext on the 2nd nanoparticle measured longitudinally"))
    yData.append(ySeries(data[:,8], "Qabs on the 2nd nanoparticle measured longitudinally"))
    yData.append(ySeries(data[:,9], "Qext on the 1st nanoparticle measured transversely"))
    yData.append(ySeries(data[:,10], "Qabs on the 1st nanoparticle measured transversely"))
    yData.append(ySeries(data[:,11], "Qext on the 2nd nanoparticle measured transversely"))
    yData.append(ySeries(data[:,12], "Qabs on the 2nd nanoparticle measured transversely"))
elif(fileType == 2):
    x = data[:,0] #Column 0 is always the wavelength #x3a
    yData = []
    yData.append(ySeries(data[:,1], "Qext measured longitudinally"))
    yData.append(ySeries(data[:,2], "Qabs measured longitudinally"))
    yData.append(ySeries(data[:,3], "Qsca measured longitudinally"))
    yData.append(ySeries(data[:,4], "Qext measured transversely"))
    yData.append(ySeries(data[:,5], "Qabs measured transversely"))
    yData.append(ySeries(data[:,6], "Qsca measured transversely"))
else:
    print("Error: File not formatted correctly.")
    quit()

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
    gam = int(gam)

dataRequest = ""
yNumber = []
print("\nProgram has detected that your file has %d data sets\n" % (columnAmount))
while(dataRequest != "x"):
    print("Please select which series to process (enter any other character to exit):")
    for index in range(0, len(yData)):
        print("[",index,"] ",yData[index].name)
        if(index not in yNumber): yNumber.append(index)
    dataRequest = input()
    try:
        dataRequest = int(dataRequest)
    except ValueError:
        quit()
    if(dataRequest not in yNumber):
        quit()
    fano = processData(x, yData[dataRequest].values, lamdaF, lamdaL, gam)
    print(Fore.YELLOW + "\nq = %0.5f\ngamma = %.3e\nx0 = %0.5f\na scalar = %0.5f\nFitness = %0.5f\n" % (fano[0], fano[1], fano[2], fano[5], fano[3]))
    print(Style.RESET_ALL)