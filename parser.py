import requests

def get_webpage(url):
	try:
		html = requests.get(url)
		html.raise_for_status()
		print(html.text)
	except requests.exceptions.HTTPError as e:
		print("System encountered an HTTP error. See logs for more details.")
	except requests.exceptions.Timeout:
		### TODO: attempt to reconnect 3 times, let user know
	    print("System encountered a Timeout error and attempted to re-connect 3 times. See logs for more details.")
	except requests.exceptions.TooManyRedirects:
	    print("System encountered TooManyRedirects error. Please try a different URL. See logs for more details.")
	except requests.exceptions.ConnectionError as e:
		print("System encountered a Connection error. There is most-likely a network problem. See logs for more details.")
	except requests.exceptions.RequestException as e:
		print("System threw a Request Exception. Please see logs for more details.")


if __name__ == "__main__":
	url = "https://xdxd"
	get_webpage(url)