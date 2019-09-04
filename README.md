
# Docker HealthCheck Alert System

### Introduction
**This python3 script sends you emails and Telegram notifications when a docker container becomes unhealthy or when it isn't running.**

This same work can be done with other monitor tools (check for example [cAdvisor](https://github.com/google/cadvisor), [Prometheus](https://hub.docker.com/r/prom/prometheus/)...), but it may be over-killing for your scenario.

The key points of Docker HealthCheck Alert System are **simplicity**, **lightness** and the **few dependencies** required.

At *UniMI* (*University of Milan*), we use it as a part of monitoring system for our CTF challenges.

### Screenshot
![Screenshot image](https://raw.githubusercontent.com/franco-marino/docker_alert/master/img/001.png)

### Setup, requirements and config

 - Firstly, be sure to have python3 and python3-pip installed:
   ```
   sudo apt update
   sudo apt install python3-pip
   ```

 - Then move to your favorite folder, download source and install requirements:
   ```
    git clone https://github.com/franco-marino/docker_alert.git
    cd docker_alert
    pip3 install -r requirements.txt
    ```

 - Edit configuration parameters inside .env.production (for Telegram you need a working bot; if you don't know about it [see here](https://core.telegram.org/bots))<br>
Remember that TELEGRAM_CHANNEL_ID can also be the ID of a chat the bot is having with you.<br>
Remember that LOG_PATH must be an absolute path and not a relative path.

 - Setup a docker container with a working [healthcheck](https://docs.docker.com/engine/reference/builder/#healthcheck)<br>
**PAY ATTENTION: containers without healthcheck won't be monitored!**

 - Setup your crontab (not necessarily on root user) using `crontab -e`<br>
 The following example will alert you on Telegram every 10 minutes only if there are unhealthy docker containers:
    ```
    */10 * * * * python3 /your/absolute/path/docker_alert/main.py --telegram /your/absolute/path/docker_alert/.env.production >/dev/null 2>&1
    ```

### Usage

```Bash
python3 main.py -h

usage: main.py [-h] [--telegram] [--mail] [--stdout] env

positional arguments:
  env         Your env file path

optional arguments:
  -h, --help  show this help message and exit
  --not-running  Receive alerts also for not running containers (created,
                 exited, paused, dead, restarting)

alert options:
  --telegram  Receive alerts through a telegram bot
  --mail      Receive alerts via mail
  --stdout    Print unhealthy containers to stdout (if there aren't the output
              will be empty)
```
You can of course combine alert options to receive them in multiple ways (e.g. Telegram & mail).

### Exit codes

To improve automation, the process related to this script ends with an exit code different from 0 in case some problem has occurred.<br>
This, among other things, allows the script to **not stop if an error occurs, completing the sending of the remaining alerts**.<br>
Here is the list of all possible exit codes (in bash you can check them with `echo $?` after using the script):<br>

 - 0: successful (no errors occurred)
 - 1: errors parsing arguments
 - 2: errors parsing the .env config file
 - 3: communication errors (email/telegram unreachable or permission error writing to stdout)

If multiple errors occurs, the exit code refers to the first.<br>
If an error occurs, you can find more detailed information in the logs (see below section).

### Log system

The script save detailed logs inside the log path set in the .env config file.<br>
Log files are rotated based on their size and you can set their max size and their maximum number with appropriate configurations in the .env file.<br>
In addition, the script saves a file called "log" inside its own folder in case of errors retrieving the log path from the .env file.

### To-do list
 - Add a setting to adjust the minimum log level, in order to leave the choice to the user
 - We aim to integrate more ways to receive alerts, like Slack or Facebook.<br>
 If you need a particular one, or you want to collaborate, feel free to open an issue or a pull request.

### Credits

Coded by [Franco Marino](https://github.com/franco-marino) & reviewed by [Jacopo Tediosi](https://github.com/jacopotediosi)<br>
Inspired by [Monitor-Code-Slack](https://github.com/dennyzhang/monitor-docker-slack)
