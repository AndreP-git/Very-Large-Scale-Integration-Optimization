from z3 import *
import time, math

def solve(min_height):
    
    # need a solver (optimizer)
    solver = Optimize()
    
    # setting timeout
    solver.set("timeout", 300000)
    
    # x coordinates
    x_coord = [Int("x_{}".format(i)) for i in range(n_blocks)]
    
    # y coordinates
    y_coord = [Int("y_{}".format(i)) for i in range(n_blocks)]
    
    # constraint on minimum possible height
    min_h = Int("min_height")
    solver.add(min_h == min_height)
    
    # constraints on rectangles position (respecting max dim)
    for i in range(n_blocks):
        solver.add(x_coord[i] >= 0)
        solver.add(y_coord[i] >= 0)
        solver.add(x_coord[i] + widths[i] <= max_width)
        solver.add(y_coord[i] + heights[i] <= min_h)
        
    # non overlapping constraint
    for i in range(n_blocks):
        for j in range(n_blocks):
            if i != j:
                solver.add(Or(
                    Or(
                        x_coord[i] + widths[i] <= x_coord[j],
                        x_coord[j] + widths[j] <= x_coord[i]),
                    Or(
                        y_coord[i] + heights[i] <= y_coord[j],
                        y_coord[j] + heights[j] <= y_coord[i]
                    )
                ))
                
    # symmetry breaking constraints
    solver.add(Implies(
        And(widths[i] == widths[j],
            heights[i] == heights[j]),
        And(x_coord[i] <= x_coord[j],
            Implies(x_coord[i] == x_coord[j],
                    y_coord[i] <= y_coord[j])
            )
        ))
    # solver.add(Implies(
    #     widths[i] + widths[j] > max_width,
    #     And(x_coord[i] + widths[i] > x_coord[j],
    #         x_coord[j] + widths[j] > x_coord[i])
    #     ))
    # solver.add(Implies(
    #     heights[i] + heights[j] > min_height,
    #     And(y_coord[i] + heights[i] > y_coord[j],
    #         y_coord[j] + heights[j] > y_coord[i])
    #     ))
    
    # we try to minimize the minimum possible height
    solver.minimize(min_h)
    
    print(solver.check())
    
    if solver.check() == unsat or solver.check() == unknown:
        return {"solver": -1,
                "x_coord": -1,
                "y_coord": -1}
    
    return {"solver": solver,
            "x_coord": x_coord,
            "y_coord": y_coord}   
    
    
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
    res = solve(min_height)
    end_time = time.time()
    
    # printing time performances
    time_spent = end_time - start_time
    print(filename + "\t{:.2f}".format(time_spent))
    
    # CASE 1: UNSAT (UNTIL TIMEOUT)
    # here we try to solve using the minimum possible height ("min_height")
    # that we increment of 1 unit at each iteration if we get UNSAT
    while res["solver"] == -1 and (end_time-start_time) < 300:
        print(f"min_height={min_height} is too low, let's try +1...")
        min_height += 1
        res = solve(min_height)
        end_time = time.time()
    
    # opening output file
    output_filename = "out-{}.txt".format(i)
    output_path = "../out/" + output_filename
    output_file = open(output_path, "w")
    
    # CASE 2: SAT
    if res["solver"] != -1:
        # printing output files
        output_file.write(str(max_width) + ' ' + str(min_height) + '\n')
        output_file.write(str(n_blocks) + '\n')
        model = res["solver"].model()
        for i in range(1, n_blocks+1):
            output_file.write(str(widths[i-1]) + ' ' +
                            str(heights[i-1]) + ' ' +
                            str(model.evaluate(res["x_coord"][i-1])) + ' ' +
                            str(model.evaluate(res["y_coord"][i-1])) + '\n')
        output_file.close()
    else:
        print("TIMEOUT")
        output_file.write("TIMEOUT")
        output_file.close()