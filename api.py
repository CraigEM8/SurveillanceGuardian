import mysql.connector, random
from flask import Flask, request

#Define Flask app.
app = Flask(__name__)
application = app


mydb = mysql.connector.connect(
        host = "localhost",
        user = "em8database_em8database",
        password = "K108dls2506!",
        database = "em8database_SurveillanceGuardian"
        )


###########################################################################

#GENERAL ENDPOINTS

###########################################################################


#Default root.
@app.route('/')
def test():
    return 'EM8 API!'
    

#Get ICCID for specific site.
@app.route('/devices/getICCID/<int:site_id>')
def getICCID(site_id):
    
    mycursor = mydb.cursor()

    #Joining Sites and Pi table to get ICCID linked with Site.
    mycursor.execute("SELECT sites.site_id, sg_pi.iccid FROM sites INNER JOIN sg_pi ON sites.site_id = sg_pi.site_id")
    
    myresult = mycursor.fetchall()

    #Initalising iccid variable in case 'if' statement in 'for' loop does not find a match. 
    iccid = (f"No ICCID found for Site ID: {site_id}")

    #Check if query returned data.
    if myresult:
        for data in myresult:
            #Getting ICCID of Pi linked with Site ID.
            if data[0] == site_id:
                iccid = data[1]
        
        return (f"{iccid}")
    else:
        return (f"No ICCID found for Site ID: {site_id}")
    

#Get Site ID for given ICCID.
@app.route('/sites/getSiteID', methods=['POST'])
def getSiteID():
    #Request parameters.
    if request.method == 'POST':
        iccid = request.form['iccid']
    
        mycursor = mydb.cursor()

        #Joining Sites and Pi table to get ICCID linked with Site.
        mycursor.execute(f"SELECT `site_id` FROM `sg_pi` WHERE `iccid` = '{iccid}'")
        
        myresult = mycursor.fetchall()

        #Initalising site_id variable in case 'if' statement in 'for' loop does not find a match. 
        site_id = (f"No Site found for ICCID: {iccid}")

        #Check if query returned data.
        if myresult:
            for data in myresult:
                #Getting Site ID from query results.
                site_id = data[0]
            
            return (f"{site_id}")
        else:
            return (f"{site_id}")


###########################################################################

#DEVICE ENDPOINTS

###########################################################################


#Get new device ID.
@app.route('/devices/getNewID')
def get_new_device_id():
    getID = False

    mycursor = mydb.cursor()

    #Loop indefinetly generating a potential ID, checking if it exists until a unique one is found.
    while getID == False:
        device_id = random.randint(1, 2147483646)

        #Query database for existing changelog id.
        mycursor.execute(f"SELECT `device_id` FROM `sg_devices` WHERE `device_id` = '{str(device_id)}'")
        result = mycursor.fetchall()

        if len(result) < 1:
            getID = True

    return (f"{device_id}")


#Insert a new device record into the sg_devices table.
@app.route('/devices/inputDevice', methods=['POST'])
def insert_device():

    #Request parameters.
    if request.method == 'POST':
        device_id = request.form['device_id']
        device_type = request.form['device_type']
        iccid = request.form['iccid']

        mycursor = mydb.cursor()

        #Query if device already exists in database.
        mycursor.execute(f"SELECT * FROM `sg_devices` WHERE `device_id` = '{device_id}'")
        device_exists = mycursor.fetchall()

        #If device exists go to insert database record.
        if len(device_exists) == 0:
            mycursor.execute(f"INSERT INTO `sg_devices` (`device_id`, `device_type`, `iccid`) VALUES ('{device_id}', '{device_type}', '{iccid}')")
            mydb.commit()
            return ("record input")
        else:
            return ("Device record already exists in database.")


@app.route('/devices/getDeviceID', methods=['POST'])
def get_device_id():
    #Request parameters.
    if request.method == 'POST':
        device_id = request.form['device_id']

        mycursor = mydb.cursor()

        #Query database for existing system records.
        mycursor.execute(f"SELECT * FROM `sg_system` WHERE `device_id` = '{device_id}'")
        query_result = mycursor.fetchall()

        getData = []

        for data in query_result:
            getData = {"device_id" : data[0], "device_type" : data[1], "iccid" : data[2]}

        return getData


#Get all devices linked to an ICCID.
@app.route('/devices/getDevices/<int:iccid>')
def getDevices(iccid):
    
    mycursor = mydb.cursor()

    #Get Device data for specified ICCID.
    mycursor.execute(f"SELECT `device_id`, `device_type` FROM `sg_devices` WHERE `iccid` = '{iccid}'")

    myresult = mycursor.fetchall()

    #Check if query returned data.
    if myresult:
        return myresult
    else:
        return (f"No Devices found for ICCID: {iccid}")

        
###########################################################################

#CAMERA ENDPOINTS

###########################################################################
    

#Get stored camera data for a given camera ID.
@app.route('/camera/getCamera', methods=['POST'])
def getCamera():
    #Request parameters.
    if request.method == 'POST':
        camera_id = request.form['camera_id']
        iccid = request.form['iccid']

        mycursor = mydb.cursor()

        mycursor.execute("SELECT cameras.device_id FROM cameras INNER JOIN sg_devices ON sg_devices.device_id = cameras.device_id WHERE cameras.camera_id = '%s'" % camera_id + " AND sg_devices.iccid = '%s' AND sg_devices.device_type = '2'" % iccid)
        get_device_id = mycursor.fetchall()

        #Initialise variables.
        device_id = '0'
        getData = []

        for data in get_device_id:
            device_id = str(data[0])

        #Query database for existing camera records.
        if int(device_id) > 0:
            mycursor.execute(f"SELECT * FROM `cameras` WHERE `device_id` = '{device_id}'")
            stored_camera = mycursor.fetchall()

            for data in stored_camera:
                getData = {"id" : data[0], "device_id" : data[1], "name" : data[2], "status" : data[3]}

            return getData
        else:
            return getData


#Insert a new camera record into the cameras table.
@app.route('/camera/inputCamera', methods=['POST'])
def insert_camera():

    #Request parameters.
    if request.method == 'POST':
        camera_id = request.form['camera_id']
        device_id = request.form['device_id']
        camera_name = request.form['camera_name']
        camera_status = request.form['camera_status']
        check_date = request.form['check_date']
        check_time = request.form['check_time']

        mycursor = mydb.cursor()

        #Query if camera already exists in database.
        mycursor.execute(f"SELECT * FROM `cameras` WHERE `device_id` = '{device_id}'")
        camera_exists = mycursor.fetchall()

        #If camera exists go to update database record.
        if len(camera_exists) == 0:
            mycursor.execute(f"INSERT INTO `cameras` (`camera_id`, `device_id`, `camera_name`, `camera_status`, `check_date`, `check_time`) VALUES ('{camera_id}', '{device_id}', '{camera_name}', '{camera_status}', '{check_date}', '{check_time}')")
            mydb.commit()
            return ("record input")
        else:
            return ("Camera record already exists in database.")
        

#Update an existing camera record by camera ID.
@app.route('/camera/updateCamera', methods=['POST'])
def update_camera():

    #Request parameters.
    if request.method == 'POST':
        device_id = request.form['device_id']
        camera_name = request.form['camera_name']
        camera_status = request.form['camera_status']
        check_date = request.form['check_date']
        check_time = request.form['check_time']

        mycursor = mydb.cursor()

        #Query if camera already exists in database.
        mycursor.execute(f"SELECT * FROM `cameras` WHERE `device_id` = '{device_id}'")
        camera_exists = mycursor.fetchall()

        #If camera exists go to update database record.
        if len(camera_exists) > 0:
            mycursor.execute(f"UPDATE `cameras` SET `camera_name` = '{camera_name}', `camera_status` = '{camera_status}', `check_date` = '{check_date}', `check_time` = '{check_time}' WHERE `device_id` = '{device_id}'")
            mydb.commit()
            return ("record updated")
        else:
            return ("No Camera ID found.")
        

###########################################################################

#CHANGELOG ENDPOINTS

###########################################################################


#Get new changelog ID.
@app.route('/changelog/getNewID')
def get_new_changelog_id():
    getID = False

    mycursor = mydb.cursor()

    #Loop indefinetly generating a potential ID, checking if it exists until a unique one is found.
    while getID == False:
        changelog_id = random.randint(1, 2147483646)

        #Query database for existing changelog id.
        mycursor.execute(f"SELECT `changelog_id` FROM `changelog` WHERE `changelog_id` = '{str(changelog_id)}'")
        result = mycursor.fetchall()

        if len(result) < 1:
            getID = True

    return (f"{changelog_id}")


#Insert new changelog record. 
@app.route('/changelog/insertLog', methods=['POST'])
def insert_changelog():

    #Request parameters.
    if request.method == 'POST':
        changelog_id = request.form['changelog_id']
        device_id = request.form['device_id']
        changelog_desc = request.form['changelog_desc']
        previous_status = request.form['previous_status']
        current_status = request.form['current_status']
        changelog_date = request.form['changelog_date']
        changelog_time = request.form['changelog_time']

        mycursor = mydb.cursor()

        mycursor.execute(f"INSERT INTO `changelog` (`changelog_id`, `device_id`, `changelog_desc`, `previous_status`, `current_status`, `changelog_date`, `changelog_time`) VALUES ('{changelog_id}', '{device_id}', '{changelog_desc}', '{previous_status}', '{current_status}', '{changelog_date}', '{changelog_time}')")
        mydb.commit()
        return ("record input")
        

###########################################################################

#STORAGE ENDPOINTS

###########################################################################


#Input new storage log.
@app.route('/storage/inputStorage', methods=['POST'])
def insert_storage_log():

    #Request parameters.
    if request.method == 'POST':
        storage_id = request.form['storage_id']
        device_id = request.form['device_id']
        storage_name = request.form['storage_name']
        storage_status = request.form['storage_status']
        check_date = request.form['check_date']
        check_time = request.form['check_time']

        mycursor = mydb.cursor()

        #Query if storage device already exists in database.
        mycursor.execute(f"SELECT * FROM `sg_storage` WHERE `device_id` = '{device_id}'")
        storage_device_exists = mycursor.fetchall()
    
        #Check if storage ID is valid and insert storage log.
        if len(storage_device_exists) == 0:
            sql = "INSERT INTO sg_storage (device_id, storage_id, storage_name, storage_status, check_date, check_time) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (int(device_id), storage_id, storage_name, storage_status, check_date, check_time)
            mycursor.execute(sql, values)
            mydb.commit()
            return ("Record inserted successfully.")
        else:
            return ("Storage record already exists in database.")
        

#Get record data by storage ID.
@app.route('/storage/getStorage', methods=['POST'])
def get_storage_logs():
    #Request parameters.
    if request.method == 'POST':
        storage_id = request.form['storage_id']
        iccid = request.form['iccid']

        mycursor = mydb.cursor()

        mycursor.execute("SELECT sg_storage.device_id FROM sg_storage INNER JOIN sg_devices ON sg_devices.device_id = sg_storage.device_id WHERE sg_storage.storage_id = '%s'" % storage_id + " AND sg_devices.iccid = '%s' AND sg_devices.device_type = '1'" % iccid)
        get_device_id = mycursor.fetchall()

        getData = []

        if len(get_device_id) > 0:
            for data in get_device_id:
                device_id = str(data[0])

            getData = []

            #Query database for existing camera records.
            mycursor.execute(f"SELECT * FROM `sg_storage` WHERE `device_id` = '{device_id}'")
            stored_camera = mycursor.fetchall()

            if len(stored_camera) > 0:
                for data in stored_camera:
                    getData = {"device_id" : data[0], "storage_id" : data[1], "name" : data[2], "status" : data[3]}
                return getData
            else:
                getData = {"device_id" : '', "storage_id" : '', "name" : '', "status" : ''}
                return getData
        else:
            return getData


#Update storage status.
@app.route('/storage/updateStorage', methods=['POST'])
def updateStatus():

    #Request parameters.
    if request.method == 'POST':
        device_id = request.form['device_id']
        storage_name = request.form['storage_name']
        storage_status = request.form['storage_status']
        check_date = request.form['check_date']
        check_time = request.form['check_time']

        mycursor = mydb.cursor()

        #Query if storage device already exists in database.
        mycursor.execute(f"SELECT * FROM `sg_storage` WHERE `device_id` = '{device_id}'")
        storage_device_exists = mycursor.fetchall()
    
        #Check if storage ID is valid and insert storage log.
        if len(storage_device_exists) > 0:
            mycursor.execute(f"UPDATE `sg_storage` SET `storage_name` = '{storage_name}', `storage_status` = '{storage_status}', `check_date` = '{check_date}', `check_time` = '{check_time}' WHERE `device_id` = '{device_id}'")
            mydb.commit()
            return ("Storage record updated successfully.")
        else:
            return ("No storage record found to update.")


###########################################################################

#SYSTEM ENDPOINTS

###########################################################################


#Get stored system data for a given system ID.
@app.route('/system/getSystem', methods=['POST'])
def get_system():
    #Request parameters.
    if request.method == 'POST':
        system_id = request.form['system_id']
        iccid = request.form['iccid']

        mycursor = mydb.cursor()

        mycursor.execute("SELECT sg_system.device_id FROM sg_system INNER JOIN sg_devices ON sg_devices.device_id = sg_system.device_id WHERE sg_system.system_id = '%s'" % system_id + " AND sg_devices.iccid = '%s' AND sg_devices.device_type = '3'" % iccid)
        get_device_id = mycursor.fetchall()

        getData = []

        if len(get_device_id) > 0:
            for data in get_device_id:
                device_id = str(data[0])

            #Query database for existing system records.
            mycursor.execute(f"SELECT * FROM `sg_system` WHERE `device_id` = '{device_id}'")
            stored_system = mycursor.fetchall()

            if len(stored_system) > 0:
                for data in stored_system:
                    getData = {"id" : data[0], "device_id" : data[1], "name" : data[2], "status" : data[3], "firmware" : data[4]}
                return getData
            else:
                return getData
        else:
            return getData


#Insert a new system record into the system table.
@app.route('/system/inputSystem', methods=['POST'])
def insert_system():

    #Request parameters.
    if request.method == 'POST':
        system_id = request.form['system_id']
        device_id = request.form['device_id']
        system_name = request.form['system_name']
        system_status = request.form['system_status']
        system_firmware = request.form['system_firmware']
        check_date = request.form['check_date']
        check_time = request.form['check_time']

        mycursor = mydb.cursor()

        #Query if system already exists in database.
        mycursor.execute(f"SELECT * FROM `sg_system` WHERE `device_id` = '{device_id}'")
        system_exists = mycursor.fetchall()

        #If system does not exist go to insert database record.
        if len(system_exists) == 0:
            mycursor.execute(f"INSERT INTO `sg_system` (`system_id`, `device_id`, `system_name`, `system_status`, `system_firmware`, `check_date`, `check_time`) VALUES ('{system_id}', '{device_id}', '{system_name}', '{system_status}', '{system_firmware}', '{check_date}', '{check_time}')")
            mydb.commit()
            return ("record input")
        else:
            return ("System record already exists in database.")
        

#Update an existing system record by system ID.
@app.route('/system/updateSystem', methods=['POST'])
def update_system():

    #Request parameters.
    if request.method == 'POST':
        system_id = request.form['system_id']
        system_name = request.form['system_name']
        system_status = request.form['system_status']
        system_firmware = request.form['system_firmware']
        iccid = request.form['iccid']
        check_date = request.form['check_date']
        check_time = request.form['check_time']

        mycursor = mydb.cursor()

        mycursor.execute("SELECT sg_system.device_id FROM sg_system INNER JOIN sg_devices ON sg_devices.device_id = sg_system.device_id WHERE sg_system.system_id = '%s'" % system_id + " AND sg_devices.iccid = '%s' AND sg_devices.device_type = '3'" % iccid)
        get_device_id = mycursor.fetchall()

        for data in get_device_id:
            device_id = str(data[0])

        #Query if system already exists in database.
        mycursor.execute(f"SELECT * FROM `sg_system` WHERE `device_id` = '{device_id}'")
        system_exists = mycursor.fetchall()

        #If system exists go to update database record.
        if len(system_exists) > 0:
            mycursor.execute(f"UPDATE `sg_system` SET `system_name` = '{system_name}', `system_status` = '{system_status}', `system_firmware` = '{system_firmware}', `check_date` = '{check_date}', `check_time` = '{check_time}' WHERE `system_id` = '{system_id}'")
            mydb.commit()
            return ("record updated")
        else:
            return ("No System ID found.")
        

###########################################################################

#PI ENDPOINTS

###########################################################################


#Get Pi license status.
@app.route('/pi/getLicense', methods=['POST'])
def get_license():

    #Request parameters.
    if request.method == 'POST':
        iccid = request.form['iccid']

        mycursor = mydb.cursor()

        #Query if Pi already exists in database.
        mycursor.execute(f"SELECT `activate_status`, `suspend_status` FROM `sg_pi` WHERE `iccid` = '{iccid}'")
        pi_exists = mycursor.fetchall()

        #If Pi exists return database values.
        if len(pi_exists) > 0:
            return pi_exists
        else:
            return ("No ICCID found.")
        

#Get Pi IP Info.
@app.route('/pi/getInfo', methods=['POST'])
def get_pi():

    #Request parameters.
    if request.method == 'POST':
        iccid = request.form['iccid']

        mycursor = mydb.cursor()

        #Query if Pi already exists in database.
        mycursor.execute(f"SELECT `eth_address`, `ppp_address` FROM `sg_pi` WHERE `iccid` = '{iccid}'")
        pi_exists = mycursor.fetchall()

        #If Pi exists return database values.
        if len(pi_exists) > 0:
            return pi_exists
        else:
            return ("No ICCID found.")
        

#Update an existing Pi record by ICCID.
@app.route('/pi/updateIP', methods=['POST'])
def update_ip():

    #Request parameters.
    if request.method == 'POST':
        iccid = request.form['iccid']
        eth_address = request.form['eth_address']
        ppp_address = request.form['ppp_address']
        check_date = request.form['check_date']
        check_time = request.form['check_time']

        mycursor = mydb.cursor()

        #Query if Pi already exists in database.
        mycursor.execute(f"SELECT * FROM `sg_pi` WHERE `iccid` = '{iccid}'")
        pi_exists = mycursor.fetchall()

        #If Pi exists go to update database record.
        if len(pi_exists) > 0:
            mycursor.execute(f"UPDATE `sg_pi` SET `eth_address` = '{eth_address}', `ppp_address` = '{ppp_address}', `check_date` = '{check_date}', `check_time` = '{check_time}' WHERE `iccid` = '{iccid}'")
            mydb.commit()
            return ("record updated")
        else:
            return ("No ICCID found.")


if __name__ == '__main__':
    app.run(debug=True)