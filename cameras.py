import requests, xmltodict, check_license, get_iccid, credentials
from datetime import date, datetime


#Make API calls to get new device ID, insert record, and return the ID.
def get_new_device_id():

    #Get new unique device ID.
    URL = ("%s/devices/getNewID" % credentials.db_address)

    new_device_id = requests.get(url=URL).json()
    
    #Insert new device record.
    URL = ("%s/devices/inputDevice" % credentials.db_address)

    PARAMS = {'device_id': new_device_id, 'device_type': '2', 'iccid': iccid}

    r = requests.post(url=URL, data=PARAMS)

    print(r.text)

    return new_device_id

#Before inserting/updating, compare if any changes have occurred and to insert change into changelog table.
def camera_changelog():
    #Request url.
    request_url = ("http://%s/ISAPI/System/Video/inputs/channels" % credentials.ipAddress)
    auth = requests.auth.HTTPDigestAuth(credentials.username, credentials.password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_video = json_data["VideoInputChannelList"]["VideoInputChannel"]

        #MAKE COMPARISON BETWEEN LAST LOGGED RECORD AND NEW ONE IF ONE EXISTS, WRITE CHANGES TO CHANGELOG.
        current_video_data = []
        stored_video_data = []
        changelog_data = []

        #Get current camera values from Hikvision API and store in array.
        for data in json_video:
            current_video_data.append([data["id"], data["name"], data["resDesc"]])

        #Loop through data stored in array to query database for relating records with the same camera ID.
        for data in current_video_data:
            camera_id = data[0]

            #Call API to check if camera ID exists.
            URL = ("%s/camera/getCamera" % credentials.db_address)
            PARAMS = {'camera_id' : camera_id, 'iccid' : iccid}
            stored_camera = requests.post(url=URL, data=PARAMS)

            #If query returns results, loop through and save found values to an array for comparison. 
            if len(stored_camera.text) > 3 and stored_camera.status_code != 500:
                stored_values = stored_camera.json()
                stored_video_data.append([stored_values["id"], stored_values["device_id"], stored_values["name"], stored_values["status"]])
            else:
                #If first entry input null value.
                stored_video_data.append(["null", "null", "null", "null"])

        #Iterate through and compare data from API to database array, provided a database entry exists.
        if len(stored_video_data) > 0:
            for i in range(len(current_video_data)):
                #Check if videoID is the same..
                if str(current_video_data[i][0]) == str(stored_video_data[i][0]):
                    #Check if camera status is different.
                    if str(current_video_data[i][2]) != str(stored_video_data[i][3]):
                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % credentials.db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_video_data[i][1], "status changed", stored_video_data[i][3], current_video_data[i][2], date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_video_data[i][0]} status changed from output {stored_video_data[i][3]} to {current_video_data[i][2]} at {datetime.now().strftime("%H:%M:%S")}.')

                    else:

                        print(f'Camera {current_video_data[i][0]} is showing no changes at {datetime.now().strftime("%H:%M:%S")}.')

        #Check if any changes are to be made.
        if len(changelog_data) > 0:
            for i in range(len(changelog_data)):
                #Call API to insert any changelogs.
                URL = ("%s/changelog/insertLog" % credentials.db_address)
                PARAMS = {'changelog_id' : changelog_data[i][0], 'device_id' : changelog_data[i][1], 'changelog_desc' : changelog_data[i][2], 'previous_status' : changelog_data[i][3], 'current_status' : changelog_data[i][4], 'changelog_date' : changelog_data[i][5], 'changelog_time' : changelog_data[i][6]}
                request_site = requests.post(url=URL, data=PARAMS)
                print(request_site.text)
        else:
            print("No changes to be made.")

#Call changelog function then insert or update camera record.
def get_video_info():
    #Request url.
    request_url = ("http://%s/ISAPI/System/Video/inputs/channels" % credentials.ipAddress)
    auth = requests.auth.HTTPDigestAuth(credentials.username, credentials.password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_video = json_data["VideoInputChannelList"]["VideoInputChannel"]

        #Call function to make a check for any changes and insert a new changelog prior to any amendments to the database.
        camera_changelog()
        
        #Loop through camera data recieved from Hikvision API.
        for data in json_video:

            URL = ("%s/camera/getCamera" % credentials.db_address)

            PARAMS = {'camera_id' : str(data["id"]), 'iccid' : iccid}

            camera_exists = requests.post(url=URL, data=PARAMS)

            #If length of values returned is greater than 1 then the record exists and to update it. Else input a new record. 
            if len(camera_exists.text) > 3 and camera_exists.status_code != 500:
                camera_values = camera_exists.json()

                URL = ("%s/camera/updateCamera" % credentials.db_address)

                PARAMS = {'device_id' : camera_values["device_id"], 'camera_name': data["name"], 'camera_status' : data["resDesc"], 'check_date': date.today(), 'check_time': datetime.now().strftime("%H:%M:%S")}

                r = requests.post(url=URL, data=PARAMS)

                print(r.text)
            elif camera_exists.status_code != 500:

                new_device_id = get_new_device_id()

                URL = ("%s/camera/inputCamera" % credentials.db_address)

                PARAMS = {'camera_id': str(data["id"]), 'device_id': new_device_id, 'camera_name': data["name"], 'camera_status' : data["resDesc"], 'check_date': date.today(), 'check_time': datetime.now().strftime("%H:%M:%S")}

                r = requests.post(url=URL, data=PARAMS)

                print(r.text)
            else:
                print("Server Error Status Code: %s" % camera_exists.status_code)
    else:
        print(response.text) 


#Check if ICCID is able to be retrieved.
if get_iccid.get_sim_iccid() != "Unable to get ICCID.":
    iccid = get_iccid.get_sim_iccid()
    #Get data from API of whether the Pi has been activated or is suspended and if to continue with processing. 
    if check_license.get_license(iccid) == True:
        try:
            #Call function to insert or update camera table, and check for any changes to be inserted into changelog table.
            get_video_info()
        except:
            print("Unable to get camera data.")
    else:
        print("Pi not activated or license suspended.")
else:
    print("Unable to get ICCID.")