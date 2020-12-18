# Import library to read & write csv
import csv
# Import os to check the file properties
import os
import logger # Custom library to log errors/info. Managed by one central switch
import logging # Library to log exceptions

# Write to csv file 
def write_csv(csv_file, row):
    # Get the file path
    file_path = os.path.join(os.getcwd(), csv_file) 
    # Create a file and append rows to it
    with open(csv_file, mode='a', newline='') as csv_file:        
        csv_writer = csv.writer(csv_file)
        # Check whether file is empty or not
        file_empty = os.stat(file_path).st_size == 0
        # Write header row to the CSV file if empty
        if file_empty:
            header = ["Namespace", "Actual CPU cores used", "Actual CPU usage %", \
                "Max CPU usage %", "CPU requests usage %", "CPU limits usage %", \
                "Actual Memory usage %", "Max Memory usage %", "Memory requests usage %", "Memory limits usage %", \
                "Grafana URL"]
            csv_writer.writerow(header)              
        csv_writer.writerow(row)             
    return True