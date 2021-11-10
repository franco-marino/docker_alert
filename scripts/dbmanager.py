import sqlite3
import logging
import datetime
from os import getenv

class DbManager:
    """
    Constructor for DbManager class
    """
    def __init__(self):
        # Get logger
        self.logger = logging.getLogger("docker_alert")

        # Create DB
        self.conn = sqlite3.connect(getenv("DB_PATH"), detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.logger.debug("Connected to database")

        # Create tables
        self.__create_tables()

    """
    Private method user to create tables
    """
    def __create_tables(self):
        # Get conn cursor
        c = self.conn.cursor()
        # Create table queries
        c.execute(
            """
                CREATE TABLE IF NOT EXISTS container_statuses (
                    id INTEGER PRIMARY KEY,
                    container_name TEXT NOT NULL,
                    container_status TEXT NOT NULL
                );
            """
        )
        c.execute(
            """
                CREATE TABLE IF NOT EXISTS script_errors (
                    id INTEGER PRIMARY KEY,
                    error_type TEXT NOT NULL,
                    insert_date TEXT NOT NULL
                );
            """
        )
        # Commit and close cursor
        self.conn.commit()
        c.close()
        # Log
        self.logger.debug("Created tables")

    """
    Returns the container_status that was associated to the container_name into DB
    Update container_status in the DB if different from how it is now or if not present
    """
    def check_container_status(self, container_name, new_container_status):
        # Get conn cursor
        c = self.conn.cursor()

        # Get container_name row
        c.execute("SELECT container_status FROM container_statuses WHERE container_name=?", (container_name,))
        row = c.fetchone()

        if not row:
            # If not present, insert it into DB
            c.execute("INSERT INTO container_statuses (container_name,container_status) VALUES (?,?)", (container_name,new_container_status))
            self.conn.commit()
            self.logger.debug(f"{container_name} was not present into DB; added")
            old_container_status = new_container_status
        else:
            old_container_status = row[0]
            # If changed, update it into DB
            if old_container_status != new_container_status:
                c.execute("UPDATE container_statuses SET container_status=? WHERE container_name=?", (new_container_status, container_name))
                self.conn.commit()
                self.logger.debug(f"Updated {container_name} into DB: {old_container_status} --> {new_container_status}")

        # Close conn cursor
        c.close()            

        # Return old_container_status
        return(old_container_status)

    """
    Check if the given error_type was already into DB:
    - If it wasn't present, add it and returns True
    - If it was already present, update its insert_date and returns True if insert_date+hours_delay was older than now; False otherwise
    """
    def check_script_error(self, error_type, hours_delay):
        # Get conn cursor
        c = self.conn.cursor()

        # Check if present
        c.execute('SELECT insert_date "[timestamp]" FROM script_errors WHERE error_type=?', (error_type,))
        row = c.fetchone()

        # If it wasn't present
        if not row:
            # Add it
            c.execute("INSERT INTO script_errors (error_type, insert_date) VALUES (?,?)", (error_type, datetime.datetime.now()))
            self.conn.commit()
            self.logger.debug(f"{error_type} wasn't present into DB and got inserted")
            # Return True
            return True
        # If it was already present
        else:
            # Get old_insert_date and new_insert_date
            old_insert_date = row[0]
            new_insert_date = datetime.datetime.now()
            # Update its insert_date
            c.execute("UPDATE script_errors SET insert_date=? WHERE error_type=?", (new_insert_date, error_type))
            self.conn.commit()
            self.logger.debug(f"{error_type} was present into DB and it's insert_date got updated: {old_insert_date} --> {new_insert_date}")
            # Return True if insert_date+hours_delay was older than now; False otherwise
            return ( old_insert_date < new_insert_date-datetime.timedelta(hours=int(hours_delay)) )

    """
    Remove the given error_type from DB, returns True if it was present; False otherwise
    """
    def delete_script_error(self, error_type):
        # Get conn cursor
        c = self.conn.cursor()

        # Delete row corresponding to script_errors
        c.execute("DELETE from script_errors WHERE error_type=?", (error_type,))
        self.conn.commit()

        # Return True if it removed something; False otherwise
        if c.rowcount >= 1:
            self.logger.debug(f"{error_type} was present into DB and got deleted")
            return True
        else:
            self.logger.debug(f"{error_type} wasn't present into DB during deletion")
            return False
