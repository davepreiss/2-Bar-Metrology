import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.animation import FuncAnimation
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms
from numpy.random import randn

'''
ToDo:
Colorbar with dynamic max and min sliding
^ Display max and min height values
Option for matrix rotation to get a sense of flatness
    Minimize sum of least squares to fit a plane
Surface of best fit
Resolution heatmap for different linkages

https://brushingupscience.com/2016/06/21/matplotlib-animations-the-easy-way/
https://www.youtube.com/watch?v=cLNOADl17b4&index=10&list=PLQVvvaa0QuDfefDfXb9Yf0la1fPDKluPF
'''

def cartesian(T1,T2):
    case = 1
    A1 = (np.deg2rad(offset1)) - T1/(encoderRes*4) * 2*np.pi # wired backwards
    A2 = (np.deg2rad(offset2)) + T2/(encoderRes*4) * 2*np.pi
    if np.rad2deg(A2) > 180 and np.rad2deg(A2) < 270: # We need to deal with cases where our A2 is greater than 180 and the triangle flips
        A2 = np.deg2rad(180) - (A2 - np.deg2rad(180))
        case = 2
    if np.rad2deg(A2) > 270 and np.rad2deg(A2) < 360:
        A2 = np.deg2rad(360) - A2
        case = 3
    #A1 = np.deg2rad(T1) + np.deg2rad(offset1)
    #A2 = np.deg2rad(T2) + np.deg2rad(offset2)
    dist = (L1**2 + L2**2 -2*L1*L2*np.cos(A2))**(1/2) # Solve for dist with law of cos:
    D2 = np.arccos((dist**2 + L1**2 - L2**2) / (2*dist*L1)) # Solve for D2 with law of cos:
    if case == 1:
        D1 = A1 - D2 # Solve for D1:
    if case == 2: # Here we flip our triangle back
        D1 = A1 + D2 # Solve for D1:
    if case == 3:
        D1 = A1 + D2
        
    xPos = dist*(np.cos(D1)) # Solve for x and y
    yPos = dist*(np.sin(D1))
    xPos2 = L1*np.cos(A1) # Let's also get the x and y position of our first linkage
    yPos2 = L1*np.sin(A1)
    cords = [xPos,yPos,xPos2,yPos2]
    #print(cords)
    return cords

def findMaxMin(xar, yar, zar):
    zMax = max(zar)
    zMin = min(zar)
    
def animate(i):
    # Break all data out into arrays
    pullData = open("Sample1.txt","r").read()
    dataArray = pullData.split('\n')
    # printprint(dataArray)
    dataArray.pop(0) # gets rid of header and can be stored later
    xar = []
    yar = []
    zar = []
    for eachLine in dataArray:
        try: # and eachLine.split(',')[3] != false # <--- We want a way to make sure there's data on the indicator
            unusedTime,alpha,theta,z = eachLine.split(',')
            xar.append(cartesian(float(alpha),float(theta))[0])
            yar.append(cartesian(float(alpha),float(theta))[1])
            zar.append(float(z))
        except:
            pass

    # Scatter plot x y and z data with z corresponding to color
    ax1.clear()
    scat = ax1.scatter(xar, yar, c=zar, cmap='viridis', s=35)

    # Plot linkage Arm Position
    unusedTimeFinal,alphaFinal,thetaFinal,unusedC = dataArray[-2].split(',')
    midX = cartesian(float(alphaFinal),float(thetaFinal))[2]
    midY = cartesian(float(alphaFinal),float(thetaFinal))[3]
    plt.plot([0, midX], [0, midY], 'k-', color='burlywood') # Syntax wants [start x, end x], [start y, end y]
    plt.plot([midX, xar[-1]], [midY, yar[-1]], 'k-', color='burlywood')

    # Find the cells with max/min height and put the max and min values there
    
    maxPos = zar.index(max(zar))
    minPos = zar.index(min(zar))
    ax1.text(xar[maxPos] + 10, yar[maxPos] + 10, "Max (mm): " + str(round(max(zar),3))) # x pos, y pos, value
    ax1.text(xar[minPos] + 10, yar[minPos] + 10, "Min (mm): " + str(round(min(zar),3)))
    
# Start: -----------------------------------------------------------------------
# Had to move all of these out of startPlot because they weren't global and other functions couldn't access
L1 = 262.5 # Lengths of our arms
L2 = 262.5
encoderRes = 2048 # Encoder dependent - quadratures multiply by 4
#offset1 = 196.88 # offset angle in deg
#offset2 = 90
offset1 = 45 # offset angle in deg
offset2 = 180

fig = plt.figure() # Always exists but gives us a variable
ax1 = fig.add_subplot(111)

# def startPlot():
ax1.set_title('2-Bar Metrology')
ax1.set_xlim((-20,525))
ax1.set_ylim((-20,525))

#ax1.set_xlim((-700,700))
#ax1.set_ylim((-525,525))

anim = FuncAnimation(fig, animate, interval=200) # run the animate function every 1000 ms and plot to fig
plt.show()

# if __name__ == '__main__': #means run this first
#     startPlot()

'''
data = np.clip(randn(250, 250), -1, 1)
cax = ax1.imshow(data, interpolation='nearest', cmap='seismic')

Add colorbar, make sure to specify tick locations to match desired ticklabels
cbar = fig.colorbar(cax, ticks=[-.5, 0, .5])
heatmap = ax1.pcolor(data, cmap='seismic')
cbar = plt.colorbar(heatmap)
'''