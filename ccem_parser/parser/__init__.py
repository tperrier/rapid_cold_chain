import utils
from tests import *


def get_parser(*args):
	'''
	Return a parser with args as keywords or a parser based on the 
	default keyword list otherwise.
	'''
	import parser as P
	from keywords import KEYWORDS
	
	if len(args)==0:
		return P.Parser(*[kw() for kw in KEYWORDS])
	return P.Parser(args)

default_parser = get_parser()

def parse(msg):
	'''
	@msg: string contents of message to be parsed
	Return:
	- parsed: utils.ParseResult object
	- error: the error thrown or None
	'''
	error = None
	try:
		parsed = default_parser.parse(msg)
	except utils.ParseError as e:
		error = e
		parsed = default_parser.parse(msg,fake=True)
	
	return parsed,error
	
