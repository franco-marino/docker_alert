import requests
import json
import os
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

"""
Print unhealthy containers to stdout (if there aren't it won't print anything)
Need as parameters the message to print and the logger object
Return an int as exit_code, which could be 0 (successful) or 3 (error)
"""
def send_to_stdout(message, logger):
    try:
        exit_code = 0
        print("Result: {0}".format(message))
        logger.log("info", "Message printed to stdout: {0}".format(message))
    except Exception as e:
        logger.log("error", "An error occured while printing to stdout: {0}".format(e))
        exit_code = 3
    finally:
        return exit_code

"""
Get email info from .env file and send a mail via sendmail containing unhealthy containers names (only if there are)
Need as parameters the message to send and the logger object
Return an int as exit_code, which could be 0 (successful), 2 (error parsing .env) or 3 (error sending mail)
"""
def send_mail(message, logger):
    try:
        exit_code = 0
        # Get env variables
        sender = os.getenv("EMAIL_FROM")
        to = os.getenv("EMAIL_TO")
        subject = os.getenv("EMAIL_SUBJECT")
        if sender != None and to != None and subject != None:
            # Format email
            msg = MIMEText(message)
            msg["From"] = sender
            msg["To"] = to
            msg["Subject"] = subject

            # Send email
            p = Popen(
                ["/usr/sbin/sendmail", "-t", "-oi", "-f" + msg["From"]], stdin=PIPE
            )
            p.communicate(msg.as_bytes())

            # Log
            logger.log("info", "Alert mail sento to {0}".format(to))
            logger.log("info", "Mail info: {0}".format(msg.as_bytes()))
        else:
            logger.log("error", "Invalid or empty .env variables for email ")
            exit_code = 2
    except Exception as e:
        logger.log("error", "Error in send_mail function: {0}".format(e))
        exit_code = 3
    finally:
        return exit_code

"""
Get telegram bot & channel info from .env file and send a message via Telegram API containing unhealthy containers names (only if there are)
Need as parameters the message to send and the logger object
Return an int as exit_code, which could be 0 (successful), 2 (error parsing .env) or 3 (error sending mail)
"""
def send_telegram_alert(message, logger):
    try:
        exit_code = 0
        # Get env variables
        token = os.getenv("TELEGRAM_TOKEN")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        if token != None and channel_id != None:
            # Make API Request
            url = "https://api.telegram.org/bot{0}/sendMessage".format(token)
            json_response = json.loads(
                requests.post(url, params={"chat_id": channel_id, "text": message}).text
            )

            if json_response["ok"]:
                logger.log("info", "Message sent to {0}".format(channel_id))
            else:
                logger.log("error", "Oh no,{0}".format(json_response["description"]))
                exit_code = 3
        else:
            logger.log("error", "Invalid or empty .env variables for telegram ")
            exit_code = 2
    except Exception as e:
        logger.log("error", "Error in send_telegram_alert function: {0}".format(e))
        exit_code = 3
    finally:
        return exit_code

