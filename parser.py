import requests
 
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

# def parse()


if __name__ == "__main__":
	## TODO: User input of URL
	url = "https://helpx.adobe.com/security/products/magento/apsb20-02.html"
	# url = "http://example.com:81"
	get_webpage(url, 1)