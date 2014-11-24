# Chris Hogan
# EECS 645
# Project 1
# 12/1/2014

import re
import pprint
import pdb

class Pipeline:

    data_stages = {
        1: 'IF',
        2: 'ID',
        3: 'EXE',
        4: 'MEM',
        5: 'WB'
    }

    add_stages  = {
        1: 'IF',
        2: 'ID',
        3: 'A1',
        4: 'A2',
        5: 'A3',
        6: 'A4',
        7: 'MEM',
        8: 'WB'
    }

    mult_stages = {
        1: 'IF',
        2: 'ID',
        3: 'M1',
        4: 'M2',
        5: 'M3',
        6: 'M4',
        7: 'M5',
        8: 'M6',
        9: 'M7',
        10: 'MEM',
        11: 'WB'
    }

    def __init__(self, data, fileName=True):
        
        self.data_dep = []
        self.timing = ""
        self.instructions = {}
        self.cc = 1

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
            key = mem_num
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
        self.populate_instr_types()
        self.num_instructions = len(self.Code)
        self.get_all_data_dependencies()
        self.create_instructions()
        self.execute_instructions()

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
            self.Mem[int(tup[0])] = float(tup[1])

    def populate_code(self):
        self.Code = {}
        code_regex = re.compile(r'(L\.D|S\.D|ADD\.D|SUB\.D|MUL\.D)\s+([^\s,]+),\s+([^\s,]+),?(?:\s*([^\sLSAM]+))?\s*')
        instr_list = code_regex.findall(self.file_contents)
        for i in range(1, len(instr_list) + 1):
            self.Code[i] = instr_list[i - 1]
    
    def populate_instr_types(self):
        self.instr_types = {}
        types = {'ADD.D': 'add', 'SUB.D': 'sub', 'L.D': 'load', 'S.D': 'store', 'MUL.D': 'mult'}
        for i in range(1, len(self.Code) + 1):
            self.instr_types[i] = types[self.Code[i][0]]

    def get_all_data_dependencies(self):
        for i in range(2, len(self.Code) + 1):
            for j in range(1, i):
                if self.Code[i][2] == self.Code[j][1] or self.Code[i][3] == self.Code[j][1]:
                    self.data_dep.append((i, j))
       
    def get_instr_data_dependencies(self, instr):
        deps = []
        for dep in self.data_dep:
            if dep[0] == instr:
                deps.append(dep[1])
        return deps

    def get_stages(self, instr):
        if instr == 'L.D' or instr == 'S.D':
            return Pipeline.data_stages
        elif instr == 'ADD.D' or instr == 'SUB.D':
            return Pipeline.add_stages
        elif instr == 'MUL.D':
            return Pipeline.mult_stages
        else:
            print("Error: Invalid instruction")

    def add_stalls(self, num_stalls, stages):
        for i in range(num_stalls):
            stages[1:1] = ['s']
        return stages
   
    def print_timing(self):
        print("      ", end="")
        for i in range(1, self.num_instructions + 1):
            print("I#%d" % i, end="    ")
        print("")
        for cc in range(1, self.cc + 1):
            print("c#%d" % cc, end="%-3s" % "")
            for instr in range(1, self.num_instructions + 1):
                print("%-7s" % self.instructions[instr]['instr_seq'][cc - 1], end="")
            print("")
        print("")

    def print_registers(self):
        values = ""
        for reg in range(0, 32):
            key = "F%d" % reg
            if self.FPRegs[key] != 0:
                print(key, end="           ")
                values += "%f    " % self.FPRegs[key]
        print("")
        print(values)

    def can_proceed(self, num):
        return True


    def advance_instr(self, num):
        self.instructions[num]['current_stage'] += 1
        stage = self.instructions[num]['current_stage']
        if stage > len(self.instructions[num]['stages']):
            self.instructions[num]['active'] = False
            self.instructions[num]['instr_seq'].append('')
        else:
            self.instructions[num]['instr_seq'].append(self.instructions[num]['stages'][stage])

    def can_fetch(self, num):
        return self.instructions[num-1]['instr_seq'][self.cc-1] == 'ID'


    def create_instructions(self):
        for i in range(1, self.num_instructions + 1):
            self.instructions[i] = {
                'instr': self.Code[i][0],
                'op1': self.Code[i][1],
                'op2': self.Code[i][2],
                'op3': self.Code[i][3],
                'stages': self.get_stages(self.Code[i][0]),
                'current_stage': 0,
                'stalls': 0,
                'active': False,
                'd_dep': self.get_instr_data_dependencies(i),
                'instr_seq': []
            }

    
    def finished(self):
        fin = True
        for i in range(1, len(self.instructions) + 1):
            if 'WB' not in self.instructions[i]['instr_seq']:
                fin = False
        return fin

    def execute_instructions(self):
        while(True):
            for i in range(1, len(self.instructions) + 1):
                if self.instructions[i]['active'] == False:
                    if i == 1:
                        if len(self.instructions[i]['instr_seq']) == 0:
                            self.instructions[i]['instr_seq'].append('IF')
                            self.instructions[i]['active'] = True
                            self.instructions[i]['current_stage'] += 1
                        else:
                            
                            self.advance_instr(i)
                    else:    
                        if self.can_fetch(i):
                            self.instructions[i]['active'] = True
                            self.instructions[i]['current_stage'] += 1
                            self.instructions[i]['instr_seq'].append('IF')
                        else:
                            self.instructions[i]['instr_seq'].append('')
                else:
                    if self.can_proceed(i):
                        self.advance_instr(i)
                    else:
                        self.instructions[i]['instr_seq'].append('')
               
            if self.finished():
                break
            self.cc += 1

            #if self.can_proceed(instr):
                #cur = 0: Can always go to IF => 1
                #cur = 1: IF.  Can go to 2(ID) if this instr has no data dependencies => 2
                #cur = 2: ID.  Can always start execution in next cc => 3
                #cur = 3-9: EXE.  Depends on instruction type. => MEM
                #cur = MEM: Must check waw dependencies and can't write twice in same cc
                #           unless one is a memory write and one is a register write

    