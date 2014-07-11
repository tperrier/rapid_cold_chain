#!/usr/bin/python

import unittest
import utils

class TestKW(utils.Keyword):
	kw = 'test'

class TestKeyword(unittest.TestCase):
	
	def setUp(self):
		self.result = utils.ParseResult()
		self.kw = TestKW()
		
	def test_result_arg(self):
		self.result.arg(self.kw,(1,2))
		self.assertEqual(self.result.commands,{'test':(1,2)})
		
	def test_result_arg_multiple(self):
		self.result.arg(self.kw,(1,2))
		self.result.arg(self.kw,(3,4))
		self.assertEqual(self.result.commands,{'test':[(1,2),(3,4)]})
	
if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestUtils)
	unittest.TextTestRunner(verbosity=2).run(suite)
