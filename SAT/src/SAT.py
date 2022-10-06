from z3 import *
import os, math, time

def solve():
    
    # first: instantiate a solver
    solver = Solver()
    
    # x_coord boolean variable (2-D matrix)
    x_coord = [[Bool(f"x_coord_{i+1}_{w}")
                for w in range(max_width)]
               for i in range(n_blocks)]
    
    # y_coord boolean variable (2-D matrix)
    y_coord = [[Bool(f"y_coord_{i+1}_{h}")
                for h in range(min_height)] 
               for i in range(n_blocks)]
    
    # variable to encode the relative x position of a rectangle w.r.t another
    left = [[Bool(f"left_{i+1}_{j+1}")
             if i!=j else 0 for j in range(n_blocks)] 
            for i in range(n_blocks)]
    
    # variable to encode the relative y position of a rectangle w.r.t another
    below = [[Bool(f"below_{i+1}_{j+1}")
             if i!=j else 0 for j in range(n_blocks)] 
            for i in range(n_blocks)]
    
    # order encoding constraints
    for i in range(n_blocks):
        # COMMENT
        for w in range(max_width - widths[i], max_width):
            solver.add(x_coord[i][w])
        # COMMENT
        for h in range(min_height - heights[i], min_height):
            solver.add(y_coord[i][h])
        # COMMENT
        for w in range(0, max_width - widths[i]):
            solver.add(Or(
                Not(x_coord[i][w]),
                x_coord[i][w+1])
            )
        # COMMENT
        for h in range(0, min_height - heights[i]):
            solver.add(Or(
                Not(y_coord[i][h]),
                y_coord[i][h+1])
            )
            
    # IDEA: for each pair of rectangles, it must be true that one
    # of the two must be on the left to the other (same for above/below)
    for i in range(n_blocks):
        for j in range(n_blocks):
            # we consider comparisions only when i<j
            if i >= j: continue
            
            solver.add(Or(
                left[i][j],
                left[j][i],
                below[i][j],
                below[j][i]
            ))
    
# ------------------ END FUNCTION --------------------

print("INSTANCE   --   TIME")

n_files = len([f for f in os.listdir("./instances")
               if os.path.isfile(os.path.join("./instances", f))])

# cycle over the list of input files
for i in range(1, n_files+1):
    
    # opening file
    filename = "./instances/ins-{}.txt".format(i)
    file = open(filename)
    
    # max_width
    max_width = int(file.readline())
    
    # n_blocks
    n_blocks = int(file.readline())
    
    # width and height
    widths, heights = [], []
    for line in file:
        splitted = line.split()
        widths.append(int(splitted[0]))
        heights.append(int(splitted[1]))
        
    # defining minimum possible height
    areas = [widths[i] * heights[i] for i in range(n_blocks)]
    min_height = int(math.ceil(sum(areas) / max_width))
    
    # measuring performances of solve
    start_time = time.time()
    # SOLVE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    end_time = time.time()
    
    # printing time performances
    time_spent = end_time - start_time
    print(filename + "\t{:.2f}".format(time_spent))
    
    # converting boolean variables into coordinates for the output
    corner_x, corner_y = [], []
    for i in range(n_blocks):
        x_coord = 0
        while x_coord < max_width:
            # COMPLETE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            pass
        
        y_coord = 0
        while y_coord < min_height:
            # COMPLETE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            pass
    
    # printing output files
    output_filename = "out-{}.txt".format(i)
    output_path = "../out/" + output_filename
    output_file = open(output_path, "w")
    output_file.write(str(max_width) + ' ' + str(min_height) + '\n')
    output_file.write(str(n_blocks) + '\n')
    zipped_data = zip(widths, heights, corner_x, corner_y)
    for(width, height, c_x, c_y) in zipped_data:
        output_file.write(str(width) + ' ' +
                          str(height) + ' ' +
                          str(c_x) + ' ' +
                          str(c_y) + '\n')
    output_file.close()