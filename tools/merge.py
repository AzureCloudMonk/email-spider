import datetime
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials


MAIN_SHEET_NAME = 'Domains'
STAGING_SHEET_NAME = 'Domains-staging'
CREDENTIALS_FILE = 'opt-out-8e22f0087b51.json'


def mergeLists():
	scope = ['https://spreadsheets.google.com/feeds',
	         'https://www.googleapis.com/auth/drive']

	credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)

	gc = gspread.authorize(credentials)

	main_sheet = gc.open(MAIN_SHEET_NAME).sheet1
	new_sheet = gc.open(STAGING_SHEET_NAME).sheet1
	new_list = new_sheet.get_all_records()

	for row in new_list:
		try:
			privacy_policy = row['Privacy Policy']
			email = row['Email']
			display_name = row['Display Name']
			search_terms = row['Search Terms']
			domain = row['Domain']
			print('New list row - Domain: "{0}", Policy: "{1}", Email "{2}", Display Name "{3}".'.format(
				domain,privacy_policy,email,display_name))		

			try:
				cell = main_sheet.find(domain)
				main_sheet.update_cell(cell.row, 2, display_name)
				main_sheet.update_cell(cell.row, 3, search_terms)
				main_sheet.update_cell(cell.row, 5, privacy_policy)
				print("Updated row {0}.".format(cell.row))
			except gspread.exceptions.CellNotFound:
				print("Adding as new record.")
				now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				main_sheet.append_row([domain, display_name, search_terms, email, privacy_policy,'N',0, now])
			#time.sleep(3)
		except gspread.exceptions.APIError as error:
			print("RESOURCE_EXHAUSTED exception.")
			time.sleep(110)


if __name__== "__main__":
  mergeLists()
