import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata
import re
import json
import logging
import sys


'''
Logger Set Up
'''
def init_logger(name):
	### Logs to the file ./app.log
	logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='app.log',
                    filemode='w')

	### Logs to the console
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)
	logger = logging.getLogger(name)
	return logger


'''
Scrapes the HTML using the URL of the given webpage. Also tries the URL. 
'''
def get_webpage(url, attempt, log):
	numAttempts = 2
	html = None
	status_code = 0
	try:
		html = requests.get(url, timeout=1)
		html.raise_for_status()
		status_code = 1
		log.info("Succesfully requested and recieved HTML from: " + url)
	except requests.exceptions.HTTPError as e:
		log.error("System encountered an HTTP error. See logs for more details.")
		log.debug(e)
	except requests.exceptions.Timeout as e:
		if (attempt < numAttempts):
			log.info("System encountered a Timeout error after waiting 1s. Trying attempt 2 of 2.")
			get_webpage(url, attempt+1, log)
		else:
		    log.error(
		    	"System encountered Timeout errors after two attempts to re-connect."
		    	" See logs for more details."
		    )
		    log.debug(e)
	except requests.exceptions.TooManyRedirects as e:
	    log.error(
	    	"System encountered TooManyRedirects error. Please try a different URL."
	    	"See logs for more details."
	    )
	    log.debug(e)
	except requests.exceptions.ConnectionError as e:
		log.error(
			"System encountered a Connection error. There is most-likely a network problem."
			"See logs for more details."
		)
		log.debug(e)
	except requests.exceptions.RequestException as e:
		log.error("System threw a Request Exception. Please see logs for more details.")
		log.debug(e)

	if status_code:
		return html.text
	else:
		sys.exit(0)

### Helpers
def trim_version_info_for_affected_version_table(version):
	pattern = "and earlier version"
	if (version.find(pattern) != -1):
		return version[:version.index(pattern)]
	return version

def find_affected_version_range(version):
	new = re.sub('[A-Za-z]', '', version)
	new = re.sub('\s', ',', new)
	new = list(filter(lambda x : x != '', new.split(",")))
	return new

def get_version_start_end(version):
	version_list = find_affected_version_range(version)
	size = len(version_list)
	return [version_list[0], version_list[size-1]] if (size) else []

def adjust_cve_table(cve_table):
	if "Affected Versions" in cve_table.columns:
		cve_table['Affected Versions'] = cve_table['Affected Versions'].apply(lambda x: get_version_start_end(x))
	return cve_table

def adjust_affected_table(affected_table):
	affected_table['Version'] = affected_table['Version'].apply(lambda x: trim_version_info_for_affected_version_table(x))
	affected_table['Version'] = affected_table['Version'].apply(lambda x: get_version_start_end(x))	
	return affected_table

def compile_cve_information(cve_table, affected_table):
	affected_table = adjust_affected_table(affected_table)
	cve_table = adjust_cve_table(cve_table)

	num_affected_versions = affected_table.shape[0]
	num_cves = cve_table.shape[0]

	cve_table = cve_table.loc[cve_table.index.repeat(num_affected_versions)].reset_index(drop=True)
	affected_table = affected_table.append([affected_table]*5).reset_index(drop=True)

	return cve_table.merge(affected_table, left_index=True, right_index=True)






'''
Retrieving information to populate JSON object
'''

### All fixed strings in output
def get_source():
	return "adobe"

def get_type():
	return "vendor"

def get_category():
	return "a"

def get_timestamp():
	curr_time = datetime.now()
	return curr_time.strftime("%Y-%m-%dT%H:%MZ")


### All information not from Vulnerability Table
def get_published_date(info_table, log):
	if ("Date Published" in info_table.columns):
		date_unfmt = info_table['Date Published'][1]
		date_obj = datetime.strptime(date_unfmt, "%B %d, %Y")
		return date_obj.strftime("%Y-%m-%dT%H:%MZ")
	log.error("Could not find published date in web page.")
	return "N/A"

def get_name(html_soup):
	desc = html_soup.find(attrs={'name':'description'}) 
	desc_content = desc["content"]
	name_idx = desc_content.index("for")
	term_idx = desc_content.index("|")
	return (desc_content[name_idx+4:term_idx-1])



### All strings that come from source HTML
def get_description(cve_table_rows, log):
	if ("Vulnerability Category" in cve_table_rows.columns):
		return cve_table_rows["Vulnerability Category"][0].lower()
	log.error("Could not find Vulnerability Category field Vulnerability Details table.")
	return "N/A"

def get_vendor(cve_table_row, log):
	if ("Vulnerability Category" in cve_table_row.index.values):
		return cve_table_row["Product"].split(" ")[0].lower()
	log.error("Could not find Product field Vulnerability Details table.")
	return "N/A"

def get_product(cve_table_row):
	return "_".join(cve_table_row["Product"].split(" ")[1:]).lower()

def get_version_start(cve_table_row, has_specific_version):
	res = cve_table_row["Version"]
	if has_specific_version and len(cve_table_row["Affected Versions"]):
		res = cve_table_row["Affected Versions"]
	return None if (res[0] == res[1]) else res[0]

def get_version_end(cve_table_row, has_specific_version):
	res = cve_table_row["Version"]
	if has_specific_version and len(cve_table_row["Affected Versions"]):
		res = cve_table_row["Affected Versions"]
	return res[1]

def get_cpe(cve_table_row, log):
	has_specific_version = ("Affected Versions" in cve_table_row.index.values)
	if (get_version_start(cve_table_row, has_specific_version)):
		return {
			"vendor": get_vendor(cve_table_row, log),
			"product": get_product(cve_table_row),
			"category": get_category(),
			"versionStartIncluding": get_version_start(cve_table_row, has_specific_version),
			"versionEndIncluding": get_version_end(cve_table_row, has_specific_version)
		}
	return {
		"vendor": get_vendor(cve_table_row, log),
		"product": get_product(cve_table_row),
		"category": get_category(),
		"versionEndIncluding": get_version_end(cve_table_row, has_specific_version)
	}

def get_cpe_list(cve_table_rows, log):
	return {"cpe_list": [get_cpe(cve_table_rows.loc[i,:], log) for i in range(len(cve_table_rows))]}

def get_cve(cve_table_rows, name, url, ID, published_date, log):
	return {
		"timestamp": get_timestamp(),
		"published_date": published_date,
		"id": ID,
		"url": url,
		"name": name,
		"description": get_description(cve_table_rows, log),
		"cpes": get_cpe_list(cve_table_rows, log)
	}

def get_cves(cve_table, name, url, published_date, log):
	cve_table.set_index(keys=['ID'], drop=False,inplace=True)
	ids = cve_table['ID'].unique().tolist()
	cve_list = []
	for i in ids:
		sub_table = cve_table.loc[cve_table["ID"] == i].reset_index(drop=True)
		cve_list.append(get_cve(sub_table, name, url, i, published_date, log))
	return {
		"source": get_source(),
		"type": get_type(),
		"cves": cve_list,
	}


def get_tables(url):
	dfs = pd.read_html(url)
	new_data_frames = dfs
	for df in new_data_frames:
		if df.columns[0] == 0:
			df.columns = ["ID" if 'CVE' in col else col for col in df.iloc[0]]
			df.drop([0], inplace=True)

	return new_data_frames


if __name__ == "__main__":
	url = input("Enter URL: ")
	logger = init_logger('cve_parser')

	html = get_webpage(url, 1, logger)
	soup = BeautifulSoup(html, "lxml")
	tables = get_tables(url)
	(info_table, affected_table, solution_table, cve_table) = (tables[0], tables[1], tables[2], tables[3])

	tables = get_tables(url)
	name = get_name(soup)
	published_date = get_published_date(info_table, logger)
	cves_data_table = compile_cve_information(cve_table, affected_table)
	logger.info("System is compiling CVE Information")
	logger.info(json.dumps(get_cves(cves_data_table, name, url, published_date, logger)))
	logger.info("System has completed task.")





