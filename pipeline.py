# Chris Hogan
# EECS 645
# Project 1
# 12/1/2014

import re

class Pipeline:

    def __init__(self, data, fileName=True):
        
        data_stages = ['IF', 'ID', 'EXE', 'MEM', 'WB']
        add_stages  = ['IF', 'ID', 'A1', 'A2', 'A3', 'A4', 'MEM', 'WB']
        mult_stages = ['IF', 'ID', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'MEM', 'WB']

        self.data_dep = []

        #Initialize all integer registers to zero
        self.IRegs = {}
        for reg_num in range(0,32):
            key = "R%s" % reg_num
            self.IRegs[key] = 0

        #Initialize all floating point registers to zero
        self.FPRegs = {}
        for fp_num in range(0,32):
            key = "F%s" % fp_num
            self.FPRegs[key] = 0

        #Initialize all memory locations to zero
        self.Mem = {}
        for mem_num in range(0, 992, 8):
            key = "%s" % mem_num
            self.Mem[key] = 0

        #Read file into file_contents
        if fileName:
            file_handle = open(data)
            self.file_contents = file_handle.read()
            file_handle.close()
        else:
            self.file_contents = data
        
        self.populate_i_regs()
        self.populate_fp_regs()
        self.populate_mem()
        self.populate_code()

    def populate_i_regs(self):
        int_regex = re.compile(r'(R(?:0|[1-9]|[12][0-9]|3[01]))\s+(\d+)\s*')
        list_of_matches = int_regex.findall(self.file_contents)
        for tup in list_of_matches:
            self.IRegs[tup[0]] = int(tup[1])

    def populate_fp_regs(self):
        fp_regex = re.compile(r'(F(?:0|[1-9]|[12][0-9]|3[01]))\s+((?:\d+\.\d+)|(?:\d+)|(?:\.\d+))\s*')
        list_of_matches = fp_regex.findall(self.file_contents)
        for tup in list_of_matches:
            self.FPRegs[tup[0]] = float(tup[1])

    def populate_mem(self):
        mem_regex = re.compile(r'(\d{1,3})\s*((?:\d+\.\d+)|(?:\d+)|(?:\.\d+))\s*')
        list_of_matches = mem_regex.findall(self.file_contents)
        for tup in list_of_matches:
            self.Mem[tup[0]] = float(tup[1])

    def populate_code(self):
        code_regex = re.compile(r'(L\.D|S\.D|ADD\.D|SUB\.D|MUL\.D)\s+([^\s,]+),\s+([^\s,]+),?(?:\s*([^\sLSAM]+))?\s*')
        self.Code = code_regex.findall(self.file_contents)
        
    def get_data_dependencies(self):
        for i in range(1, len(self.Code)):
            for j in range(0, i):
                if self.Code[i][2] == self.Code[j][1] or self.Code[i][3] == self.Code[j][1]:
                    self.data_dep.append((i, j))
        
    #def execute_instructions(self):


    #def add_stalls(num_stalls, list):
        #for i in range(num_stalls):
            #list[1:1] = ['s']
        #return list