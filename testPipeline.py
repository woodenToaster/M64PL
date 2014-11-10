import cutest as unittest
import re
from pipeline import Pipeline

class TestPipeline(unittest.TestCase):

	def testPopulateIRegs(self):
		pipeline = Pipeline('project-input.0.txt')
		self.assertEqual(pipeline.IRegs, {'R2': 16})
