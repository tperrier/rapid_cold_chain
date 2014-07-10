#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.utils import timezone
from rapidsms.apps.base import AppBase
from .models import Message


class MessageLogApp(AppBase):

	@classmethod
	def _log(cls, direction, msg):
		if not msg.contact and not msg.connection:
			raise ValueError
		text = msg.raw_text if direction == Message.INCOMING else msg.text
		return Message.objects.create(
			date=timezone.now(),
			direction=direction,
			text=text,
			contact=msg.contact,
			connection=msg.connection,
		)
	'''
	Moved the message filtering to my own app
	def filter(self, msg):
		#tnp: Moved to filter
		# annotate the message as we log them in case any other apps
		# want a handle to them
		
		msg.logger_msg = self.__class__._log(Message.INCOMING, msg)

	def outgoing(self, msg):
		msg.logger_msg = self.__class__._log(Message.OUTGOING, msg)
	'''
