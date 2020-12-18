import api_client
import logger # Custom library to log errors/info. Managed by one central switch
import logging # Library to log exceptions
import time
import datetime
import jq
import configparser
from datetime import datetime, timedelta
import json

# Parser to read configuration values
config = configparser.ConfigParser()
config.read("config.ini")

# Get avg CPU cores utilization for a given namespace over time range
def cpu_cores_utilization(namespace):
    try:
        rate = config['default']['rate_cpu_avg']
        query = f'query=sum (rate(container_cpu_usage_seconds_total{{namespace=\"{namespace}\"}}[{rate}]))'
        # Step duration
        step_time = config['default']['step_time_cpu_cores_usage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)       
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_avg(response)
        return result
    except:
        raise

# Get avg CPU actual percentage utilization for a given namespace over time range
def cpu_actual_percentage_utilization(namespace):
    try:
        rate = config['default']['rate_cpu_avg']
        query = f'query=sum (rate(container_cpu_usage_seconds_total{{namespace=\"{namespace}\"}}[{rate}])) / sum(kube_resourcequota{{resource=\"requests.cpu\",type=\"hard\",namespace=\"{namespace}\"}}) * 100'
        # Step duration
        step_time = config['default']['step_time_cpu_actual_percentage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_avg(response)
        return result
    except:
        raise

# Get max actual CPU percentage utilization for a given namespace over time range
def cpu_max_percentage_utilization(namespace):
    try:
        rate = config['default']['rate_cpu_max']
        query = f'query=sum (rate(container_cpu_usage_seconds_total{{namespace=\"{namespace}\"}}[{rate}])) / sum(kube_resourcequota{{resource=\"requests.cpu\",type=\"hard\",namespace=\"{namespace}\"}}) * 100'
        # Step duration
        step_time = config['default']['step_time_cpu_actual_max_percentage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_max(response)
        return result
    except:
        raise

# Get CPU limits percentage allocated per quota in a namespace
def cpu_limits_percentage_utilization(namespace):
    try:
        query = f'query=sum (kube_resourcequota{{resource=\"limits.cpu\",type=\"used\",namespace=\"{namespace}\"}}) / sum(kube_resourcequota{{resource=\"limits.cpu\",type=\"hard\",namespace=\"{namespace}\"}}) * 100'
        # Step duration
        step_time = config['default']['step_time_cpu_limits_percentage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_avg(response)
        return result
    except:
        raise

# Get CPU requests percentage allocated per quota in a namespace
def cpu_requests_percentage_utilization(namespace):
    try:
        query = f'query=sum (kube_resourcequota{{resource=\"requests.cpu\",type=\"used\",namespace=\"{namespace}\"}}) / sum(kube_resourcequota{{resource=\"requests.cpu\",type=\"hard\",namespace=\"{namespace}\"}}) * 100'
        # Step duration
        step_time = config['default']['step_time_cpu_requests_percentage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_avg(response)
        return result
    except:
        raise

# Get Memory limits percentage allocated per quota in a namespace
def memory_limits_percentage_utilization(namespace):
    try:
        query = f'query=sum (kube_resourcequota{{resource=\"limits.memory\",type=\"used\",namespace=\"{namespace}\"}}) / sum(kube_resourcequota{{resource=\"limits.memory\",type=\"hard\",namespace=\"{namespace}\"}}) * 100'
        # Step duration
        step_time = config['default']['step_time_memory_limits_percentage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_avg(response)
        return result
    except:
        raise

# Get Memory requests percentage allocated per quota in a namespace
def memory_requests_percentage_utilization(namespace):
    try:
        query = f'query=sum (kube_resourcequota{{resource=\"requests.memory\",type=\"used\",namespace=\"{namespace}\"}}) / sum(kube_resourcequota{{resource=\"requests.memory\",type=\"hard\",namespace=\"{namespace}\"}}) * 100'
        # Step duration
        step_time = config['default']['step_time_memory_requests_percentage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_avg(response)
        return result
    except:
        raise

# Get Memory actual percentage allocated per quota in a namespace
def memory_actual_percentage_utilization(namespace):
    try:
        query = f'query=sum (container_memory_working_set_bytes{{image!=\"\",name=~\"^k8s_.*\", namespace=\"{namespace}\"}}) / sum(kube_resourcequota{{resource=\"requests.memory\",type=\"hard\",namespace=\"{namespace}\"}}) * 100'
        # Step duration
        step_time = config['default']['step_time_memory_actual_percentage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_avg(response)
        return result
    except:
        raise

# Get Max Memory usage percentage allocated per quota in a namespace
def memory_max_percentage_utilization(namespace):
    try:
        query = f'query=sum (container_memory_working_set_bytes{{image!=\"\",name=~\"^k8s_.*\", namespace=\"{namespace}\"}}) / sum(kube_resourcequota{{resource=\"requests.memory\",type=\"hard\",namespace=\"{namespace}\"}}) * 100'
        # Step duration
        step_time = config['default']['step_time_memory_max_percentage']
        # Query parameters concatenated
        query_params = build_query(query, step_time)
        # Invoke the REST API method
        response = get_response(query_params)
        # Get the average of "result" array in json response
        result = get_max(response)
        return result
    except:
        raise

# Build query
def build_query(query, step_time):
    try:
        # Start time range
        start_time = (datetime.now() - timedelta(days=int(config['default']['start_time']))).strftime("%s")
        start = "&start=" + start_time
        # End time range
        end = "&end=" + str(int(time.time()))
        # Step duration
        step = "&step=" + step_time
        # Query parameters concatenated
        query_params = query + start + end + step
        return query_params
    except:
        raise

# Build parameters & invoke the API
def get_response(query_params):
    try:
        # Complete url
        url = config['default']['prometheus_endpoint'] + query_params
        
        # Bearer token for authorization
        token = config['default']['token']
        # headers is of Dictionary type in Python Requests
        headers = {'Authorization': 'Bearer {}'.format(token)}
        # data is of Dictionary type in Python Requests
        payload = {}

        # Invoke the REST API GET method
        response = api_client.get(url, headers, payload)
        return response
    except:
        raise

# Get average of "result" array in json response
def get_avg(response):
    try:
        result = ""
        if response.status_code == 200:
            # Load the json document into a python object
            json_response = json.loads(response.text)
            # Get the values in a list
            response_list_string = jq.compile(".data.result[].values[][1]").input(json_response).all()
            # Convert list of string to float
            response_list_float = [float(item) for item in response_list_string]
            if len(response_list_float) > 0:
                # Calculate the average
                response_list_avg = sum(response_list_float) / len(response_list_float) 
                result = round(response_list_avg, 3)
            else:
                # If the list is empty
                result = "N/A"
        else:
            result = "N/A"
        return result 
    except:
        raise

# Get max of "result" array in json response
def get_max(response):
    try:
        result = ""
        if response.status_code == 200:
            # Load the json document into a python object
            json_response = json.loads(response.text)
            # Get the values in a list
            response_list_string = jq.compile(".data.result[].values[][1]").input(json_response).all()
            # Convert list of string to float
            response_list_float = [float(item) for item in response_list_string]
            if len(response_list_float) > 0:
                # Get the max value
                response_list_avg = max(response_list_float)
                result = round(response_list_avg, 3)
            else:
                # If the list is empty
                result = "N/A"
        else:
            result = "N/A"
        return result 
    except:
        raise
        