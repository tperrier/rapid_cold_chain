import utils


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
