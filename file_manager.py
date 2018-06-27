import os
import db_query
import hashlib


# ==============Function: Move file using system command==============
# Arguments:         [1]             [2]        [3]                 [4]
# Arguments:    [Original Name]   [To Name] [FTP Folder]    [AMS Library Folder]
def move_cmd(original_name, to_name, ftp_folder, ams_folder):
    # cmd line move file
    command = "move " + str(ftp_folder) + "\\" + str(original_name) + " " + str(ams_folder) + "\\" + str(to_name)
    try:
        os.system(command)
    except OSError:
        print("Error")
# ====================================================================


# ==============Function: Check MD5 valid==============
# Arguments:         [1]                [2]
# Arguments:    [FTP Folder Path]   [File Name]
def check_md5(ftp_folder_path, file_name):
    hash_md5 = hashlib.md5()
    with open(ftp_folder_path + "\\" + file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    if hash_md5.hexdigest() == db_query.get_md5(file_name):
        return 1
    else:
        return 0
# ====================================================

