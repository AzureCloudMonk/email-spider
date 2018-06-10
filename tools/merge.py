import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials


COMPANY_SHEET_NAME = 'Companies'
NEW_LIST_NAME = 'alexa-1k-company-emails.csv'


def mergeLists():
	scope = ['https://spreadsheets.google.com/feeds',
	         'https://www.googleapis.com/auth/drive']

	credentials = ServiceAccountCredentials.from_json_keyfile_name('opt-out-c93ecd1b36c5.json', scope)

	gc = gspread.authorize(credentials)

	main_sheet = gc.open(COMPANY_SHEET_NAME).sheet1
	new_sheet = gc.open(NEW_LIST_NAME).sheet1
	new_list = new_sheet.get_all_records()

	for row in new_list:
		privacy_policy = row['Privacy Policy']
		email = row['Email']
		company_name = row['Company Name']
		print('New list row - Policy: "{0}", Email "{1}", Company Name "{2}".'.format(privacy_policy,email,company_name))		

		try:
			cell = main_sheet.find(email)
			main_sheet.update_cell(cell.row, 4, privacy_policy)
			print("Updated row {0}.".format(cell.row))
		except gspread.exceptions.CellNotFound:
			print("Adding as new record.")
			now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			domain = email[email.find('@')+1:]
			main_sheet.append_row([company_name,email,domain,privacy_policy,'N',0, now])


if __name__== "__main__":
  mergeLists()
