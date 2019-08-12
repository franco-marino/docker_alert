import requests_unixsocket
import requests
import json
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from scripts import argsmanager, alert, logger

"""
Search for unhealthy containers from Docker JSON API
Need as parameters the logger object
Return an array of their names
"""
def get_unhealthy_containers(logger):
    # Containers info url
    URL = "http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/json"

    # Make request
    session = requests_unixsocket.Session()
    json_response = session.get(URL)
    containers = json_response.json()

    # Prepare the unhealthy_containers array
    unhealthy_containers = []

    # Parse the response
    if len(containers) > 0:
        for container in containers:
            if container["Status"].find("unhealthy") != -1:
                unhealthy_containers.append(container["Names"][0][1:])
                logger.log("info", "Found unhealthy container: {0}".format(container["Names"][0][1:]))
    else:
        logger.log("info", "There aren't containers")

    # Return
    return unhealthy_containers

"""
Main function
"""
def main():
    # Init args and recover them
    args = argsmanager.init_args()

    # Exit with exit_code 1 if there are argument errors
    if args == None:
        sys.exit(1)

    # Load .env file
    load_dotenv(dotenv_path=Path(args.env))

    # Default exit code (successful)
    exit_code = 0

    # Create logger obj
    logg = logger.Logger()

    # Log script started
    logg.log("info", "Script started. Env file path='{0}', send telegram message = {1}, send email = {2}, send to stdout= {3}".format(args.env, args.telegram, args.mail, args.stdout))

    # Get unhealthy containers array
    unhealthy_containers = get_unhealthy_containers(logg)

    # Send alerts (if necessary)
    if len(unhealthy_containers) > 0:
        # Create the message
        msg = "The following containers are unhealthy:\n"
        for container in unhealthy_containers:
            msg += "{0} \n".format(container)

        # Send alerts
        if args.stdout:
            exit_code_temp = alert.send_to_stdout(msg, logg)
            if exit_code == 0:
                exit_code = exit_code_temp
        if args.telegram:
            exit_code_temp = alert.send_telegram_alert(msg, logg)
            if exit_code == 0:
                exit_code = exit_code_temp
        if args.mail:
            exit_code_temp = alert.send_mail(msg, logg)
            if exit_code == 0:
                exit_code = exit_code_temp
    else:
        logg.log("info", "All containers are healthy")

    # Exit with right exit code
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
