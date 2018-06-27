import configparser
import MySQLdb
import hashlib
import log_writer
import os
import os.path


# ==========Function: Connect to database=============
# Arguments:            [1]
# Arguments:    [FTP Folder Path]
# GET DATABASE CONNECTION
def get_conn():
    config = configparser.ConfigParser()
    config.sections()
    config.read("config.ini")
    config.sections()

    host = str(config["AMS_SERVER"]["server_name"])
    user = str(config["AMS_SERVER"]["user_name"])
    password = str(config["AMS_SERVER"]["password"])
    db = str(config["AMS_SERVER"]["db_name"])

    db = MySQLdb.connect(host=host, user=user, passwd=password, db=db)
    return db
# ====================================================


# ==========Function: Get the next auto increment value in table=============
# Arguments:      [1]           [2]
# Arguments: [Db Name]     [Table Name]
def get_next_id(db_name, table_name):
    # Connect database
    db = get_conn()

    # Create a Cursor object to execute queries.
    cur = db.cursor()
    query = "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = '" + db_name + \
            "' AND TABLE_NAME = '" + table_name + "'"
    cur.execute(query)
    rows = cur.fetchall()
    result = 0
    for row in rows:
        result = row[0]
    db.close()
    return result
# ==========================================================================


# ==========Function: Update media's info in "MEDIA_TEMP" table=============
# Arguments:    [1]               [2]           [3]
# Arguments: [Original Name]  [Is Moved]    [New Name]
def update_media_temp(original_name, is_move, to_name):
    db = get_conn()
    query = 'UPDATE media_temp SET isMoved=%s, toName=%s WHERE fromName=%s '
    data = (is_move, to_name, original_name)

    cur = db.cursor()
    cur.execute(query, data)
    db.commit()
    db.close()
# ==========================================================================


# ==============Function: Insert media's info into AMS library==============
# Arguments:         [1]            [2]
# Arguments:    [Folder Path]   [File Name]
def insert_media(folder_path, file_name):
    # Get file's info
    insert_config_reader = configparser.ConfigParser()
    insert_config_reader.sections()
    insert_config_reader.read("config.ini")
    insert_config_reader.sections()

    media_id = str(get_next_id("gdsadmin", "MEDIA"))
    media_type = str(insert_config_reader["MEDIA"]["type"])
    media_duration = str(insert_config_reader["MEDIA"]["duration"])
    md5 = str(hashlib.md5(open(folder_path + "\\" + file_name, 'rb').read()).hexdigest())
    file_size = str(os.path.getsize(folder_path + "\\" + file_name))
    user_id = str(insert_config_reader["MEDIA"]["user_id"])
    retired = str(insert_config_reader["MEDIA"]["is_retired"])
    is_edited = str(insert_config_reader["MEDIA"]["is_edited"])
    edited_id = str(insert_config_reader["MEDIA"]["edited_media_id"])
    module_file = str(insert_config_reader["MEDIA"]["module_system_file"])
    valid = str(insert_config_reader["MEDIA"]["valid"])
    expires = str(insert_config_reader["MEDIA"]["expires"])

    # Insert media's info into "MEDIA" table
    query = "INSERT INTO `media`(`mediaID`, `name`, `type`, " \
            "`duration`, `originalFilename`, `storedAs`," \
            " `MD5`, `FileSize`," \
            " `userID`, `retired`, `isEdited`, `editedMediaID`, `moduleSystemFile`, `valid`, `expires`) " \
            "VALUES (null,'" + file_name + "','" + media_type + "'," \
            + media_duration + ",'" + file_name + "','" + media_id + ".mp4'," \
            "'" + md5 + "','" + file_size + "'," \
            "" + user_id + "," + retired + "," + is_edited + "," + edited_id + "," + module_file + \
            "," + valid + "," + expires + ")"

    db = get_conn()
    cur = db.cursor()
    try:
        # log_writer.write_log("Insert media temp into database.")
        cur.execute(query)
        db.commit()
    except:
        log_writer.write_log("Insert error!")
        db.rollback()
    db.close()
    # Update new name (media's ID)
    update_media_temp(file_name, "0", media_id + ".mp4")
# ==========================================================================


# ==============Function: Get "toName" of file in FTP folder==============
# Arguments:        [1]
# Arguments:    [File Name]
def get_new_name(file_name):
    db = get_conn()
    query = "SELECT toName FROM media_temp WHERE fromName = '" + file_name + "'"

    cur = db.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    result = 0
    for row in rows:
        result = row[0]
    db.close()
    return result
# ===========================================================================


# ==============Function: Get AMS library location==============
# Arguments:        [1]
# Arguments:    [File Name]
def get_ams_path():
    db = get_conn()
    query = 'SELECT value FROM setting WHERE setting = "LIBRARY_LOCATION" '

    cur = db.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    result = 0

    for row in rows:
        result = row[0]
    db.close()
    return result
# ==============================================================


# ==============Function: Check if file is moved to AMS library==============
# Arguments:        [1]
# Arguments:    [File Name]
def is_moved(file_name):
    db = get_conn()
    query = "SELECT isMoved FROM media_temp WHERE fromName= '" + file_name + "'"

    cur = db.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    result = -1  # NOT FOUND+

    for row in rows:
        if row[0] != "":
            result = row[0]
    db.close()
    return result
# ===========================================================================


# ==============Function: Get MD5 check of media==============
# Arguments:        [1]
# Arguments:    [File Name]
def get_md5(file_name):
    db = get_conn()
    query = "SELECT MD5 FROM media WHERE originalFilename='" + file_name + "'"

    cur = db.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    result = 0

    for row in rows:
        result = row[0]
    db.close()
    return result
# ============================================================


# ==============Function: Clear old streaming media in AMS library==============
# Arguments:
# Arguments:
def clear_old_media_library():
    folder_path = get_ams_path()
    list_file = os.listdir(folder_path)
    for f in list_file:
        try:
            # ext = os.path.splitext()
            if os.path.isfile(folder_path + f):
                query = "SELECT `mediaID` FROM `media` WHERE `storedAs` = \'" + f + "\'"
                # print(query)
                db = get_conn()
                cur = db.cursor()
                cur.execute(query)
                rows = cur.fetchall()
                if len(rows) == 0:
                    os.remove(folder_path + f)
                db.close()
        except Exception as e:
            log_writer.write_log(e)
    return
# ===========================================


# ==============Function: Get mediaID in "MEDIA" table==============
# Arguments:        [1]
# Arguments:    [File Name]
def get_media_id(file_name):
    db = get_conn()
    query = "SELECT `mediaID` FROM `media` WHERE `storedAs` = \"" + file_name + "\""

    cur = db.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    result = 0

    for row in rows:
        result = row[0]
    db.close()
    return result
# ====================================================================


# ==============Function: Set media to AMS_Streaming_Layout==============
# Arguments
# Arguments:
def set_streaming_media(media_name, layout_id):
    media_id = get_media_id(media_name)
    query_1 = 'UPDATE `layout` SET `xml`=' \
        '"<?xml version=""1.0""?>' \
        '<layout width=""1920"" height=""1080"" resolutionid=""9"" bgcolor=""#000000"" schemaVersion=""2"">' \
        '<region id=""5af3fb9e0838c"" userId=""1"" width=""1920"" height=""1080"" top=""0"" left=""0"">' \
        '<media id=""' + str(media_id) + \
        '"" type=""video"" render=""native"" duration=""120"" lkid=""26"" userId=""1"" schemaVersion=""1"">' \
        '<options><uri>' + str(media_name) +\
        '</uri></options><raw/></media></region></layout>" ' \
        'WHERE `layoutID`=' + str(layout_id)
    query_2 = 'UPDATE `lklayoutmedia` SET `mediaID`=' + str(media_id) + ' WHERE `layoutID`= ' + str(layout_id)
    query_3 = 'UPDATE `lklayoutmediagroup` SET `MediaID`=' + str(media_id) + ' WHERE `LayoutID`= ' + str(layout_id)
    # print(query_1)
    # print(query_2)
    # print(query_3)
    db = get_conn()
    cur = db.cursor()
    cur.execute(query_1)
    db.commit()
    cur.execute(query_2)
    db.commit()
    cur.execute(query_3)
    db.commit()
    db.close()
# =============================================================


# ==============Function: Set media to AMS_Buffer_Layout==============
# Arguments
# Arguments:
def set_buffer_media(media_name, layout_id):
    media_id = get_media_id(media_name)
    query_1 = 'UPDATE `layout` SET `xml`=' \
        '"<?xml version=""1.0""?>' \
        '<layout width=""1920"" height=""1080"" resolutionid=""9"" bgcolor=""#000000"" schemaVersion=""2"">' \
        '<region id=""5b1510e8a0d9a"" userId=""1"" width=""1920"" height=""1080"" top=""0"" left=""0"">' \
        '<media id=""' + str(media_id) + \
        '"" type=""video"" render=""native"" duration=""120"" lkid=""55"" userId=""1"" schemaVersion=""1"">' \
        '<options><uri>' + str(media_name) +\
        '</uri></options><raw/></media></region></layout>" ' \
        'WHERE `layoutID`=' + str(layout_id)
    query_2 = 'UPDATE `lklayoutmedia` SET `mediaID`=' + str(media_id) + ' WHERE `layoutID`= ' + str(layout_id)
    query_3 = 'UPDATE `lklayoutmediagroup` SET `MediaID`=' + str(media_id) + ' WHERE `LayoutID`= ' + str(layout_id)
    # print(query_1)
    # print(query_2)
    # print(query_3)
    db = get_conn()
    cur = db.cursor()
    cur.execute(query_1)
    db.commit()
    cur.execute(query_2)
    db.commit()
    cur.execute(query_3)
    db.commit()
    db.close()
# =============================================================


