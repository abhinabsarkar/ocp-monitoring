# Customized logging. Ensures switching the log labels at one single place

# Libraries
import logging # Import module for logging
import time # Import module for date time. Used to create log file with today's date

# Log info. When required to debug, set level to INFO
def log_message(message):
    # Configure logging to file
    configure_log_file()    
    # Configure log level
    logging.getLogger().setLevel(logging.ERROR)
    # Create logger & set the value in runtime
    logger = logging.getLogger()
    # Log messsage with appropriate log level - INFO, ERROR, DEBUG
    logger.info(message)

def log_error(message): 
    # Configure logging to file
    configure_log_file()    
    # Configure log level
    logging.getLogger().setLevel(logging.ERROR)
    # Create logger
    logger = logging.getLogger()
    # Log messsage with appropriate log level - INFO, ERROR, DEBUG
    logger.error(message, exc_info=1)

# Log info. When required to debug, set level to INFO
def log_note(message):
    # Configure logging to console
    configure_log()
    
    # Configure logging to file
    configure_log_file()

    # Configure log level
    logging.getLogger().setLevel(logging.INFO)
    # Create logger
    logger = logging.getLogger()
    # Log messsage with appropriate log level - INFO, ERROR, DEBUG
    logger.info(message) 

def configure_log():
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', \
        level=logging.DEBUG)

def configure_log_file():
    # timestamp = time.strftime("%Y%m%d-%H%M%S")
    # Create log file with today's date
    timestamp = time.strftime("%Y%m%d")
    filename = timestamp + ".log"
    # Configure logging 
    logging.basicConfig(
        # level=logging.ERROR,    # Changed by individual methods during the runtime
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
        filename=filename,
        filemode='a'
    )