import matplotlib.pyplot as plt
import numpy as np
import csv

x = []
y = []

'''
with open('Sample1.txt','r') as csvfile:
    plots = csv.reader(csvfile, delimiter = ',')
    for row in plots:
        x.append(int(row[0]))
        y.append(int(row[1]))
plt.plot(x,y)
'''

x,y = np.loadtxt("Sample1.txt", delimiter = ',', unpack = True)
plt.scatter(x,y)
plt.show()