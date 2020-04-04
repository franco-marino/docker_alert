import argparse
import os
import sys

"""
Check if the env argument is a valid file
If it is not a valid file raise an ArgumentTypeError error
"""
def check_env(env):
    if os.path.isfile(env):
        return env
    else:
        msg = f"Not a valid env file: {env}"
        raise argparse.ArgumentTypeError(msg)

"""
Returns script arguments if there are no errors, None otherwise
"""
def init_args():
    try:
        # Parser initialization
        parser = argparse.ArgumentParser()

        # Required arguments
        parser.add_argument("env", help="Your env file path", type=check_env)

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

        # Return
        return args
    except SystemExit as e:
        print(f"Invalid args: {sys.argv}")
