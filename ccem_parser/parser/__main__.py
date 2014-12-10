import __init__ as P

while True:
	message = raw_input('Message: ')
	parsed,error = P.parse(message)
	
	print 'Message: %s'%message
	print 'Parsed: %s'%repr(parsed)
	print 'Error: %s'%error
	print ''
