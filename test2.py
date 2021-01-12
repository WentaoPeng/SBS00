import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from scipy.signal import find_peaks

# 洛伦兹拟合光谱

def lorentzian( x, x0, a, gam ):
    return a * gam**2 / ( gam**2 + ( x - x0 )**2 )

def multi_lorentz( x, params ):
    off = params[0]
    paramsRest = params[1:]
    assert not ( len( paramsRest ) % 3 )
    return off + sum( [ lorentzian( x, *paramsRest[ i : i+3 ] ) for i in range( 0, len( paramsRest ), 3 ) ] )

def res_multi_lorentz( params, xData, yData ):
    diff = [ multi_lorentz( x, params ) - y for x, y in zip( xData, yData ) ]
    return diff

y0 = np.loadtxt( 'y_peo.tsv' )
yData = np.loadtxt( 'y_peo.tsv' )
xData = np.arange( len( yData ) )

yGround = min( yData )
yData = yData - yGround
yAmp = max( yData )
yData = yData / yAmp

#initial properties of peaks
pk, properties = find_peaks( yData, height = .05, width = 3 )#, prominence=0.1 )
#extract peak heights and fwhm
I = properties [ 'peak_heights' ]
fwhm = properties[ 'widths' ]

guess = [0]
for i in range( len( pk ) ):
    guess.append( pk[i] )
    guess.append( I[i] )
    guess.append( fwhm[i] )

guess=np.array( guess )

popt, pcov = leastsq( res_multi_lorentz, x0=guess, args=( xData, yData ) )
print( popt )


testData = [ multi_lorentz( x, popt ) for x in xData ]
fitData = [ yGround + yAmp * multi_lorentz( x, popt ) for x in xData ]

fig= plt.figure( figsize=( 10, 5 ) )
ax= fig.add_subplot( 2, 1, 1 )
bx= fig.add_subplot( 2, 1, 2 )
ax.plot( pk, yData[pk], 'o', ms=5 )
ax.plot( xData, yData, 'ok', ms=1 )
ax.plot( xData, testData , 'r--', lw=0.5 )
bx.plot( xData, y0, ls='', marker='o', markersize=1 )
bx.plot( xData, fitData )
plt.show()