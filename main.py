import sys
from pipeline import Pipeline

file_name = 'project-input.0.txt'#input('Enter the name of the input data file:  ')
pipeline = Pipeline(file_name)
timing_file = 't.1'#input('Enter the name of the timing file:  ')
sys.stdout = open(timing_file, 'w')
pipeline.print_timing()
sys.stdout.close()
register_file = 'r.1'#input('Enter the name of the register file:  ')
sys.stdout = open(register_file, 'w')
pipeline.print_registers()
sys.stdout.close()
