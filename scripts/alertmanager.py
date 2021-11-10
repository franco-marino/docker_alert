import requests
import logging
import json
from os import getenv
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

"""
Print alert to stdout (if there aren't it won't print anything)
Need as parameter the message to print
Returns an int as exit_code, which could be 0 (successful) or 3 (error)
"""
def send_to_stdout(message):
    # Get logger
    logger = logging.getLogger("docker_alert")

    try:
        exit_code = 0
        print(f"{message}")
        logger.info(f"Message printed to stdout: {message}")
    except Exception as e:
        exit_code = 3
        logger.error(f"An error occured while printing to stdout: {e}")
    finally:
        return exit_code

"""
Get email info from .env file and send a mail via sendmail containing the alert message
Need as parameter the message to send
Returns an int as exit_code, which could be 0 (successful), 2 (error parsing .env) or 3 (error sending mail)
"""
def send_mail(message):
    # Get logger
    logger = logging.getLogger("docker_alert")

    try:
        # Get env variables
        sender             = getenv("EMAIL_FROM")
        to                 = getenv("EMAIL_TO")
        subject            = getenv("EMAIL_SUBJECT")
        if sender and to and subject:
            # Format email
            msg            = MIMEText(message)
            msg["From"]    = sender
            msg["To"]      = to
            msg["Subject"] = subject

            # Send email
            p = Popen(
                ["/usr/sbin/sendmail", "-t", "-oi", "-f" + msg["From"]], stdin=PIPE
            )
            p.communicate(msg.as_bytes())

            # Mail successfully sent
            exit_code = 0
            logger.info(f"Alert mail sento to {to}")
            logger.debug(f"Mail info: {msg.as_bytes()}")
        else:
            exit_code = 2
            logger.error("Invalid or empty .env variables for email")
    except Exception as e:
        exit_code = 3
        logger.error(f"Error in send_mail function: {e}")
    finally:
        return exit_code

"""
Get telegram bot & channel info from .env file and send a message via Telegram API containing the alert
Need as parameter the message to send
Returns an int as exit_code, which could be 0 (successful), 2 (error parsing .env) or 3 (error sending mail)
"""
def send_telegram_alert(message):
    # Get logger
    logger = logging.getLogger("docker_alert")

    try:
        # Get env variables
        token      = getenv("TELEGRAM_TOKEN")
        channel_id = getenv("TELEGRAM_CHANNEL_ID")
        if token and channel_id:
            # Make API Request
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            json_response = json.loads(
                requests.post(url, params={"chat_id": channel_id, "text": message}).text
            )

            if json_response["ok"]:
                exit_code = 0
                logger.info(f"Message sent to {channel_id}")
            else:
                exit_code = 3
                logger.error(f"Oh no, {json_response['description']}")
        else:
            exit_code = 2
            logger.error("Invalid or empty .env variables for telegram")
    except Exception as e:
        exit_code = 3
        logger.error(f"Error in send_telegram_alert function: {e}")
    finally:
        return exit_code

