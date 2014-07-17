#!/usr/bin/python
import json,datetime,sys,code

# Setup Django Environment
sys.path.append('../') #path to rapid_cold_chain
from django.core.management import setup_environ
from rapid_sms import settings
setup_environ(settings)
# End Django Setup 

import rapidsms.router as router

BACKEND = 'test_backend'

def fix_date(message):
	message['date'] = datetime.datetime.strptime(message['date'],'%Y-%m-%d %H:%M:%S')
	return message
	
def send(message,i):
	connection = router.lookup_connections(BACKEND,[message['connection__identity']])[0]
	router.receive(message['text'],connection)
	print 'Sent',i,':',message['text']


messages = [fix_date(m) for m in json.load(open('messages.json'))]

for i,m in enumerate(messages):
	send(m,i)

code.interact(local=locals())

