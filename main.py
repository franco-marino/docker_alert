import requests_unixsocket
import requests
import json
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from scripts import argsmanager, alert, logger

"""
Recover containers status, state and details from the Docker JSON API
Need no parameters
Return a JSON object
"""
def get_containers_json():
    # Containers info url
    URL = "http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/json?all=1"

    # Make request
    session = requests_unixsocket.Session()
    json_response = session.get(URL)

    # Return
    return json_response.json()

"""
Search for unhealthy containers inside a given JSON object recovered from Docker APIs
Need the JSON object and a logger object as parameters
Return an array of unhealthy containers names
"""
def get_unhealthy_containers(containers_json, logger):
    # Initialize the unhealthy_containers array
    unhealthy_containers = []

    # Parse the containers json and add unhealthy containers to the array
    if len(containers_json) > 0:
        for container in containers_json:
            if container["Status"].find("unhealthy") != -1:
                unhealthy_containers.append(container["Names"][0][1:])
                logger.log("info", "Found unhealthy container: {0}".format(container["Names"][0][1:]))
    else:
        logger.log("info", "There aren't containers")

    # Return the array
    return unhealthy_containers

"""
Search for not running (eg created, exited, paused, dead, restarting) containers inside a given JSON object recovered from Docker APIs
Need the JSON object and a logger object as parameters
Return an array of not running containers names
"""
def get_not_running_containers(containers_json, logger):
    # Initialize the not_running_containers array
    not_running_containers = []

    # Parse the containers json and add not running containers names to the array
    if len(containers_json) > 0:
        for container in containers_json:
            if container["State"].find("running") < 0:
                not_running_containers.append(container["Names"][0][1:])
                logger.log("info", "Found not running container: {0}".format(container["Names"][0][1:]))
    else:
        logger.log("info", "There aren't containers")

    # Return the array
    return not_running_containers

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

    # Get containers status and details via JSON Docker API
    containers_json = get_containers_json()

    # Get unhealthy containers array
    unhealthy_containers = get_unhealthy_containers(containers_json, logg)

    # Get not running containers array (only if --not-running argument is set)
    if args.not_running:
        not_running_containers = get_not_running_containers(containers_json, logg)

    # Send alerts (if necessary)
    if len(unhealthy_containers) > 0 or (args.not_running and len(not_running_containers) > 0):
        # Initialize the alert message
        msg = ""

        # Add to the alert message unhealthy containers (only if there are)
        if len(unhealthy_containers) > 0:
            msg += "The following containers are unhealthy:\n"
            for container in unhealthy_containers:
                msg += "{0} \n".format(container)

        # Add to the alert message not running containers (only if --notrunning argument is set and only if there are "not running" containers)
        if args.not_running and len(not_running_containers) > 0:
            msg += "The following containers aren't running:\n"
            for container in not_running_containers:
                msg += "{0} \n".format(container)

        # Send alerts via the right method
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

    # Exit with the right exit code
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
