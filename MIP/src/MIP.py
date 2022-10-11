import pulp, math, os, time, mosek
import numpy as np

def build_pulp_model(max_width, n_blocks, widths, heights):
    
    # defining the model
    model = pulp.LpProblem("vlsi", pulp.LpMinimize)
    
    # bounds for the height
    lower_bound = max(
        max(heights),
        math.ceil(sum([widths[i] * heights[i] for i in range(n_blocks)]) / max_width)
    )
    upper_bound = int(sum(heights))

    # defining height variable
    height = pulp.LpVariable("height",
                        lowBound=lower_bound,
                        upBound=upper_bound,
                        cat=pulp.LpInteger)
    model += height, "height"

    # defining coordinates variables for rectangles
    x_coord = [pulp.LpVariable("x_{}".format(i), 
                               lowBound=0, 
                               upBound=int(max_width- widths[i]), 
                               cat=pulp.LpInteger)
               for i in range(n_blocks)]
    
    y_coord = [pulp.LpVariable("y_{}".format(i),
                               lowBound=0,
                               upBound=int(upper_bound - heights[i]),
                               cat=pulp.LpInteger)
                for i in range(n_blocks)]

    # height constraint
    for i in range(n_blocks):
        model += y_coord[i] + heights[i] <= height, "height boundary r_{}".format(i)

    # delta value
    delta = pulp.LpVariable.dicts(
        "delta",
        indices=(range(n_blocks), range(n_blocks), range(2)),
        cat=pulp.LpBinary,
        lowBound=0,
        upBound=1,
    )

    # IDEA: trying to check whether placing the rectangle
    # with the biggest area in position (0,0) helps the solver
    widths_arr = np.asarray(widths)
    heights_arr = np.asarray(heights)
    biggest_rect_idx = np.argmax(widths_arr * heights_arr)
    model += x_coord[biggest_rect_idx] == 0, "biggest x_coord"
    model += y_coord[biggest_rect_idx] == 0, "biggest y_coord"

    # non overlapping constraints
    for i in range(n_blocks):
        for j in range(n_blocks):
            if i < j:
                
                # COMMENTTTTTTTTTTTTT
                if widths[i] + widths[j] > max_width:
                    model += delta[i][j][0] == 1
                    model += delta[j][i][0] == 1

                # COMMENTTTTTT
                model += x_coord[i] + widths[i] <= x_coord[j] + (delta[i][j][0]) * max_width
                
                # COMMENTTTTTT
                model += x_coord[j] + widths[j] <= x_coord[i] + (delta[j][i][0]) * max_width
                
                # COMMENTTTTTT
                model += y_coord[i] + heights[i] <= y_coord[j] + (delta[i][j][1]) * upper_bound
                
                # COMMENTTTTTT
                model += y_coord[j] + heights[j] <= y_coord[i] + (delta[j][i][1]) * upper_bound
                
                # COMMENTTTTTT
                model += (delta[i][j][0] + delta[j][i][0] + delta[i][j][1] + delta[j][i][1] <= 3 )

    return model

# ------------------ END FUNCTION ----------------------------

def build_pulp_model_rot(max_width, n_blocks, widths, heights):
    
    # define the model
    model = pulp.LpProblem("vlsi-with-rotation", pulp.LpMinimize)

    # bounds for the height
    lower_bound = max(
        max([min(widths[i], heights[i]) for i in range(n_blocks)]),
        math.ceil(sum([widths[i] * heights[i] for i in range(n_blocks)]) / max_width))
    upper_bound = int(sum([max(heights[i], widths[i]) for i in range(n_blocks)]))

    # defining height variable
    height = pulp.LpVariable("height",
                             lowBound=lower_bound,
                             upBound=upper_bound,
                             cat=pulp.LpInteger)
    model += height, "height"

    # defining coordinates variables for rectangles
    x_coord = [pulp.LpVariable("x_{}".format(i),
                               lowBound=0,
                               upBound=int(max_width - min(widths[i], heights[i])),
                               cat=pulp.LpInteger)
               for i in range(n_blocks)]
    
    y_coord = [pulp.LpVariable("y_{}".format(i),
                               lowBound=0,
                               upBound=int(upper_bound - min(widths[i], heights[i])),
                               cat=pulp.LpInteger)
               for i in range(n_blocks)]

    # rotation auxiliary variable
    rotation = pulp.LpVariable.dicts("rot",
                                     indices=range(n_blocks),
                                     lowBound=0,
                                     upBound=1,
                                     cat=pulp.LpBinary)

    # IDEA 1: if the height of a rectangle is greater than max_width,
    # it must not be allowed to be rotated since it would not fit
    for i in range(n_blocks):
        if heights[i] > max_width:
            rotation[i] = 0
    
    # IDEA 2: if a piece is squared, rotating it would be useless
    for i in range(n_blocks):
        if widths[i] == heights[i]:
            rotation[i] = 0

    # width boundary constraint
    for i in range(n_blocks):
        model += (x_coord[i] + widths[i] * (1 - rotation[i]) +
                  heights[i] * rotation[i] <= max_width,
            "width boundary r_{}".format(i))
        
    # height boundary constraint
    for i in range(n_blocks):
        model += (y_coord[i] + heights[i] * (1 - rotation[i]) +
                  widths[i] * rotation[i] <= height,
            "height boundary r_{}".format(i))

    # delta value 
    delta = pulp.LpVariable.dicts(
        "delta",
        indices=(range(n_blocks), range(n_blocks), range(2)),
        cat=pulp.LpBinary,
        lowBound=0,
        upBound=1,
    )
    
    # IDEA 3: trying to check whether placing the rectangle
    # with the biggest area in position (0,0) helps the solver
    widths_arr = np.asarray(widths)
    heights_arr = np.asarray(heights)
    biggest_rect_idx = np.argmax(widths_arr * heights_arr)
    model += x_coord[biggest_rect_idx] == 0, "biggest x_coord"
    model += y_coord[biggest_rect_idx] == 0, "biggest y_coord"

    # non overlapping constraints
    for i in range(n_blocks):
        for j in range(n_blocks):
            if i < j:
                
                # COMMENTTTTTTTT
                if all([(u + v) > max_width
                        for u in [widths[i], heights[i]]
                        for v in [widths[j], heights[i]]]):
                    model += delta[i][j][0] == 1
                    model += delta[j][i][0] == 1

                # x axis i-j
                model += (x_coord[i] + widths[i] * (1 - rotation[i]) +
                          heights[i] * rotation[i] <=
                          x_coord[j] + delta[i][j][0] * max_width)
                
                # x axis j-i
                model += (x_coord[j] + widths[j] * (1 - rotation[j]) +
                          heights[j] * rotation[j] <=
                          x_coord[i] + delta[j][i][0] * max_width)

                # y axis i-j
                model += (y_coord[i] + heights[i] * (1 - rotation[i]) +
                          widths[i] * rotation[i] <=
                          y_coord[j] + delta[i][j][1] * upper_bound)
                
                # y axis j-i
                model += (y_coord[j] + heights[j] * (1 - rotation[j]) +
                          widths[j] * rotation[j] <=
                          y_coord[i] + delta[j][i][1] * upper_bound)

                # COMMENTTTTTT
                model += (delta[i][j][0] + delta[j][i][0] + delta[i][j][1] + delta[j][i][1] <= 3)

    return model

# ------------------ END FUNCTION ----------------------------

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
        
    # model selection
    model_name = "base" # base | rot
    if model_name == "base":
        model = build_pulp_model(max_width, n_blocks, widths, heights)
    else:
        model = build_pulp_model_rot(max_width, n_blocks, widths, heights)

    # solver selection
    solver_name = "cplex" # cplex | mosek
    if solver_name == "cplex":
        solver = pulp.CPLEX_CMD(mip=True,
                                msg=False,
                                timeLimit=300)
    else:
        solver = pulp.MOSEK(mip=True,
                            msg=False,
                            options={mosek.dparam.mio_max_time: 300})
    
    # measuring performances of solve
    start_time = time.time()
    model.solve(solver)
    end_time = time.time()
    
    # printing time performances
    time_spent = end_time - start_time
    print(filename + "\t{:.2f}".format(time_spent))
    
    output_filename = "out-{}.txt".format(i)
    output_path = "../out/" + output_filename
    output_file = open(output_path, "w")
    
    result = {}
    
    if model.objective == None:
        output_file.write("TIMEOUT")
        continue
    
    result["height"] = round(pulp.value(model.objective))
    rotation = [False] * n_blocks
    coordinates = {"x": [None] * n_blocks,
                   "y": [None] * n_blocks}
    for var in model.variables():
        #print(f"{v.name}: {v.value()}")
        if str(var.name).startswith("x_"):
            coordinates["x"][int(var.name[2:])] = round(var.varValue)
        elif str(var.name).startswith("y_"):
            coordinates["y"][int(var.name[2:])] = round(var.varValue)
        elif str(var.name).startswith("rot"):
            rotation[int(var.name[4:])] = bool(round(var.varValue))

    result["coords"] = coordinates
    result["rotation"] = rotation if model_name == "rot" else None
    
    #print(result)
    
    # printing output files
    output_file.write(str(max_width) + ' ' + str(result["height"]) + '\n')
    output_file.write(str(n_blocks) + '\n')
    zipped_data = zip(widths, heights, result["coords"]["x"], result["coords"]["y"])
    for(width, height, c_x, c_y) in zipped_data:
        output_file.write(str(width) + ' ' +
                          str(height) + ' ' +
                          str(c_x) + ' ' +
                          str(c_y) + '\n')
    output_file.close()