#!/usr/bin/python
import logging, code
from rapidsms.apps.base import AppBase

from django.utils import translation 

import django_ccem.models as ccem, parser, dhis2.models as dhis2

logger = logging.getLogger(__name__)

class CCEIParser(AppBase):
	
	@classmethod
	def _log(cls,direction,msg):
		'''
		Return an unsaved Message object
		'''
		if not msg.connection:
			raise ValueError
		return ccem.Message(
			direction=direction,
			text=msg.raw_text,
			connection=msg.connection,
		)
	
	def filter(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		# annotate the message as we log them in case any other apps
		# want a handle to them
		
		msg.ccem_msg = self.__class__._log(ccem.Message.INCOMING,msg)
	
	def parse(self,msg):
		'''
		The RapidSMS parse phase: pass the message through the ccem_parser
		Attach result as ccem_parsed
		'''
		#logger.debug('CCEIParser: %s',msg.raw_text)
		msg.ccem_parsed,msg.ccem_error = parser.parse(msg.text)
		msg.ccem_contact = dhis2.Contact.from_connection(msg.connections[0])
		
		#save msg.ccem_msg with data from parsed message
		msg.ccem_msg.is_submission = False if isinstance(msg.ccem_error,parser.utils.NoKeywordError) else True
		msg.ccem_msg.save()
		
	def handle(self,msg):
		
		if msg.ccem_msg.is_submission:
			#The message looks like a report submission. So generate report.
			report = ccem.Report.from_msg(msg)
		language = msg.ccem_contact.language if msg.ccem_contact else 'ka'
		translation.activate(language)
		if not msg.ccem_error: #No other errors
			response = msg.respond(unicode(msg.ccem_parsed))
		else: #there were errors
			response = msg.respond(unicode(msg.ccem_error))
		return True
		
	def outgoing(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		msg.ccem_msg = self.__class__._log(ccem.Message.OUTGOING,msg)
		msg.ccem_msg.save()
		
		#add to correct CCEM Report if it exists
		msg.ccem_report = ccem.Report.add_latest_response(msg)
		
		return True
