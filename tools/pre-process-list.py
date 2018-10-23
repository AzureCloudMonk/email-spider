import csv
import sys
import getopt

from collections import defaultdict


EMAIL_PREFIXES = [
	'dpo','dataprotection','closemyaccount','data.protection','dataprivacy','dataprotectionofficer','optout','opt-out',
	'privacy.officer','gdpr','privacyofficer','privacypolicy','privacyshield','account.disable','account.disabled',
	'privacymanager','privacyoffice','data','dataprivacyofficer','remove','privacy','legal','legaldept','customercare','pii',
	'datarequest','datenschutz','grievanceofficer','questions','customerservice','support','dmca','unsubscribe','info','contact',
	'webmaster','help','admin','feedback','service','sales','security','tab','copyright','site','hello','safeharboragent','cs',
	'email','name','team','compliance','rating','abuse','ads','bugbounty','editor','terms','2a62c5378d9b4c8aa92615a84e120430',
	'2db1fe908c734593b15029361071c2a4','account.enable','account.verify','me','permissions','testcancel','webfeedback','you',
	'20privacy','link','mail','marketing','media','press','spoof','username','hi','inquiry','spam','user','web','your','bcpinfo',
	'billing','chlegal','cibcinvestorservicesinc','commissioner','contactus','daniel'
]
DOMAIN_2_COMPANY_NAME = {}


def preProcess(inFile, outFile, domainFile):
	complete_results = []
	incomplete_results = []
	domains_details = defaultdict(list)
	rows = getRawList(inFile)

	# index by domain
	for row in rows:
		domain = row[0]
		email = row[1]
		source = row[2]
		page_type = row[3]
		if domain.startswith('www.'):
			domain = domain[4:]
		domains_details[domain].append({'email': email, 'source': source, 'page_type': page_type})

	print("Loaded a list of {0} domains.".format(len(domains_details.keys())))

	# email selection and add company name
	unresolved_emails = 0
	unresolved_names = 0
	for domain, details in domains_details.items():
		company_name = domain2CompanyName(domain, domainFile)
		selection = selectEmail(details)
		privacy_policy = getPPLink(details)
		print("Reduced {0} emails to {1}.".format(len(details), len(selection)))
		if len(selection) == 1 and company_name:
			complete_results.append({
				'Domain': domain, 
				'Display Name': company_name,
				'Search Terms': company_name,
				'Email': selection[0]['email'], 
				'Privacy Policy': privacy_policy,
				'Page Type': selection[0]['page_type']
				})
		else: 			
			for item in selection:
				incomplete_results.append({
					'Domain': domain, 
					'Display Name': company_name,
					'Search Terms': company_name,
					'Email': item['email'], 
					'Privacy Policy': privacy_policy,
					'Page Type': item['page_type']
					})
			if len(selection) > 1:
				unresolved_emails += 1
		if not company_name:
			unresolved_names += 1

	generateOutput(complete_results, incomplete_results, outFile)
	print ("Output file generaed. Unresoled emails: {0}, unresolved names: {1}".format(unresolved_emails, unresolved_names))


def getRawList(inFile):
	with open(inFile) as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		reader.__next__() # waste the header
		return [list(x) for x in set(tuple(x) for x in reader)]


def selectEmail(details):
	highest_rank = None
	chosen = None
	for item in details:
		try:
			prefix = item['email'][:item['email'].find('@')]
			rank = EMAIL_PREFIXES.index(prefix)+1
		except ValueError:
			rank = 0
		if not highest_rank or rank > highest_rank:
			highest_rank = rank
			chosen = [item]
	return chosen if chosen else details


def getPPLink(details):
	for item in details:
		if item['page_type'] == 'Privacy policy':
			return item['source']
	return ""

def loadDomain2ComoanyNameLookup(domainFile):
	global DOMAIN_2_COMPANY_NAME
	with open(domainFile) as csvfile:
		reader = csv.DictReader(csvfile)
		for line in reader:
			DOMAIN_2_COMPANY_NAME[line['homepage_domain']] = line['name']
	print('Lookup loaded.')


def domain2CompanyName(domain, domainFile):
	global DOMAIN_2_COMPANY_NAME
	if not DOMAIN_2_COMPANY_NAME:
		loadDomain2ComoanyNameLookup(domainFile)
	if domain in DOMAIN_2_COMPANY_NAME:
		return DOMAIN_2_COMPANY_NAME[domain] 
	else:
		print("Cound not find company name for domain '{0}'.".format(domain)) 
		return None


def generateOutput(complete_results, incomplete_results, outFile):
	with open('{0}-complete.csv'.format(outFile), 'w') as csvfile:
		fieldnames = ['Domain', 'Display Name', 'Search Terms', 'Email', 'Privacy Policy', 'Page Type']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for row in complete_results:
			writer.writerow(row)
	with open('{0}-incomplete.csv'.format(outFile), 'w') as csvfile:
		fieldnames = ['Domain', 'Display Name', 'Search Terms', 'Email', 'Privacy Policy', 'Page Type']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for row in incomplete_results:
			writer.writerow(row)


def getArgs():
	usage = 'pre-process-list.py -i <inputfile> -o <outputfileprefix> -d <domainfile>'
	inputfile = ''
	outputfile = ''
	domainfile = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hi:o:d:",["ifile=", "ofile=", "dfile="])
	except getopt.GetoptError:
		print(usage)
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print(usage)
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg
		elif opt in ("-d", "--dfile"):
			domainfile = arg
	if not inputfile or not outputfile or not domainfile:
		print(usage)
		sys.exit(2)
	return inputfile, outputfile, domainfile


if __name__== "__main__":
  	preProcess(*getArgs())
