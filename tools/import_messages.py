#!/usr/bin/python
import json,datetime,sys,os,code

# Setup Django Environment
FILE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(FILE_DIR,'..')
sys.path.append(PROJECT_ROOT) #path to rapid_cold_chain
from django.core.management import setup_environ
from rapid_sms import settings
setup_environ(settings)
# End Django Setup 

import rapidsms.router as router

BACKEND = 'test_backend'
JSON_FILE = os.path.join(FILE_DIR,'messages_fake.json')

def fix_date(message):
	message['date'] = datetime.datetime.strptime(message['date'],'%Y-%m-%d %H:%M:%S')
	return message
	
def send(message,i=0):
	connection = router.lookup_connections(BACKEND,[message['identity']])[0]
	msg_in = router.receive(message['message'],connection)
	msg_in.ccem_msg.created = message['date']
	msg_in.ccem_msg.save()
	print 'Sent',i,':',message['message']
	return msg_in


messages = [fix_date(m) for m in json.load(open(JSON_FILE))]

for i,m in enumerate(messages):
	send(m,i)

code.interact(local=locals())

