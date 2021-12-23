# User inputs one of the following file types (AverageEsphere, AverageEXTABS, or Orientation)
# System detects which file type it is
    # System will use pandas to read amount of columns in file (AverageEsphere (21), AverageEXTABS (13), or Orientation (10))
# System will load and transform the data into series of lists of the x values and the multiple y values
# While user still wants processing:
    # System will ask (depending on which file type) which data set to be processed
    # User inputs which column to be processed
    # User imputs lamda window (lamdaF and lamdaL) where Fano is found
    # System outputs Fano parameters to user
# User inputs 'x' to exit.

import numpy as np
import pandas as pd
from IPython.display import clear_output
import os
import matplotlib.pyplot as plt
from pylab import *
import scipy.constants as sc
import scipy as scipy
from scipy import optimize
import matplotlib
from matplotlib.ticker import AutoMinorLocator
from matplotlib import gridspec
import matplotlib.ticker as ticker
%matplotlib inline

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
        print("**", end='')

    #outputs q, gamma, x0, fitness, nFano y values, a scalar, original x data, scaled y data (in that order)
    return(popt_nfano[2], popt_nfano[0], popt_nfano[1], fitness, nFano(x, *popt_nfano), poptsFano[3], x, y)

print("Fano Fitting processor\n\nPlease make sure your file is formatted as an output file from the following list:\n\tAverageEsphere\n\tAverageEXTABS\n\tOrientation\n")

# Ask the user for file name of file with Fano data

######
# detect text files in directory
# give user options for which one
######
# return all files as a list
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

filename = input("Please select file number:\t")
path = os.getcwd() + "/" + files[filename] #path of the file
# path = '/Users/brintoneldridge/Downloads/Research/Data/bldrdge1/AverageEXTABS/2nm.txt'
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
    yData.append(ySeries(data[:,6], "E^2 on the 1st Nano Particle longitudinally"))
    yData.append(ySeries(data[:,10], "E^2 on the 2nd Nano Particle longitudinally"))
    yData.append(ySeries(data[:,14], "E^2 on the 1st Nano Particle transversely"))
    yData.append(ySeries(data[:,18], "E^2 on the 2nd Nano Particle transversely"))
elif(fileType == 1):
    x = data[:,0]  #Column 0 is always the wavelength #x2a
    yData = []
    yData.append(ySeries(data[:,5], "Qext on the 1st Nano Particle longitudinally"))
    yData.append(ySeries(data[:,6], "Qabs on the 1st Nano Particle longitudinally"))
    yData.append(ySeries(data[:,7], "Qext on the 2nd Nano Particle longitudinally"))
    yData.append(ySeries(data[:,8], "Qabs on the 2nd Nano Particle longitudinally"))
    yData.append(ySeries(data[:,9], "Qext on the 1st Nano Particle transversely"))
    yData.append(ySeries(data[:,10], "Qabs on the 1st Nano Particle transversely"))
    yData.append(ySeries(data[:,11], "Qext on the 2nd Nano Particle transversely"))
    yData.append(ySeries(data[:,12], "Qabs on the 2nd Nano Particle transversely"))
elif(fileType == 2):
    x = data[:,0] #Column 0 is always the wavelength #x3a
    yData = []
    yData.append(ySeries(data[:,1], "Qext longitudinally"))
    yData.append(ySeries(data[:,2], "Qabs longitudinally"))
    yData.append(ySeries(data[:,3], "Qsca longitudinally"))
    yData.append(ySeries(data[:,4], "Qext transversely"))
    yData.append(ySeries(data[:,5], "Qabs transversely"))
    yData.append(ySeries(data[:,6], "Qsca transversely"))
else:
    print("Error: File not formatted correctly.")
    quit()

# Ask the user to identify the interval in which the user thinks the fano resonance is in
print("Enter 'd' to set value to default.")
lamdaF = input("First wavelength of the interval (default: 350nm):")
if(lamdaF == 'd'):
    lamdaF = 350
else:
    lamdaF = int(lamdaF)
lamdaL = input("Last wavelength of the interval (default: 450nm):")
if(lamdaL == 'd'):
    lamdaL = 450
else:
    lamdaL = int(lamdaL)
gam = input("Guess for gamma (default: 5e-21):")
if(gam == 'd'):
    gam = 5e-21
else:
    gam = int(gam)

dataRequest = ""
print("Program has detected a %s file with %d data sets\n" % (fileTypeName, columnAmount))
while(dataRequest != "x"):
    print("Please select which series to process?")
    for index in range(0, len(yData)):
        print("[",index,"] ",yData[index].name)
    dataRequest = input()
    if(dataRequest == 'x'):
        quit()
    else:
        dataRequest = int(dataRequest)
    fano = processData(x, yData[dataRequest].values, lamdaF, lamdaL, gam)
    print("q = %0.5f" % (fano[0]))
    print("gamma = %.3e" % (fano[1]))
    print("x0 = %0.5f" % (fano[2]))
    print("a scalar = %0.5f" % (fano[5]))
    print("Fitness = %0.5f" % (fano[3]))