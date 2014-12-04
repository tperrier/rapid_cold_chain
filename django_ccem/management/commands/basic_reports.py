from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

#CCEM
from dhis2 import models as dhis2
from django_ccem import models as ccem

#Python Imports
import code,datetime

'''
Command to produce basic reports of messages sent
'''

class Command(BaseCommand):
	
	help = 'show monthly report usage per facility'

	action_list = ['summary','facilities']
	
	option_list = BaseCommand.option_list + (
		#make_option('-s','--send',help='send messages',action='store_true',default=False),
		#make_option('--silent',help='don\t print output',action='store_true',default=False),
		make_option('-a','--action',help='action to preform',choices=action_list,default='summary'),
		make_option('-m','--month',help='month for reporting',default=None),
		make_option('-y','--year',help='year for reporting',default=None),
		make_option('-f','--file_out',help='output file for csv',default=None),
	)
	
	
	
	def handle(self,*args,**kwargs):
		if kwargs['action'] == 'summary':
			self.non_reporting_summary(**kwargs)
		elif kwargs['action'] == 'facilities':
			self.facility_report(**kwargs)
		
	def non_reporting_summary(self,month=None,year=None,**kwargs):
		'''
		Print basic non reporting report
		'''
		month,year = get_month_year(month,year)
		print "Reporting Summary"
		
		messages = ccem.Message.objects.filter(created__month=month,created__year=year,direction='I')
		msg_count = messages.count()
		print 'Messages: {} A({})'.format(msg_count,messages.filter(connection__dhis2__isnull=True).count())
		
		reports = ccem.Report.objects.filter(created__month=month,created__year=year)
		report_count = reports.count()
		print 'Reports: {} ({}) A({})'.format(report_count,msg_count-report_count,reports.filter(message__connection__dhis2__isnull=True).count())
		
		valid_count = reports.filter(has_error=False).count()
		print 'Valid: {} ({}) A({})'.format(valid_count,report_count-valid_count,
			reports.filter(has_error=True,message__connection__dhis2__isnull=True).count())
		
		print "\nNot Reporting"
		for i,f in enumerate(dhis2.Facility.objects.non_reporting()):
			print '{} {}'.format(i,f.i18n_name['ke'])
		
					
	def facility_report(self,month=None,year=None,**kwargs):
		districts = dhis2.Facility.objects.facility_groups()
		for district,facilities in districts.iteritems():
			d_str = str(district.i18n_name['ke'])
			f_count = len(facilities)
			report_count = sum([reporting(f,month,year) for f in facilities])
			
			#Print District and summary
			print "{0}: {1} of {2} reporting".format(d_str,report_count,f_count)
			
			#Print None Reporint Districts
			for facility in facilities:
				invalid_cnt = reports_by_month(facility,month,year,valid=True)
				report_cnt = reports_by_month(facility,month,year)
				print '\t{}{} {} of {}'.format(
					'*' if report_cnt==0 else '',
					facility.i18n_name['ke'],
					invalid_cnt,report_cnt )

###################
# Utility Functions 
###################

def get_month_year(month,year):
	today = datetime.date.today()
	if not (month and month >= 1 and month <= 12):
		month = today.month
	if not year:
		year = today.year
	return month,year
		
def reports_by_month(facility,month=None,year=None,valid=False):
	'''
	Return the number of reports for the given month
	'''
	month,year = get_month_year(month,year)
	if not valid:
		return facility.report_set.filter(created__month=month,created__year=year).count()
	return facility.report_set.filter(created__month=month,created__year=year,has_error=True).count()

def reporting(facility,month=None,year=None):
	'''
	Returns 1 if facility reported in the current month and year
	'''
	return min(1,reports_by_month(facility,month,year))
