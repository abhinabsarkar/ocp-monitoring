import os
import logger # Custom library to log errors/info. Managed by one central switch
import logging # Library to log exceptions
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import configparser

# Parser to read configuration values
config = configparser.ConfigParser()
config.read("config.ini")

def send_email(subject, body, attachments):
    sender_email=config['default']['sender_email']
    receiver_email=config['default']['receiver_email']
    smtp_server = config['default']['smtp_server']
    port = config['default']['smtp_port']  # For starttls

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        # Create secure connection with server and send email
        # context = ssl.create_default_context()
        # server.starttls(context=context) # Secure the connection
        server = smtplib.SMTP(smtp_server, port)

        # Add message body
        message.attach(MIMEText(body, "html"))

        # Parse through attachments - Report.csv & chart.png
        if len(attachments) > 0:
            for counter in range(len(attachments)): 
                if (attachments[counter] != ""):
                    # Add attachment
                    # Open file in binary mode
                    with open(attachments[counter], "rb") as attachment:
                        # Add file as application/octet-stream
                        # Email client can usually download this automatically as attachment
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())

                    # Encode file in ASCII characters to send by email    
                    encoders.encode_base64(part)

                    # Add header as key/value pair to attachment part
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachments[counter]}",
                    )
                    # Add attachment to message and convert message to string
                    message.attach(part)

        # Send email
        server.sendmail(sender_email, receiver_email, message.as_string())
        logger.log_note("Mail sent successfully")
    except:
        raise
    finally:
        server.quit()