# Chris Hogan
# EECS 645
# Project 1
# 12/1/2014

import re

class Pipeline:

	IRegs  = {}
	FPRegs = {}
	Mem    = {}
	Code   = {}

	def __init__(self, data, fileName=True):
		if fileName:
			fileContents = open(data)
		else:
			fileContents = data
		regex = re.compile(r'\s*I-REGISTERS\s*')
		if(regex.match())
			self.populate_iregs(data)

	def populate_iregs(self, data):
		regex = re.compile(r'\s*R[0-31]\s+\d+\s*')
