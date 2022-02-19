# Fano Fitting

## File Format
This is the most important note on how to use *fano.py*.

Files must be tab separated lists. Files to be used must have their first column be wavelengths (nm). Additional columns will be usable data. 

First row in file must have column names/titles.

These files need to have values separated by **one** tab and **no** spaces.

Tip: open all files in Visual Studio Code and do a *Find and Replace* for any lone space characters or any doubled tab characters.

## Fano equation
## &emsp; $y=\frac{\left[\left(2hc\frac{\left(\frac{1}{\lambda}-\frac{1}{\lambda_0}\right)}{\Gamma}\right)+q\right]^2}{\left(2hc\frac{\left(\frac{1}{\lambda}-\frac{1}{\lambda_0}\right)}{\Gamma}\right)^2+1}$

## Variable types
* $\gamma$ must be positive and on the order of at least $10^{-20}$
* $\lambda_{0}$ must be positive and between the two peaks of the fano curve
* $q$ can be positive or negative but signifies a fano resonance between the values of $[-10,10]$ 

## Fitness Measurement
Fitness is measured as an R $^2$ value where:\
&emsp;R $^2=1-\frac{SSE}{SST}$,\
&emsp;SSE $=\Sigma_i(y_i-\hat{y})^2$,\
&emsp;SST $=\Sigma_i(y_i-\bar{y})^2$.\
R $^2$ is a value between 0 and 1.

## Editing guesses
The *fano.py* uses a computer generation function *scipy.optimize.curve_fit* to find fano parameters. However, the computer requires a guess as an input to give the computation a good starting point. Sometimes these guesses aren't helpful. The only guess that is not entered by the user is $\lambda_{0}$.

The user is asked for a range of wavelengths that encompases the fano resonance. The $\lambda_{0}$ resides in this range and by default, the guess is the average of the wavelengths that bookend the range. This equation can be changed if the computer requires a finer guess for $\lambda_{0}$.

## Graphical integration
This file was originally written in the Jupyter Notebook environment with the intention of using its graphical capabilities. It was later simplified to a *.py* format for practical use. For those who want to graph the fano parameters given by *fano.py*, two options are availible:
1.  Use the equation of a Fano curve to plug in the given parameters and graph it algebraically.
2.  The **processData** function outputs a y data set of the fitted curve. By adding a graphing function to the script, a user can graph that y data set easily and compare it to the original data.
