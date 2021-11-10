from urllib.parse import quote
import requests_unixsocket
import requests
from os import getenv
import logging

class ContainerManager:
    """
    Constructor for ContainerManager class
    """
    def __init__(self):
	# Get logger
        self.logger = logging.getLogger("docker_alert")

        # Containers info url
        URL = "http+unix://" + quote(getenv("DOCKER_SOCK_PATH"),safe='') + "/containers/json?all=1"

        # Make request and assign the result to self.containers_json
        session = requests_unixsocket.Session()
        self.containers_json = session.get(URL).json()

    """
    Returns a dictionary in format {container_name: container_status} with statuses of all existing containers
    """
    def get_container_statuses(self):
        # Initialize the container_statuses dictionary
        container_statuses = {}

        # Insert statuses into dictionary
        if len(self.containers_json) > 0:
            for container in self.containers_json:
                if container["Status"].find("unhealthy") != -1:
                    container_status = "unhealthy"
                elif container["Status"].find("Up") != -1:
                    container_status = "healthy"
                else:
                    container_status = container["State"]
                container_statuses[ container['Names'][0][1:] ] = container_status
        else:
            self.logger.info("There aren't containers")

        # Return the dictionary
        return container_statuses
