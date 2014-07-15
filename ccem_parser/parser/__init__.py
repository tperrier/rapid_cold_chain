import utils


def get_parser(*args):
	import parser as P
	if len(args)==0:
		return P.Parser()
	return P.Parser(args)

default_parser = get_parser()
