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
	results = []
	domains_details = defaultdict(list)
	rows = getRawList(inFile)

	# index by domain
	for row in rows:
		email = row[1]
		source = row[2]
		domain = email[email.find('@')+1:]
		if domain.startswith('www.'):
			domain = domain[4:]
		domains_details[domain].append({'email': email, 'source': source})

	print("Loaded a list of {0} domains.".format(len(domains_details.keys())))

	# email selection and add company name
	unresolved_emails = 0
	unresolved_names = 0
	for domain, details in domains_details.items():
		company_name = domain2CompanyName(domain, domainFile)
		if len(details) == 1:
			results.append({
				'domain': domain, 
				'company_name': company_name,
				'email': details[0]['email'], 
				'source': details[0]['source']
				})
		else: 
			selection = selectEmail(details)
			print("Reduced {0} emails to {1}.".format(len(details), len(selection)))
			for item in selection:
				results.append({
					'domain': domain, 
					'company_name': company_name,
					'email': item['email'], 
					'source': item['source']
					})
			if len(selection) > 1:
				unresolved_emails += 1
		if not company_name:
			unresolved_names += 1

	generateOutput(results, outFile)
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


def generateOutput(rows, outFile):
	with open(outFile, 'w') as csvfile:
		fieldnames = ['domain', 'company_name', 'email', 'source']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for row in rows:
			writer.writerow(row)


def getArgs():
	usage = 'pre-process-list.py -i <inputfile> -o <outputfile> -d <domainfile>'
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
