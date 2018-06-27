import configparser
import datetime


# ===========Function: Write to log file==============
# Arguments:       [1]
# Arguments: [Log Content]
def write_log(str1):
    config = configparser.ConfigParser()
    config.sections()
    config.read("config.ini")
    config.sections()

    # Log config
    is_log = config["LOG"]["is_log"]
    log_file_path = config["LOG"]["full_path"] + str(datetime.date.today()) + ".txt"
    # Open file and write log
    if is_log:
        log_file = open(log_file_path, "w+")
        log_file.writelines(str(datetime.datetime.now()) + ": " + str1)
        log_file.close()
# ====================================================

