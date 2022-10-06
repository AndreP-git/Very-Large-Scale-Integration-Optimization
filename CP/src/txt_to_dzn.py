import os

# need a context manager due to error while using "chdir" function
class change_directory:
    def __init__(self, path):
        self.newPath = os.path.expanduser(path)
                  
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# selecting instances dirctory
with change_directory("./instances"):

    # cycling over instances files
    for i in range(1, 41):
        
        # opening file
        filename = "ins-{}.txt".format(i)
        file = open(filename, "r")
        
        # MAX width
        MAX_width = file.readline().rstrip("\n")
        
        # N_blocks
        N_blocks = file.readline().strip("\n")
        
        # Dimensions --> then splitting into "width" and "heights"
        dimensions = [[int(value) for value in line.split()] for line in file]
        widths = str([pair[0] for pair in dimensions])
        heights = str([pair[1] for pair in dimensions])
        
        # closing resources
        file.close()
        
        # new directory to create
        dir_dzn = "../instances_dzn"
        if not os.path.exists(dir_dzn):
            os.makedirs(dir_dzn)
        
        # change directory --> instances_dzn
        with change_directory(dir_dzn):
            
            # selecting filename and opening
            filename = "ins-{}.dzn".format(i)
            file = open(filename, "w")
            
            # writing values
            file.write('max_width = {};\n'.format(MAX_width) +
                     'n_blocks = {};\n'.format(N_blocks) + 
                     'width = {};\n'.format(widths) +
                     'height = {};\n'.format(heights))
            
            # closing resources
            file.close()