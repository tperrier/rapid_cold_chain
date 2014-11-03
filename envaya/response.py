#python imports
import logging, pprint, json, unittest,code

'''
This module creates an Envaya response object
'''

class EnvayaResponse(object):
	
	def __init__(self,messages=None,log=''):
		self._messages = messages if messages else []
		self._log = log
		
	def add(self,message,to=None,id=None,priority=None):
		new_message = {'message':message}
		
		#add optional arguments
		if to:
			new_message['to'] = to
		if id:
			new_message['id'] = id
		if priority:
			new_message['priority'] = priority
			
		self._messages.append(new_message)
		
	def log(self,log):
		if self.has_log():
			self._log += '\n'
		self._log += log
	
	def has_log(self):
		return bool(self._log)
		
	def to_dict(self):
		response_array = []
		
		if self._messages:
			response_array.append({
				'event':'send',
				'messages':self._messages
			})
			
		if self._log:
			response_array.append({
				'event':'log',
				'message':self._log
			})
			
		return {'events':response_array}
		
	def to_json(self,indent=None):
		return json.dumps(self.to_dict(),indent=indent)
		
	def __len__(self):
		return len(self._messages)
			

class TestEnvayaResponse(unittest.TestCase):
	
	def setUp(self):
		self.basic = EnvayaResponse()
		self.basic.add('Content','1234')
		
	def test_dict(self):
		basic_dict = self.basic.to_dict()
		final_dict = {'events':[{'event':'send','messages':[{'to':'1234','message':'Content'}]}]}
		self.assertEqual(final_dict,basic_dict)
		
	def test_json(self):
		basic_json = self.basic.to_json()
		final_json = '{"events": [{"messages": [{"to": "1234", "message": "Content"}], "event": "send"}]}'
		self.assertEqual(final_json,basic_json)
		
	def test_log(self):
		log = EnvayaResponse()
		log.log('Log Message')
		log_json = log.to_json()
		final_json = '{"events": [{"message": "Log Message", "event": "log"}]}'
		self.assertEqual(final_json,log_json)
		
	def test_id(self):
		self.basic.messages[0]['id']='0000'
		basic_json = self.basic.to_json()
		final_json = '{"events": [{"messages": [{"to": "1234", "message": "Content", "id": "0000"}], "event": "send"}]}'
		self.assertEqual(final_json,basic_json)

if __name__ == '__main__':
	unittest.main()
	
