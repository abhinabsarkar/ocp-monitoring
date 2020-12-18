# Importing my libraries
import requests
# Import json module
import json
# Library to convert string to dictionary
import ast
# Import CSV read & write module
import csv
# Importing configuration parser
import configparser
import logger # Custom library to log errors/info. Managed by one central switch
import logging # Library to log exceptions
# Suppress InsecureRequestWarning in the response
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Added retry strategy
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Get client with url, resource & id for an unsecured api
def get(url, headers, payload):
    try:
        retry_strategy = Retry(
            total=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        # Invoke the REST API call
        response = http.request("GET", url, headers=headers, data=payload, verify=False)
        # Log response        
        if int(response.status_code) == 200:
            logger.log_message('GET return code: ' + str(response.status_code))
            logger.log_message('GET response text: ' + response.text)
        else:
            logger.log_note('GET return code: ' + str(response.status_code) + ' URL:' + url) 
            logger.log_note('GET error message: ' + str(response.text))
        return response
    except:
        raise