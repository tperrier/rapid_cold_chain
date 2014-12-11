import argparse
import __init__ as P
import tests

#################
# Argument Parser
#################

ACTION_LIST = ['live','test']

parser = argparse.ArgumentParser()
parser.add_argument('action',default='live',nargs='?',choices=ACTION_LIST)
parser.add_argument('-v','--verbose',action='count',default=0)
parser.add_argument('--valid',action='store_false',default=True)
parser.add_argument('--invalid',action='store_false',default=True)
args =  parser.parse_args()

###################
# Actions 
##################

def live():
	while True:
		message = raw_input('Message: ')
		parsed,error = P.parse(message)
		
		print 'Message: %s'%message
		print 'Parsed: %s'%repr(parsed)
		print 'Error: %s'%error
		print ''
		
def test():
	
	if args.invalid:
		process_messages(tests.VALID_LIST,valid=True)
		
	if args.valid:
		process_messages(tests.INVALID_LIST,valid=False)

def process_messages(messages,valid=True):
	'''
	Process all messages in message list according to valid status
	'''
	
	output('Valid Tests' if valid else 'Invalid Tests')
	valid,invalid = [],[]
	valid_cnt,invalid_cnt = 0,0
	for i,msg in enumerate(messages):
		#Loop through Valid Message Tests 
		parsed,error = P.parse(msg)
		out = '%i: %s '%(i,msg)
		if not error:
			valid.append(out+'OK')
			if args.verbose >= 2:
				valid.append('\t'+repr(parsed))
			valid_cnt += 1
		else:
			invalid.append(out+'ERROR')
			if args.verbose >= 2:
				invalid.append('\t'+str(error))
			invalid_cnt += 1
	
	#Totals For Valid and Invalid
	output('%i failed %i passed of %i'%(invalid_cnt,valid_cnt,invalid_cnt+valid_cnt),tab=1)
	
	#Valid Messages
	if valid:
		output('Valid',level=1 if valid else 0,tab=1)
	for out in valid:
		output(out,tab=2,level=1 if valid else 0)
	
	#Invalid Messages
	if invalid:
		output('Invalid',tab=1,level=0 if valid else 1)
	for out in invalid:
		output(out,tab=2,level=0 if valid else 1)
		
def output(msg,level=0,tab=0):
	if args.verbose >= level:
		print '\t'*tab + msg
		
def output_str(msg,level=0):
	if args.verbose >= level:
		return msg
	return ''
	
locals()[args.action]()
