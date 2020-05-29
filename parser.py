import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata
 
'''
Scrapes the HTML using the URL of the given webpage.
'''
def get_webpage(url, attempt):
	### TODO: create a log
	numAttempts = 2
	html = None
	status = "OK: Succesfully requested and recieved HTML from: " + url
	status_code = 0
	try:
		### TODO: log event of reading url
		html = requests.get(url, timeout=0.1)
		html.raise_for_status()
		status_code = 1
	except requests.exceptions.HTTPError as e:
		status = "ERROR: System encountered an HTTP error. See logs for more details."
	except requests.exceptions.Timeout as e:
		if (attempt < numAttempts):
			print("System encountered a Timeout error after waiting 50ms. Trying attempt", attempt + 1, "of 2.")
			get_webpage(url, attempt+1)
		else:
		    status = (
		    	"ERROR: System encountered Timeout errors after two attempts to re-connect."
		    	" See logs for more details."
		    )
	except requests.exceptions.TooManyRedirects as e:
	    status = (
	    	"ERROR: System encountered TooManyRedirects error. Please try a different URL."
	    	"See logs for more details."
	    )
	except requests.exceptions.ConnectionError as e:
		status = (
			"ERROR: System encountered a Connection error. There is most-likely a network problem."
			"See logs for more details."
		)
	except requests.exceptions.RequestException as e:
		status = "ERROR: System threw a Request Exception. Please see logs for more details."

	return html.text if status_code else None



'''
Extracts the tables from the HTML file
'''
def get_tables_from_html(text):
	parsed_soup = BeautifulSoup(text, 'lxml')
	tables = parsed_soup.find_all('table')

	fmt_tables = []
	for table in tables:
		new_table = []
		rows = table.find_all('tr')
		for row in rows:
			new_row = []
			cols = row.find_all('td')
			for col in cols:
				new_row.append(unicodedata.normalize("NFKD", col.get_text()).rstrip())
			new_table.append(new_row)
		fmt_tables.append(new_table)
	
	pd_tables = []
	for table in fmt_tables:
		header = table[0]
		df = pd.DataFrame(table[1:], header)
		pd_tables.append(df)
		print(df)
				


	return fmt_tables


'''
All fixed strings in output
'''
def get_source():
	return "adobe"

def get_type():
	return "vendor"

def get_category():
	return "a"

def get_timestamp():
	curr_time = datetime.now()
	return curr_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4] + "Z"

'''
All strings that come from source HTML
'''

def get_published_date(tables):

	return ""

def get_cve_info(tables):
	return []


if __name__ == "__main__":
	## TODO: User input of URL

	url = "https://helpx.adobe.com/security/products/magento/apsb20-02.html"
	url = "https://helpx.adobe.com/security/products/experience-manager/apsb20-01.html"
	# url = "http://example.com:81"
	# html_text = get_webpage(url, 1)


	# table = get_tables_from_html(html_text)

	# print(get_timestamp())





