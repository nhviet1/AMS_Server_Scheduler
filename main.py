# ================Import Library=================
import os
import db_query
import time
import configparser
import file_manager
import log_writer
import layout_media_controller
# ===============================================

# ==========================Main Program====================================
# ==============Read config data=================
log_writer.write_log("AMS_Client Start!")
config_reader = configparser.ConfigParser()
config_reader.sections()
config_reader.read("config.ini")
config_reader.sections()
# Database config
ams_server_name = config_reader["AMS_SERVER"]["server_name"]
ams_user_name = config_reader["AMS_SERVER"]["user_name"]
ams_password = config_reader["AMS_SERVER"]["password"]
ams_db_name = config_reader["AMS_SERVER"]["db_name"]
ftp_folder_path = config_reader["FTP"]["ftp_folder"]
# Clear old media in FTP folder
list_file = os.listdir(ftp_folder_path)                                         # Get all file in ftp delay folder
list_file.sort(key=lambda x: os.path.getmtime(ftp_folder_path + "\\" + x))      # Sort list by created date
if len(list_file) > 2:
    for i in range(0, len(list_file)-2):
        try:
            os.remove(ftp_folder_path + "\\" + list_file[i])
        except:
            log_writer.write_log("File %s not found", list_file[i])
# Clear old media in AMS library
db_query.clear_old_media_library()
# Create new threads
log_writer.write_log("Create schedule thread")
layout_thread = layout_media_controller.LayoutControlThread()
# Start new Threads
log_writer.write_log("Start thread")
layout_thread.start()
# ===========Main loop============
while True:
    list_file = os.listdir(ftp_folder_path)                                         # Get all file in ftp delay folder
    list_file.sort(key=lambda x: os.path.getmtime(ftp_folder_path + "\\" + x))      # Sort list by created date
    if len(list_file) > 0:
        for f in list_file:
            # 1.Insert media's info into database, update name to "MEDIA_TEMP"
            if not db_query.is_moved(f):
                db_query.insert_media(ftp_folder_path, f)
                # 2.Move file from FTP to AMS library and update "MEDIA_TEMP" table
                if file_manager.check_md5(ftp_folder_path, f):
                    try:
                        file_manager.move_cmd(f, db_query.get_new_name(f), ftp_folder_path, db_query.get_ams_path())
                        db_query.update_media_temp(f, "1", db_query.get_new_name(f))
                    except:
                        log_writer.write_log("File %s \not found", f)
    time.sleep(10)
# ================================
# ============================

