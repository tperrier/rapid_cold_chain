from rapidsms.backends.base import BackendBase
import models as envaya

class EnvayaBackend(BackendBase):
	"""
	Simple backend that saves Envaya Messages in the database
	"""
	
	def send(self,id_,text, identities, context):
		kwargs = {'message_id':id_,'content':text}
		
		for identity in identities:
			kwargs['number'] = identity
			envaya.EnvayaOutgoing.objects.create(**kwargs)
		
		return True
