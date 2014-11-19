import cutest as unittest
import re
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

    def testGetDataDependencies(self):
        pipeline = Pipeline('project-input.0.txt')
        pipeline.get_data_dependencies()
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

if __name__ == '__main__':
    unittest.main()




