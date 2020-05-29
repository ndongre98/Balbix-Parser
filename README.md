# Balbix Coding Challenge

## Instructions

Run `python3 parser.py` and input a URL.
If an error is logged in the console, check the log file for more information.

## Context

- The Balbix platform provides customers a comprehensive analysis of their networks and inventory. Balbix maintains a knowledge repo on vulnerabilities that could exist on assets. Information is compiled from a diverse set of resources.
- The Common Vulnerabilities and Exposures (CVE) framework provides a way to identify and standardize various attributes of vulnerabilities affecting systems such as the affected products.
- Affected products are specified by the Common Platform Enumeration (CPE) which is the industry-standard for identifying product attributes.
- Parsers are required to produce output to be easily validated with respect to CPE requirements.

## Objective

Given a vendor webpage with vulnerability details, write a program to parse the website and extract all key vulnerability metrics. The program output should be formatted into JSON


## Assumptions

- Parser only needs to support the two sample websites provided in assignment writeup
- Every HTML webpage contains metadata with a description
- Every HTML webpage contains four tables: information table, affected product versions, solution, and vulnerability details
- Tables share the same column names with the exception of:
	- The Vulnerability Details table potentially including a column for Affected Versions
- The CVE number column in the Vulnerability Details table always contains the string "CVE"
- Affected Versions in the Vulnerability Details take precedence over Version in the Affected Product Versions table
- Requesting/Receiving HTML data requires 1 second
- The "product" attribute in the JSON output wants the specific product name not the product family name (i.e. "magento_commerce" as opposed to "magento") -- I emailed asking about this.
- The "name" attribute for the second example, CVE-2019-16468, was supposed to be "Adobe Experience Manager"
