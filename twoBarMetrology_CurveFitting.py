#!/usr/bin/evn python

import numpy as np
import scipy.linalg
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms

def pointToPlane(x1,y1,z1,a,b,c,d):
    f = abs((a*x1 + b*y1 + c*z1 + d))  
    e = (np.sqrt(a**2 + b**2 + c**2)) # http://mathworld.wolfram.com/Point-PlaneDistance.html
    distance = f/e
    z = (a*x1 + b*y1 + d)/(-1*c) # we need pos or neg so evaluate z for xy pos and determine if it's greater or less than z1
    if z > z1: 
        distance = distance*-1 # if it's under flip sign
    return distance

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
    dist = (L1**2 + L2**2 -2*L1*L2*np.cos(A2))**(1/2) # Solve for dist with law of cos:
    D2 = np.arccos((dist**2 + L1**2 - L2**2) / (2*dist*L1)) # Solve for D2 with law of cos:
    if case == 1:
        D1 = A1 - D2
    if case == 2: # Here we flip our triangle back
        D1 = A1 + D2
    if case == 3: # Again we are flipping back
        D1 = A1 + D2
        
    xPos = dist*(np.cos(D1)) # Solve for x and y
    yPos = dist*(np.sin(D1))
    xPos2 = L1*np.cos(A1) # Let's also get the x and y position of our first linkage bar
    yPos2 = L1*np.sin(A1)
    cords = [xPos,yPos,xPos2,yPos2]
    return cords
    
# Now we want to pull all of our points and plot them in cartesian space -----------------------------------------------------------------------
L1 = 262.5 # Lengths of our arms
L2 = 262.5
encoderRes = 2048 # Encoder dependent - quadratures multiply by 4
offset1 = 45 # offset angle in deg
offset2 = 180

pullData = open("Sample1.txt","r").read()
dataArray = pullData.split('\n')
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

# For testing this set of arrays creates a thetaX of 45 deg and a thetaY of 0
#xar = [0,0,1,1]
#yar = [0,1,0,1]
#zar = [1,1,0,0]

#xar = [0,0,1,1,.5,.5]
#yar = [0,1,0,1,.5,.5]
#zar = [0,0,0,0,.001,-.002]

data = np.c_[xar,yar,zar] # Get is in proper format for below

# regular grid covering the domain of the data (not sure why this is necessary)
X,Y = np.meshgrid(np.arange(min(xar)-10, max(xar)+10, 0.5), np.arange(min(yar)-10, max(yar)+10, 0.5)) # create arrays from -3 to 3 and increment by 0.5

# best-fit linear plane
A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])] # The .c_ dictates which axis you join along?
C,residual,_,_ = scipy.linalg.lstsq(A, data[:,2])    # gives the coefficients - the undersocres are just a way to ignore data you don't care about (so this function returns 4 things but we only care about one and will ignore the rest)
# evaluate it on grid
Z = C[0]*X + C[1]*Y + C[2] # This is the equation of our plane of best fit where normal vector has coefs. C0-2

# Point to plane for every point
P2PDistances = []
for q,row in enumerate(data): # Step through data, keep track of row with i, and enumerate is what steps through 1 line at a time
    D1 = pointToPlane(data[q][0],data[q][1],data[q][2],C[0],C[1],-1,C[2])
    P2PDistances.append(D1)
print(max(P2PDistances),min(P2PDistances))
max([max(P2PDistances),abs(min(P2PDistances))])
# print(np.average(P2PDistances)) # This is a good way to check the quality of our fit (should be very close to zero)

# Now lets find the angle by which our normal vector is off in x and y (remember formula is spit out in weird format with z coef. at -1)
thetaY = np.arctan(C[0]*-1)
thetaX = np.arctan(C[1]*-1)

# Here we are creating rotation matrices Rx and Ry for rotating points in data about the x and y axes
cx, sx = np.cos(thetaX), np.sin(thetaX)
cy, sy = np.cos(thetaY), np.sin(thetaY)
Rx = np.array(((1,0,0), (0,cx,-sx), (0,sx,cx)))
Ry = np.array(((cy,0,sy), (0,1,0), (-sy,0,cy)))

'''
# Now let's make a new dataset with everything rotated:
print(data[0])
dataRotated = data
for i,row in enumerate(data): # Step through data, keep track of row with i, and enumerate is what steps through 1 line at a time
    dataRotated[i] = np.matmul(data[i],Rx)
data = dataRotated
#print(data)
'''

# 3D plot of points and fitted surface
fig1 = plt.figure(1)
ax1 = fig1.gca(projection='3d')

ax1.plot_surface(X, Y, Z, rstride=10, cstride=10, alpha=.2)
ax1.scatter(data[:,0], data[:,1], data[:,2], c='r', s=50)
plt.xlabel('X (mm)')
plt.ylabel('Y (mm)')
ax1.set_zlabel('Z (mm)') 
ax1.axis('equal')
ax1.axis('tight')
label1 = 'Parallelism within: ' + str(round(max(zar) + abs(min(zar)),3)) + ' mm\n' + 'Theta X: ' + str(round(np.rad2deg(thetaX),2)) + '\xb0 \n' + 'Theta Y: ' + str(round(np.rad2deg(thetaY),2)) + '\xb0' + '\n' + 'Flatness within: ' + str(round(max(P2PDistances) + abs(min(P2PDistances)),4)) + ' mm'
ax1.text2D(0.05, .95, label1, transform=ax1.transAxes)

# Histogram of points to plane
fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111)

plt.hist(P2PDistances, normed=False, bins=30, color = "lightcoral", lw=1, ec="r")
ax2.set_facecolor('aliceblue')
ax2.set_title('Point to Plane Distances')
plt.xlabel('Distance (mm)')
plt.ylabel('Quantity out of ' + str(len(P2PDistances))+ ' points')

plt.show()