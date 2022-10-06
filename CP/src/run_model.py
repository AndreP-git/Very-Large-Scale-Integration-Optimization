from datetime import timedelta
import os
import io
import time
from minizinc import Instance, Model, Status, Solver

# utility function to retireve data from txt files
def get_data(res):
    
    # getting model results
    model_results = io.StringIO(str(res))
    
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

# setting model, solver, input directory
model_name = "GECODE.mzn"
solver_name = "gecode"
input_dir = "instances_dzn"

print("INSTANCE   --   TIME")

n_files = len([f for f in os.listdir("./instances_dzn")
               if os.path.isfile(os.path.join("./instances_dzn", f))])

# running solver for each input instance
for i in range(1, n_files+1):
    
    # 1) selecting input file
    input_file = "ins-{}.dzn".format(i)
    filename = "./" + input_dir + "/" + input_file
    
    # 2) setting model
    model = Model("./" + model_name)
    
    # 3) adding input file to the model
    model.add_file(filename)
    
    # 4) setting solver
    solver = Solver.lookup(solver_name)
    
    # 5) setting instance
    instance = Instance(solver, model)
    
    # 6) measuring performances of the solver
    start_time = time.time()
    time_delta = timedelta(seconds=300)
    res = instance.solve(timeout=time_delta)
    end_time = time.time()
    
    # print time performances
    time_spent = end_time-start_time
    print(input_file + "\t" + "{:.2f}sec".format(time_spent))
    
    output_file = open("../out/out-{}.txt".format(i), "w")
    
    # CASE 0: TIMEOUT
    if res.solution is None:
        print("TIMEOUT")
        output_file.write("TIMEOUT")
        output_file.close()
        continue
    
    # CASE 1: UNSATISFIABLE
    if res.status is Status.UNSATISFIABLE:
        print("UNSAT")
        output_file.write("UNSAT")
        output_file.close()
        continue
        
    # CASE 2: SATISFIABLE
    result_data = get_data(res)
    output_file.write(str(result_data['max_width']) + ' ' +
                      str(result_data['max_height']) + '\n')
    output_file.write(str(result_data['n_blocks']) + '\n')
    zipped_data = zip(result_data["widths"],
                      result_data["heights"],
                      result_data["corner_x"],
                      result_data["corner_y"])
    for (width, height, corner_x, corner_y) in zipped_data:
        output_file.write(str(width) + " " +
                          str(height) + " " +
                          str(corner_x) + " " +
                          str(corner_y) + "\n")
    output_file.close()