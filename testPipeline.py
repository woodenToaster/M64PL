import cutest as unittest
import re
import sys
import os
import pdb
from pipeline import Pipeline

class TestPipeline(unittest.TestCase):

    def testPipelineInit(self):
        pipeline = Pipeline('project-input.0.txt')
        self.assertEqual(pipeline.IRegs['R2'], 16)
        self.assertEqual(pipeline.Mem[16], 12.5)
        self.assertEqual(pipeline.Mem[8], 17.8)
        self.assertEqual(pipeline.Mem[0], 4.0)
        self.assertEqual(pipeline.Code[1], ('L.D', 'F1', '0(R2)', ''))
        self.assertEqual(pipeline.Code[2], ('L.D', 'F2', '-8(R2)', ''))
        self.assertEqual(pipeline.Code[3], ('MUL.D', 'F3', 'F2', 'F1'))
        self.assertEqual(pipeline.Code[4], ('S.D', '0(R2)', 'F3', ''))
        self.assertEqual(pipeline.Code[5], ('L.D', 'F3', '-16(R2)', ''))
        self.assertEqual(pipeline.Code[6], ('MUL.D', 'F1', 'F2', 'F3'))
        self.assertEqual(pipeline.Code[7], ('S.D', '-8(R2)', 'F3', ''))
        self.assertEqual(pipeline.Code[8], ('ADD.D', 'F4', 'F1', 'F2'))

    def testIntRegsInitializeToZero(self):
        pipeline = Pipeline('', False)
        vals = pipeline.IRegs.values()
        self.assertTrue(all(i == 0 for i in vals))

    def testFpRegsInitializeToZero(self):
        pipeline = Pipeline('', False)
        vals = pipeline.FPRegs.values()
        self.assertTrue(all(i == 0 for i in vals))

    def testMemLocationsInitToZero(self):
        pipeline = Pipeline('', False)
        vals = pipeline.Mem.values()
        self.assertTrue(all(i == 0 for i in vals))

    def testPopulateIRegs(self):
        pipeline = Pipeline("R2 16\n    \t\r       R3       \t24\t\t\r\n", False)
        self.assertEqual(pipeline.IRegs['R2'], 16)
        self.assertEqual(pipeline.IRegs['R3'], 24)

    def testPopulateFPRegs(self):
        pipeline = Pipeline("F31 67.89\n  F0  \t.3986\nF30    5\n", False)
        self.assertEqual(pipeline.FPRegs['F31'], 67.89)
        self.assertEqual(pipeline.FPRegs['F0'], 0.3986)
        self.assertEqual(pipeline.FPRegs['F30'], 5.0)

    def testPopulateMem(self):
        pipeline = Pipeline("16 12.5\n8 17.8\t\n0\t4\n352\n269.985", False)
        self.assertEqual(pipeline.Mem[352], 269.985)
        self.assertEqual(pipeline.Mem[16], 12.5)
        self.assertEqual(pipeline.Mem[8], 17.8)
        self.assertEqual(pipeline.Mem[0], 4.0)

    def testPopulateCode(self):
        pipeline = Pipeline("ADD.D F1, F2, F3\nL.D  \tF1,   0(R2)\n\n", False)
        self.assertEqual(pipeline.Code[1], ('ADD.D', 'F1', 'F2', 'F3'))
        self.assertEqual(pipeline.Code[2], ('L.D', 'F1', '0(R2)', ''))

    def testPopulateInstrTypes(self):
        pipeline = Pipeline("ADD.D F1, F2, F3\nSUB.D F1, F2, F3\nL.D F1, 0(R2)\nS.D 0(R2), F1\nMUL.D F2, F3, F4\n", False)
        self.assertEqual(pipeline.instr_types[1], 'add')
        self.assertEqual(pipeline.instr_types[2], 'sub')
        self.assertEqual(pipeline.instr_types[3], 'load')
        self.assertEqual(pipeline.instr_types[4], 'store')
        self.assertEqual(pipeline.instr_types[5], 'mult')

    def testGetAllDataDependencies(self):
        pipeline = Pipeline('project-input.0.txt')
        pipeline.get_all_data_dependencies()
        self.assertEqual(pipeline.data_dep[0], (3,1))
        self.assertEqual(pipeline.data_dep[1], (3,2))
        self.assertEqual(pipeline.data_dep[2], (4,3))
        self.assertEqual(pipeline.data_dep[3], (6,2))
        self.assertEqual(pipeline.data_dep[4], (6,3))
        self.assertEqual(pipeline.data_dep[5], (6,5))
        self.assertEqual(pipeline.data_dep[6], (7,3))
        self.assertEqual(pipeline.data_dep[7], (7,5))
        self.assertEqual(pipeline.data_dep[8], (8,1))
        self.assertEqual(pipeline.data_dep[9], (8,2))
        self.assertEqual(pipeline.data_dep[10], (8,6))

    def testGetInstrDataDependencies(self):
        pipeline = Pipeline("L.D F1, 0(R2)\nADD.D F1, F2, F3\nMUL.D F3, F1, F2\n", False)
        pipeline2 = Pipeline("L.D F6, 0(R2)\nADD.D F1, F2, F3", False)
        self.assertEqual(pipeline.get_instr_data_dependencies(3), [1, 2])
        self.assertEqual(pipeline2.get_instr_data_dependencies(2), [])

    def testGetStages(self):
        pipeline = Pipeline("L.D F1, 0(R2)\nADD.D F2, F3, F4\nMUL.D F2, F3, F4\n", False)
        self.assertEqual(pipeline.get_stages(pipeline.Code[1][0]), Pipeline.data_stages)
        self.assertEqual(pipeline.get_stages(pipeline.Code[2][0]), Pipeline.add_stages)
        self.assertEqual(pipeline.get_stages(pipeline.Code[3][0]), Pipeline.mult_stages)

    def testCreateInstructions(self):
        pipeline = Pipeline("L.D F0, 0(R2)\n", False)
        expected = {
            'instr': 'L.D',
            'op1': 'F0',
            'op2': '0(R2)',
            'op3': '',
            'stages': Pipeline.data_stages,
            'current_stage': 0,
            'executed': False,
            'stalls': 0,
            'active': False,
            'd_dep': [],
            'w_dep': [],
            'instr_seq': []
        }
        self.assertEqual(pipeline.instructions[1], expected)

    def testAddStalls(self):
        pipeline = Pipeline('', False)
        expected = pipeline.add_stalls(3, ['IF', 'ID', 'A1', 'A2', 'A3', 'A4', 'MEM', 'WB'])
        self.assertEqual(expected, ['IF', 's', 's', 's', 'ID', 'A1', 'A2', 'A3', 'A4', 'MEM', 'WB'])

    def testPrintRegisters(self):
        pipeline = Pipeline('', False)
        pipeline.FPRegs['F25'] = 15
        pipeline.FPRegs['F2'] = 15.89
        pipeline.FPRegs['F7'] = 78.56
        sys.stdout = open('test.1', 'w')
        pipeline.print_registers()
        sys.stdout.close()
        reg_file = open('test.1')
        file_contents = reg_file.read()
        self.assertEqual(file_contents, "F2        F7        F25       \n15.89     78.56     15        \n")
        reg_file.close()                              
        try:
            os.remove('test.1')
        except OSError:
            pass

    def testAddInitialStages(self):
        pipeline = Pipeline('project-input.0.txt')
        pipeline.instructions[1]['instr_seq'].extend(pipeline.instructions[1]['stages'].values())
        self.assertEqual(pipeline.instructions[1]['instr_seq'], ['IF', 'ID', 'EXE', 'MEM', 'WB'])

    def testAddInstr(self):
        pipeline = Pipeline('ADD.D F1, F2, F3', False)
        pipeline.FPRegs['F2'] = 2
        pipeline.FPRegs['F3'] = 2
        pipeline.add_instr(1)
        self.assertEqual(pipeline.FPRegs['F1'], 4)

    def testAddWithIRegs(self):
        pipeline = Pipeline('ADD.D R1, R2, R3', False)
        pipeline.IRegs['R2'] = 2
        pipeline.IRegs['R3'] = 2
        pipeline.add_instr(1)
        self.assertEqual(pipeline.IRegs['R1'], 4)

    def testSubInstr(self):
        pipeline = Pipeline('ADD.D F1, F2, F3', False)
        pipeline.FPRegs['F2'] = 2
        pipeline.FPRegs['F3'] = 2
        pipeline.sub_instr(1)
        self.assertEqual(pipeline.FPRegs['F1'], 0)

    def testMultInstr(self):
        pipeline = Pipeline('ADD.D F1, F2, F3', False)
        pipeline.FPRegs['F2'] = 2
        pipeline.FPRegs['F3'] = 3
        pipeline.mult_instr(1)
        self.assertEqual(pipeline.FPRegs['F1'], 6)

    def testOffsetRegex(self):
        osRegex = re.compile(r'(\d+)\(')
        res = int(osRegex.match('16(R2)').group(1))
        self.assertEqual(res, 16)
        res = int(osRegex.match('0(R2)').group(1))
        self.assertEqual(res, 0)

    def testRegisterRegex(self):
        regRegex = re.compile(r'\((.+)\)')
        res = regRegex.search('16(R21)')
        self.assertEqual(res.group(1), 'R21')

    def testLoadInstr(self):
        pipeline = Pipeline('L.D F1, 16(R1)', False)
        pipeline.IRegs['R1'] = 8
        pipeline.Mem[24] = 5
        pipeline.ld_instr(1)
        self.assertEqual(pipeline.FPRegs['F1'], 5)

    def testLoadInstrIRegs(self):
        pipeline = Pipeline('L.D R2, 16(R1)', False)
        pipeline.IRegs['R1'] = 8
        pipeline.Mem[24] = 5
        pipeline.ld_instr(1)
        self.assertEqual(pipeline.IRegs['R2'], 5)

    def testStInstr(self):
        pipeline = Pipeline('S.D 16(R1), F1', False)
        pipeline.IRegs['R1'] = 16
        pipeline.FPRegs['F1'] = 5
        pipeline.st_instr(1)
        self.assertEqual(pipeline.Mem[32], 5)

    def testStInstrIRegs(self):
        pipeline = Pipeline('S.D 16(R1), R2', False)
        pipeline.IRegs['R1'] = 16
        pipeline.IRegs['R2'] = 5
        pipeline.st_instr(1)
        self.assertEqual(pipeline.Mem[32], 5)

    def testGetAllWriteDependencies(self):
        pipeline = Pipeline('project-input.0.txt')
        self.assertEqual(pipeline.instructions[5]['w_dep'], [3])
        self.assertEqual(pipeline.instructions[6]['w_dep'], [1])

if __name__ == '__main__':
    unittest.main()




