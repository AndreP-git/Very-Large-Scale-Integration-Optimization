import numpy as np
import matplotlib.patches as ptchs
import matplotlib.pyplot as plt

# utility function to retireve data from txt files
def get_data(path):
    
    # opening target file
    model_results = open(path)
    
    result_collector = {}
    
    # retrieving max_width and max_height
    w_h = model_results.readline().split()
    result_collector['max_width'] = int(w_h[0])
    result_collector['max_height'] = int(w_h[1])
    
    # retrieving number of blocks
    n_blocks = model_results.readline()
    result_collector["n_blocks"] = int(n_blocks)
    
    # retrieving widths, heights, cornerx, cornery
    widths, heights, corner_x, corner_y = [], [], [], []
    for line in model_results:
        splitted = line.split()
        widths.append(int(splitted[0]))
        heights.append(int(splitted[1]))
        corner_x.append(int(splitted[2]))
        corner_y.append(int(splitted[3]))
    result_collector["widths"] = widths
    result_collector["heights"] = heights
    result_collector["corner_x"] = corner_x
    result_collector["corner_y"] = corner_y
    
    # closing resources
    model_results.close()
    
    return result_collector
#---------------------END FUNCTION-------------------------

# selecting file to plot
filename = "out-{}.txt".format(39)
path = "../out/" + filename
results = get_data(path=path)

# splitting results
max_width = results["max_width"]
max_height = results["max_height"]
n_blocks = results["n_blocks"]
heights = results["heights"]
widths = results["widths"]
corner_x = results["corner_x"]
corner_y = results["corner_y"]

# setting corners of rectangles
corners_coord = []
for c_x, c_y in zip(corner_x, corner_y):
    corners_coord.append([c_x, c_y])
    
# setting rectangles dimension
rect_dim = []
for width, height in zip(widths, heights):
    rect_dim.append([width, height])

# setting total
total = ptchs.Rectangle((0,0),
                             width=max_width,
                             height=max_height,
                             edgecolor="r",
                             fill=False)

# need a color map
cmap_name = "viridis"
cmap = plt.cm.get_cmap(cmap_name, n_blocks)

#setting rectangles
rectangles = []
for i in range(0, len(rect_dim)):
    rectangles.append(ptchs.Rectangle((corner_x[i], corner_y[i]),
                                      width=widths[i],
                                      height=heights[i],
                                      facecolor=cmap(i),
                                      edgecolor="black"))

# plots
fig, ax = plt.subplots()
ax.add_patch(total)

for r in rectangles:
    ax.add_patch(r)
    
ax.set_xticks(np.arange(0, max_width+1, 1))
ax.set_yticks(np.arange(0, max_height+1, 1))

ax.set_xlim([0, max_width])
ax.set_ylim([0, max_height])

#plt.grid()
plt.show()