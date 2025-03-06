import requests, xmltodict, re, check_license, get_iccid, credentials
from datetime import date, datetime, time

#Make API calls to get new device ID, insert record, and return the ID.
def get_new_device_id():

    iccid = get_iccid.get_sim_iccid()

    #Get new unique device ID.
    URL = ("%s/devices/getNewID" % credentials.db_address)

    new_device_id = requests.get(url=URL).json()
    
    #Insert new device record.
    URL = ("%s/devices/inputDevice" % credentials.db_address)

    PARAMS = {'device_id': new_device_id, 'device_type': '3', 'iccid': iccid}

    r = requests.post(url=URL, data=PARAMS)

    print(r.text)

    return new_device_id


#Return the comparision of current time and system time.
def system_check_datetime():
    #Request url.
    request_url = ("http://%s/ISAPI/System/time" % credentials.ipAddress)
    auth = requests.auth.HTTPDigestAuth(credentials.username, credentials.password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_system_datetime = json_data["Time"]["localTime"]
        current_date = date.today()
        current_time = datetime.now().strftime("%H:%M:%S")
        datetime_array = re.split('T|\+', str(json_system_datetime))
        current_time_array = re.split(':', str(current_time))
        system_time_array = re.split(':', datetime_array[1])
        
        system_time = time(int(system_time_array[0]), int(system_time_array[1]), int(system_time_array[2]))

        #Get time ranges +/-5 of current time to compare if system time is within range. If 5 minutes to/from the hour, calculate correct time range.
        if int(current_time_array[1]) <= int('05'):
            min_time = time(int(current_time_array[0]) - 1, (int(current_time_array[1]) + 50), int(current_time_array[2]))
            max_time = time(int(current_time_array[0]), (int(current_time_array[1]) + 5), int(current_time_array[2]))
        elif int(current_time_array[1]) >= 55:
            min_time = time(int(current_time_array[0]), (int(current_time_array[1]) - 5), int(current_time_array[2]))
            max_time = time(int(current_time_array[0]) + 1, (int(current_time_array[1]) - 50), int(current_time_array[2]))
        else:
            min_time = time(int(current_time_array[0]), (int(current_time_array[1]) - 5), int(current_time_array[2]))
            max_time = time(int(current_time_array[0]), (int(current_time_array[1]) + 5), int(current_time_array[2]))

        #If system datetime is the same as current datetime then return 0.
        if datetime_array[0] == str(current_date):
            if system_time > min_time and system_time < max_time:
                return "0"
            else:
                return "1"


#Check if any changes have occurred between last check and current system values.
def system_changelog():
    #Request url.
    request_url = ("http://%s/ISAPI/System/deviceInfo" % credentials.ipAddress)
    auth = requests.auth.HTTPDigestAuth(credentials.username, credentials.password)
    response = requests.get(request_url, auth=auth)
    iccid = get_iccid.get_sim_iccid()

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
        URL = ("%s/system/getSystem" % credentials.db_address)
        PARAMS = {'system_id' : json_system["deviceID"], 'iccid' : iccid}
        stored_system = requests.post(url=URL, data=PARAMS)
        system_datetime = system_check_datetime()

        #If query returns results response code is not 500, loop through and save found values to an array for comparison. 
        if len(stored_system.text) > 3 and stored_system.status_code != 500:
            stored_values = stored_system.json()
            stored_system_data.append([stored_values["id"], stored_values["device_id"], stored_values["name"], stored_values["status"], stored_values["firmware"], stored_values["datetime"]])
        else:
            #If first entry input null value.
            stored_system_data.append(["null", "null", "null", "null", "null", "null"])
        
        #Iterate through and compare data from API to database array, provided a database entry exists.
        if len(stored_system_data) > 0:
            for i in range(len(stored_system_data)):
                #Check if system ID is the same.
                if str(current_system_data[i][0]) == str(stored_system_data[i][0]):

                    #Check if system status is different.
                    if str(current_system_data[i][2]) != str(stored_system_data[i][3]):
                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % credentials.db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_system_data[i][1], "status changed", stored_system_data[i][3], current_system_data[i][2], date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_system_data[i][0]} status changed from output {stored_system_data[i][3]} to {current_system_data[i][2]} at {datetime.now().strftime("%H:%M:%S")}.')
                    
                    #Check if system name has changed.
                    if str(current_system_data[i][1]) != str(stored_system_data[i][2]):

                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % credentials.db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_system_data[i][1], "name changed", stored_system_data[i][2], current_system_data[i][1], date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_system_data[i][0]} name changed from output {stored_system_data[i][2]} to {current_system_data[i][1]} at {datetime.now().strftime("%H:%M:%S")}.')

                    #Check if system firmware has changed.
                    if str(current_system_data[i][3]) != str(stored_system_data[i][4]):

                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % credentials.db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_system_data[i][1], "firmware changed", stored_system_data[i][4], current_system_data[i][3], date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_system_data[i][0]} firmware changed from output {stored_system_data[i][4]} to {current_system_data[i][3]} at {datetime.now().strftime("%H:%M:%S")}.')

                    #Check if system datetime has changed.
                    if str(system_datetime) != str(stored_system_data[i][5]):

                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % credentials.db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_system_data[i][1], "showing correct datetime changed", stored_system_data[i][5], system_datetime, date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_system_data[i][0]} datetime changed showing correct output {stored_system_data[i][5]} to {system_datetime} at {datetime.now().strftime("%H:%M:%S")}.')

                    else:
                        print(f'{current_system_data[i][1]} is showing no changes at {datetime.now().strftime("%H:%M:%S")}.')

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

    insert_system_info()


#Insert new or update existing system record.
def insert_system_info():
    #Request url.
    request_url = ("http://%s/ISAPI/System/deviceInfo" % credentials.ipAddress)
    auth = requests.auth.HTTPDigestAuth(credentials.username, credentials.password)
    response = requests.get(request_url, auth=auth)
    iccid = get_iccid.get_sim_iccid()

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_system = json_data["DeviceInfo"]

        URL = ("%s/system/getSystem" % credentials.db_address)

        PARAMS = {'system_id': json_system["deviceID"], 'iccid' : iccid}

        system_exists = requests.post(url=URL, data=PARAMS)
        system_datetime = system_check_datetime()
        
        #If response length is greater than 3 then the record exists and to update it. Else input a new record. 
        if len(system_exists.text) > 3 and system_exists.status_code != 500:
            URL = ("%s/system/updateSystem" % credentials.db_address)

            PARAMS = {'system_id': json_system["deviceID"], 'system_name': json_system["deviceName"], 'system_status' : 'True', 'system_firmware': json_system["firmwareVersion"], 'system_datetime': system_datetime, 'iccid' : iccid, 'check_date': date.today(), 'check_time': datetime.now().strftime("%H:%M:%S")}
            
            r = requests.post(url=URL, data=PARAMS)

            print(r.text)
        elif system_exists.status_code != 500:

            new_device_id = get_new_device_id()

            URL = ("%s/system/inputSystem" % credentials.db_address)

            PARAMS = {'system_id': json_system["deviceID"], 'device_id': new_device_id, 'system_name': json_system["deviceName"], 'system_status' : 'True', 'system_firmware': json_system["firmwareVersion"], 'system_datetime': system_datetime, 'check_date': date.today(), 'check_time': datetime.now().strftime("%H:%M:%S")}

            r = requests.post(url=URL, data=PARAMS)

            print(r.text) 
        else:
            print("Server Error Status Code: %s" % system_exists.status_code)  
    else:
        print(response.status_code)


#Check if ICCID is able to be retrieved.
if get_iccid.get_sim_iccid() != "Unable to get ICCID.":
    iccid = get_iccid.get_sim_iccid()
    #Get data from API of whether the Pi has been activated or is suspended and if to continue with processing. 
    if check_license.get_license(iccid) == True:
        try:
            #Call function to insert or update system table, and check for any changes to be inserted into changelog table.
            system_changelog()
        except:
            print("Unable to get system data.")
    else:
        print("Pi not activated or license suspended.")
else:
    print("Unable to get ICCID.")