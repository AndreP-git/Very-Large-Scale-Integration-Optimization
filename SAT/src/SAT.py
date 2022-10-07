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
            
    # non overlapping constraints x coord
    def build_non_overlap_constraints_x_coord(i,j):
        partial_clause = []
        partial_clause.append([Not(x_coord[j][widths[i] - 1])])
        for w in range(max_width - widths[i] - 1):
            partial_clause.append([x_coord[i][w],
                                   Not(x_coord[j][w + widths[i]])])
        partial_clause.append([x_coord[i][max_width - widths[i] - 1]])
        return partial_clause
    
    for i in range(n_blocks):
        for j in range(i+1, n_blocks):
            
            # CONSTRAINT 1: if rect_i is on the right w.r.t rect_j, we
            # must check if rect_j's x_coordinate does not overlap with rect_i
            for literal in build_non_overlap_constraints_x_coord(i,j):
                clause = [Not(left[i][j])] + literal
                solver.add(Or(clause))
            
            # CONSTRAINT 2: same as CONSTRAINT 1, with i-j swapped
            for literal in build_non_overlap_constraints_x_coord(j,i):
                clause = [Not(left[j][i])] + literal
                solver.add(Or(clause))
    
    # non overlapping constraints y coord
    def build_non_overlap_constraints_y_coord(i,j):
        partial_clause = []
        partial_clause.append([Not(y_coord[j][heights[i] - 1])])
        for h in range(min_height - heights[i] - 1):
            partial_clause.append([y_coord[i][h],
                                   Not(y_coord[j][h + heights[i]])])
        partial_clause.append([y_coord[i][min_height - heights[i] - 1]])
        return partial_clause
    
    for i in range(n_blocks):
        for j in range(i+1, n_blocks):
            
            # CONSTRAINT 3: if rect_i is above rect_j, we
            # must check if rect_j's y_coordinate does not overlap with rect_i
            for literal in build_non_overlap_constraints_y_coord(i,j):
                clause = [Not(below[i][j])] + literal
                solver.add(Or(clause))
            
            # CONSTRAINT 4: same as CONSTRAINT 3, with i-j swapped
            for literal in build_non_overlap_constraints_x_coord(j,i):
                clause = [Not(below[j][i])] + literal
                solver.add(Or(clause)) 
    
    # IDEA: preliminary check on pairs of rectangles, if x_coord_1 + x_coord_2 > max_width,
    # then they cannot stay side by side (same for y_coords)
    for i in range(n_blocks):
        for j in range(i+1, n_blocks):
            
            # x_coord
            if widths[i] + widths[j] > max_width:
                solver.add(And(
                    Not(left[i][j]),
                    Not(left[j][i]))
                )    

            # y_coord
            if heights[i] + heights[j] > min_height:
                solver.add(And(
                    Not(below[i][j]),
                    Not(below[j][i]))
                )
    
    # symmetry breaking constraints
    for i in range(n_blocks):
        for j in range(i+1, n_blocks):
            
            # if rect_1 and rect_2 have the same dimension, than we force rect_1
            # to be on the left to eliminate symmetry (same for below)
            if widths[i] == widths[j] and heights[i] == heights[j]:
                solver.add(Not(left[j][i]))
                solver.add(Or(
                    left[i][j],
                    Not(below[j][i]))
                )
    
    # setting timeout (300s)
    solver.set("timeout", 300000) 
    
    if solver.check() == sat:
        return {"solver": solver,
                "x_coord": x_coord,
                "y_coord": y_coord}
    else: return {"solver": -1,
                "x_coord": -1,
                "y_coord": -1}
    
# ------------------ END FUNCTION --------------------

print("INSTANCE   --   TIME")

n_files = len([f for f in os.listdir("./instances")
               if os.path.isfile(os.path.join("./instances", f))])

# cycle over the list of input files
for i in range(1, 2): #n_files+1
    
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
    res = solve()
    end_time = time.time()
    
    # printing time performances
    time_spent = end_time - start_time
    print(filename + "\t{:.2f}".format(time_spent))
    
    # extracting results
    model = res["solver"].model()
    x_coord = res["x_coord"]
    y_coord = res["y_coord"]
    
    # converting boolean variables into coordinates for the output
    corner_x, corner_y = [], []
    for i in range(n_blocks):
        x = 0
        while x < max_width:
            if model.evaluate(x_coord[i][x]):
                corner_x.append(x)
                break
            x += 1
        
        y = 0
        while y < min_height:
            if model.evaluate(y_coord[i][y]):
                corner_y.append(y)
                break
            y += 1
                
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