import argparse
import os
import sys
from scripts import logger

"""
Check if the env argument is a valid file
If it is not a valid file raise an ArgumentTypeError error
"""
def check_env(env):
    if os.path.isfile(env):
        return env
    else:
        msg = "Not a valid env file: {0}".format(env)
        raise argparse.ArgumentTypeError(msg)

"""
Return script arguments if there are no errors
"""
def init_args():
    try:
        parser = argparse.ArgumentParser()

        # Required arguments
        parser.add_argument("env", help="Your env file path", type=check_env)

        # Optional arguments
        parser.add_argument(
            "--not-running",
            action="store_true",
            help="Receive alerts also for not running containers (created, exited, paused, dead, restarting))"
        )

        # Alert options
        alert_options = parser.add_argument_group("alert options")
        alert_options.add_argument(
            "--telegram",
            action="store_true",
            help="Receive alerts through a telegram bot"
        )
        alert_options.add_argument(
            "--mail",
            action="store_true",
            help="Receive alerts via mail"
        )
        alert_options.add_argument(
            "--stdout",
            action="store_true",
            help="Print unhealthy containers to stdout (if there aren't the output will be empty)"
        )

        # Get args
        args = parser.parse_args()

        return args
    except SystemExit as e:
        logg = logger.Logger(os.path.abspath(os.path.dirname(sys.argv[0]))+"/log", True)
        logg.log("critical", "Invalid args: {0}".format(sys.argv))
