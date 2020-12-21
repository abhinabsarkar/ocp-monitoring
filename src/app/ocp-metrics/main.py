# Importing libraries
import configparser
import json
import os 
import time
import logging
import logger
import sys, traceback
from datetime import datetime
import jq
import api_client
import metrics
import process_csv
import response_format
import HTML
import notify
import file_mgmt
import chart

# Parser to read configuration values
config = configparser.ConfigParser()
config.read("config.ini")

try:
    # List for email report
    report_list = []
    # List for detailed report
    data_list = []
    # Log the start of the process    
    logger.log_note('*** Job initiated at ' + str(datetime.today()) + ' ***')
    # OpenShift cluster name
    cluster_name = config['default']['cluster_name']
    # Report file name
    filename = "Report.csv"

    # Get the list of namespaces 
    namespaces_list = metrics.list_namespaces()
    if len(namespaces_list) > 0:
        # Loop through the namespaces list
        logger.log_note('Loop through the namespaces list')
        for counter in range(len(namespaces_list)):
            ns = namespaces_list[counter]
            # Get the metrics for the namespace
            if (ns.endswith("-dv") or ns.endswith("-dev") or ns.endswith("-qa") \
            or ns.endswith("-ut") or ns.endswith("-uat") or ns.endswith("-sit") \
            or ns.endswith("-st") or ns.endswith("-pt") or ns.endswith("-hotfix")):
                logger.log_note('Processing for namespace ' + ns)
                # Actual CPU cores used
                cpu_cores_ns = metrics.cpu_cores_utilization(ns)
                # Actual CPU usage %
                cpu_actual_use_percent_ns = metrics.cpu_actual_percentage_utilization(ns)
                # Max CPU usage %
                cpu_max_use_percent_ns = metrics.cpu_max_percentage_utilization(ns)
                # CPU requests usage %
                cpu_requests_use_percent_ns = metrics.cpu_requests_percentage_utilization(ns)
                # CPU limits usage %
                cpu_limits_use_percent_ns = metrics.cpu_limits_percentage_utilization(ns)
                # Actual Memory usage %
                memory_actual_use_percent_ns = metrics.memory_actual_percentage_utilization(ns)
                # Max Memory usage %
                memory_max_use_percent_ns = metrics.memory_max_percentage_utilization(ns)
                # Memory requests usage %
                memory_requests_use_percent_ns = metrics.memory_requests_percentage_utilization(ns)
                # Memory limits usage %
                memory_limits_use_percent_ns = metrics.memory_limits_percentage_utilization(ns)
                # Grafana url
                grafana_url = config['default']['grafana_url'].replace("ns_to_query", ns)

                # Add the metrics to a list
                row = [ns, cpu_cores_ns, cpu_actual_use_percent_ns, \
                    cpu_max_use_percent_ns, cpu_requests_use_percent_ns, cpu_limits_use_percent_ns, \
                    memory_actual_use_percent_ns, memory_max_use_percent_ns, memory_requests_use_percent_ns, memory_limits_use_percent_ns, \
                    grafana_url]
                # Adding to data_list
                data_list.append(row)
                # Create csv file with complete report
                process_csv.write_csv(filename, row)

        # Log the file has been created
        logger.log_note('Report file created: ' + filename)

        # Create a data_list report for email 
        # Add header row
        header = ["Namespace", "Actual CPU cores used", "Actual CPU usage %", \
            "Max CPU usage %", "CPU requests usage %", "CPU limits usage %", \
            "Actual Memory usage %", "Max Memory usage %", "Memory requests usage %", "Memory limits usage %", \
            "Grafana URL"]
        report_list.append(header)
        # Loop through the data_list
        logger.log_note('Loop through the data_list')
        for row in data_list:
            # Check if the max cpu is number or not, as it can be 'N/A' as well 
            try:
                val = float(row[2])
                # if max cpu is less than max_cpu_threshold, add it to report list
                if row[3] < int(config['default']['max_cpu_threshold']):
                    logger.log_note('Processing row: ' + row[0])
                    # Replace grafana url with html link
                    row[10] = '</br>' + HTML.link(row[0], row[10])
                    report_list.append(row)
            except ValueError:
                # Do nothing as it is not a number
                logger.log_message("This is not a float number type")

        # Get the namespace list from report list
        ns_list = [row[0] for row in report_list]
        # Remove the header from the list
        ns_list.pop(0)
        # Get the max CPU % used list from report list
        max_cpu_list = [row[3] for row in report_list]
        # Remove the header from the list
        max_cpu_list.pop(0)
        # Get the max Memory % used list from report list
        max_memory_list = [row[7] for row in report_list]
        # Remove the header from the list
        max_memory_list.pop(0)
        # Plot the bar chart
        chart.bar_chart(ns_list, max_cpu_list, max_memory_list)
        
        # Create email parameters
        subject = "Cluster utilization report"
        threshold = config['default']['max_cpu_threshold']
        text_message = "<p style=\"font-size:20px;\"> The following namespaces in OpenShift cluster <b>" + cluster_name+ "</b>" \
            " have max CPU utilization less than <span style=\"color: Red\">" + threshold + "</span> percent over last <b>14</b> days. Also attached" \
            " is the report of resource utilization for all application namespaces.</p>" 
        chart = "<img src='chart.png'>"
        table = response_format.html_result(report_list)
        body = text_message + chart + table
        # Add attachments
        attachments = [filename, "chart.png"]
        # Send email notification
        notify.send_email(subject, body, attachments)

    # Delete the report file & log its name
    file_list = file_mgmt.list_files(os.getcwd(), 'csv')
    for file in file_list:
        file_mgmt.delete_file(file)
    # Delete the chart file & log its name
    file_list = file_mgmt.list_files(os.getcwd(), 'png')
    for file in file_list:
        file_mgmt.delete_file(file)
    # Delete the log file
    # Check for the log files and purge, if they are other than today's date
    timestamp = time.strftime("%Y%m%d")    
    logfilename = timestamp + ".log"
    log_list = file_mgmt.list_files(os.getcwd(), 'log')
    for log in log_list:
        if log != logfilename:
            file_mgmt.delete_file(log)

    # Log the end of the process
    logger.log_note('*** Job completed successfully ***')
except Exception as error:
    # Log the error message & send notification
    logger.log_error(error)
    # printing stack trace 
    traceback.print_exc()
    notify.send_email("Failed to generate report", "Unable to generate report. Error details below: " + str(error), "")
    logger.log_note('*** Job failed. Error email sent. ***')