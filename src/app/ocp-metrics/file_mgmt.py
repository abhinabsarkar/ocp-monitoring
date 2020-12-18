# Import the libraries
import os
from datetime import datetime # Library to get today's date and time
from os import listdir # Library to list contents in a directory
import logger
import time

def delete_file(filename_with_path):
    try:
        # Check if file exists
        if os.path.exists(filename_with_path):
            # Purge the file
            os.remove(filename_with_path)
            logger.log_note('File ' + os.path.basename(filename_with_path) + ' purged at ' \
                + str(datetime.today()))
    except:
        raise

# List all files in a directory for a given extension
# Accepted parameters - directory = 'D:\myfolder', extension = 'txt'
def list_files(directory, extension):
    try:
        # Check if directory exists
        if os.path.exists(directory):
            # Return the list of files
            return (f for f in listdir(directory) if f.endswith('.' + extension))
    except:
        raise