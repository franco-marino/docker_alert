import requests_unixsocket
import requests
import logging
import sqlite3
import sys
import os
from dotenv import load_dotenv
from pathlib import Path
from scripts import argsmanager, logmanager, alertmanager
from scripts.containermanager import ContainerManager
from scripts.dbmanager import DbManager

"""
Main function
"""
def main():
    # Init args and recover them
    args = argsmanager.init_args()

    # Exit with exit_code 1 if there are argument errors
    if not args:
        sys.exit(1)

    # Load .env file
    load_dotenv(dotenv_path=Path(args.env))

    # Default exit code (successful)
    exit_code = 0

    # Create logger
    logmanager.create_logger()
    logger = logging.getLogger("docker_alert")

    # Log script started
    logger.info(f"Script started: env file path='{args.env}', send telegram message={args.telegram}, send email={args.mail}, send to stdout={args.stdout}")

    # Initialize the alert message
    alert_msg = ""

    try:
        # Connect to DB
        dbmanager = DbManager()

        # Create ContainerManager object and get container statuses
        containermanager   = ContainerManager()
        container_statuses = containermanager.get_container_statuses()
        logger.debug(f"Current container statuses are: {container_statuses}")

        # Add changed container to the alert_msg
        for container_name in container_statuses:
            old_container_status = dbmanager.check_container_status(container_name, container_statuses[container_name])
            new_container_status = container_statuses[container_name]
            if old_container_status != new_container_status:  
                alert_msg += f"{container_name}: {old_container_status} --> {new_container_status}\n"
                logger.debug(f"{container_name} changed: {old_container_status} --> {new_container_status}")

        # Remove trailing whitespaces
        alert_msg = alert_msg.strip()

        # If there are alerts to send, prepare message
        if len(alert_msg) > 0:
            alert_msg = "Container statuses changed:\n" + alert_msg

        # Remove the error "socket_conn" from the DB, and send an alert if it was present
        if dbmanager.delete_script_error("socket_conn"):
            alert_msg += "Connection to docker socket restored"
            logger.info(f"Sending alert: {alert_msg}")
    except requests.exceptions.ConnectionError as e:
        # Send an alert about "socket_conn" only every at least delay_hours
        delay_hours = os.getenv("DOCKER_DOWN_DELAY_HOURS")
        if dbmanager.check_script_error("socket_conn", delay_hours):
            alert_msg = "Connection to docker socket failed. Maybe docker daemon is down? Are you (my crontab owner) in the docker group?"
            logger.info("Sending alert: Connection to docker socket failed")
        else:
            logger.debug(f"Connection to docker socket failed, but not sending an alert because the delay ({delay_hours} hours) has not been passed yet")
        exit_code = 4
        logger.critical( str(e) )
    except sqlite3.Error as e:
        alert_msg = "DB Error"
        exit_code = 5
        logger.critical( str(e) )

    # Send alerts via the right method (if there is something to send)
    if len(alert_msg) > 0:
        if args.stdout:
            exit_code_temp = alertmanager.send_to_stdout(alert_msg)
            if exit_code == 0:
                exit_code = exit_code_temp
        if args.telegram:
            exit_code_temp = alertmanager.send_telegram_alert(alert_msg)
            if exit_code == 0:
                exit_code = exit_code_temp
        if args.mail:
            exit_code_temp = alertmanager.send_mail(alert_msg)
            if exit_code == 0:
                exit_code = exit_code_temp
    else:
        # No alerts to send
        logger.info("All OK: no alerts to send, exiting")

    # Exit with the right exit code
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
