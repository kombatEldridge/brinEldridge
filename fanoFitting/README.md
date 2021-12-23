# Fano Fitting

## File Format
This is the most important note on how to use *fano.py*.
To begin, there are only three files that are compatible with *fano.py*:
* AverageEspheres.txt
* AverageEXTABS.txt
* Orientation.txt

These three files are outputs of a compiling script and are tab separated values. These files need to have values separated by **one** tab and **no** spaces.

Tip: open all files in Visual Studio Code and do a *Find and Replace* for any lone space characters or any doubled tab characters.

## Adding new file type
For files not of the three given types, it is possible to edit *fano.py* to accomidate the different file type. 
* Make sure to new file is also a text file list of tab separated values. 
* Next, the user must add another possibily of column size. The *fano.py* reads the number of columns in the text file to learn what type it is. Adding a column count for the new file will add it to the list of possible files. 
* Finally, adding the data processing of the columns is the last step. Adding the column index of every important y data set and its name will complete the process.
* In all, follow the format of the current code to insert the new file type.

## Fano equation
## &emsp; $\sigma=\frac{([\frac{2hc(\frac{1}{\lambda}-\frac{1}{\lambda_{0}})}{\gamma}]+q)^2}{1+(\frac{2hc(\frac{1}{\lambda}-\frac{1}{\lambda_{0}})}{\gamma})^2}$

## Variable types
* $\gamma$ must be positive and on the order of at least $10^{-20}$
* $\lambda_{0}$ must be positive and between the two peaks of the fano curve
* $q$ can be positive or negative but signifies a fano resonance between the values of $[-10,10]$ 

## Editing guesses
The *fano.py* uses a computer generation function *scipy.optimize.curve_fit* to find fano parameters. However, the computer requires a guess as an input to give the computation a good starting point. Sometimes these guesses aren't helpful. The only guess that is not entered by the user is $\lambda_{0}$.

The user is asked for a range of wavelengths that encompases the fano resonance. The $\lambda_{0}$ resides in this range and by default, the guess is the average of the wavelengths that bookend the range. This equation can be changed if the computer requires a finer guess for $\lambda_{0}$.

## Graphical integration
This file was originally written in the Jupyter Notebook environment with the intention of using its graphical capabilities. It was later simplified to a *.py* format for practical use. For those who want to graph the fano parameters given by *fano.py*, two options are availible:
1.  Use the equation of a Fano curve to plug in the given parameters and graph it algebraically.
2.  The **processData** function outputs a y data set of the fitted curve. By adding a graphing function to the script, a user can graph that y data set easily and compare it to the original data.