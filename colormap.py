import matplotlib
import matplotlib.pyplot as plt
import random

# We have three dimensions of data. x and y will be plotted on the x and y axis, while z will 
# be represented with color.
# If z is a numpy array, matplotlib refuses to plot this.
x = list(range(300))
y = sorted([random.random()*10 for i in range(300)])
z = list(reversed([i**3 for i in y]))

# cmap will generate a tuple of RGBA values for a given number in the range 0.0 to 1.0 
# (also 0 to 255 - not used in this example).
# To map our z values cleanly to this range, we create a Normalize object.
cmap = matplotlib.cm.get_cmap('viridis')
normalize = matplotlib.colors.Normalize(vmin=min(z), vmax=max(z))
colors = [cmap(normalize(value)) for value in z]

fig, ax = plt.subplots(figsize=(10,10))
ax.scatter(x, y, color=colors)

# Optionally add a colorbar
cax, _ = matplotlib.colorbar.make_axes(ax)
cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize)