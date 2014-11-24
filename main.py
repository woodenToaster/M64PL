import sys
from pipeline import Pipeline

file_name = input('Enter the name of the input data file:  ')
pipeline = Pipeline(file_name)
timing_file = input('Enter the name of the timing file:  ')
sys.stdout = open(timing_file, 'w')
pipeline.print_timing()
sys.stdout.close()
register_file = input('Enter the name of the register file:  ')
sys.stdout = open(register_file)
pipeline.print_registers()
sys.stdout.close()
