import requests, xmltodict, check_license
from datetime import date, datetime

#Temporary variables for testing.
ipAddress = "192.168.1.143"
username = "admin"
password = "Concept1"
iccid = "8935711001091680386"
db_address = "https://em8database.com/api"


#Make API calls to get new device ID, insert record, and return the ID.
def get_new_device_id():

    #Get new unique device ID.
    URL = ("%s/devices/getNewID" % db_address)

    new_device_id = requests.get(url=URL).json()
    
    #Insert new device record.
    URL = ("%s/devices/inputDevice" % db_address)

    PARAMS = {'device_id': new_device_id, 'device_type': '3', 'iccid': iccid}

    r = requests.post(url=URL, data=PARAMS)

    print(r.text)

    return new_device_id


def system_changelog():
    #Request url.
    request_url = ("http://%s/ISAPI/System/deviceInfo" % ipAddress)
    auth = requests.auth.HTTPDigestAuth(username, password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_system = json_data["DeviceInfo"]

        #MAKE COMPARISON BETWEEN LAST LOGGED RECORD AND NEW ONE IF ONE EXISTS, WRITE CHANGES TO CHANGELOG.
        current_system_data = []
        stored_system_data = []
        changelog_data = []

        #Get current system values from Hikvision API and store in array.
        current_system_data.append([json_system["deviceID"], json_system["deviceName"], 'True', json_system["firmwareVersion"]])

        #Call API to check if system ID exists.
        URL = ("%s/system/getSystem" % db_address)
        PARAMS = {'system_id' : json_system["deviceID"], 'iccid' : iccid}
        stored_system = requests.post(url=URL, data=PARAMS)

        #If query returns results response code is not 500, loop through and save found values to an array for comparison. 
        if len(stored_system.text) > 3 and stored_system.status_code != 500:
            stored_values = stored_system.json()
            stored_system_data.append([stored_values["id"], stored_values["device_id"], stored_values["name"], stored_values["status"], stored_values["firmware"]])
        else:
            #If first entry input null value.
            stored_system_data.append(["null", "null", "null", "null", "null"])
        
        #Iterate through and compare data from API to database array, provided a database entry exists.
        if len(stored_system_data) > 0:
            for i in range(len(stored_system_data)):
                #Check if system ID is the same.
                if str(current_system_data[i][0]) == str(stored_system_data[i][0]):

                    #Check if system status is different.
                    if str(current_system_data[i][2]) != str(stored_system_data[i][3]):
                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_system_data[i][1], "status changed", stored_system_data[i][3], current_system_data[i][2], date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_system_data[i][0]} status changed from output {stored_system_data[i][3]} to {current_system_data[i][2]} at {datetime.now().strftime("%H:%M:%S")}.')
                    
                    #Check if system name has changed.
                    if str(current_system_data[i][1]) != str(stored_system_data[i][2]):

                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_system_data[i][1], "name changed", stored_system_data[i][2], current_system_data[i][1], date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_system_data[i][0]} name changed from output {stored_system_data[i][2]} to {current_system_data[i][1]} at {datetime.now().strftime("%H:%M:%S")}.')

                    #Check if system firmware has changed.
                    if str(current_system_data[i][3]) != str(stored_system_data[i][4]):

                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_system_data[i][1], "firmware changed", stored_system_data[i][4], current_system_data[i][3], date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_system_data[i][0]} name changed from output {stored_system_data[i][4]} to {current_system_data[i][3]} at {datetime.now().strftime("%H:%M:%S")}.')

                    else:
                        print(f'{current_system_data[i][1]} is showing no changes at {datetime.now().strftime("%H:%M:%S")}.')

        #Check if any changes are to be made.
        if len(changelog_data) > 0:
            for i in range(len(changelog_data)):
                #Call API to insert any changelogs.
                URL = ("%s/changelog/insertLog" % db_address)
                PARAMS = {'changelog_id' : changelog_data[i][0], 'device_id' : changelog_data[i][1], 'changelog_desc' : changelog_data[i][2], 'previous_status' : changelog_data[i][3], 'current_status' : changelog_data[i][4], 'changelog_date' : changelog_data[i][5], 'changelog_time' : changelog_data[i][6]}
                request_site = requests.post(url=URL, data=PARAMS)
                print(request_site.text)
        else:
            print("No changes to be made.")

    insert_system_info()


#Insert new or update existing system record.
def insert_system_info():
    #Request url.
    request_url = ("http://%s/ISAPI/System/deviceInfo" % ipAddress)
    auth = requests.auth.HTTPDigestAuth(username, password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_system = json_data["DeviceInfo"]

        URL = ("%s/system/getSystem" % db_address)

        PARAMS = {'system_id': json_system["deviceID"], 'iccid' : iccid}

        system_exists = requests.post(url=URL, data=PARAMS)
        
        #If response code is 200 then the record exists and to update it. Else input a new record. 
        if len(system_exists.text) > 3 and system_exists.status_code != 500:
            URL = ("%s/system/updateSystem" % db_address)

            PARAMS = {'system_id': json_system["deviceID"], 'system_name': json_system["deviceName"], 'system_status' : 'True', 'system_firmware': json_system["firmwareVersion"], 'iccid' : iccid, 'check_date': date.today(), 'check_time': datetime.now().strftime("%H:%M:%S")}
            
            r = requests.post(url=URL, data=PARAMS)

            print(r.text)
        else:

            new_device_id = get_new_device_id()

            URL = ("%s/system/inputSystem" % db_address)

            PARAMS = {'system_id': json_system["deviceID"], 'device_id': new_device_id, 'system_name': json_system["deviceName"], 'system_status' : 'True', 'system_firmware': json_system["firmwareVersion"], 'check_date': date.today(), 'check_time': datetime.now().strftime("%H:%M:%S")}

            r = requests.post(url=URL, data=PARAMS)

            print(r.text)   
    else:
        print(response.status_code)


#############################################

#CHECK SYSTEM TIME WITH LOCAL TIME

# /ISAPI/System/time

#############################################


#Get data from API of whether the Pi has been activated or is suspended and if to continue with processing. 
if check_license.get_license(iccid) == True:
    #Call function to insert or update system table, and check for any changes to be inserted into changelog table.
    system_changelog()
else:
    print("Pi not activated or license suspended.")

