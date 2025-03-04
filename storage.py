import requests, xmltodict, random, check_license
from datetime import date, datetime

#Temporary variables for testing.
ipAddress = "192.168.1.73"
username = "admin"
password = "Concept1"
iccid = "8935711001091680394"
db_address = "https://em8database.com/api"
#db_address = "http://127.0.0.1:5000"


#Get a random value in maximum integer range for the video log ID.
def get_random_number():
    random_number = random.randint(1, 2147483646)
    return random_number


#Make API calls to get new device ID, insert record, and return the ID.
def get_new_device_id():

    #Get new unique device ID.
    URL = ("%s/devices/getNewID" % db_address)

    new_device_id = requests.get(url=URL).json()
    
    #Insert new device record.
    URL = ("%s/devices/inputDevice" % db_address)

    PARAMS = {'device_id': new_device_id, 'device_type': '1', 'iccid': iccid}

    r = requests.post(url=URL, data=PARAMS)

    print(r.text)

    return new_device_id


def storage_changelog():
    #Request url.
    request_url = ("http://%s/ISAPI/ContentMgmt/Storage/hdd" % ipAddress)
    auth = requests.auth.HTTPDigestAuth(username, password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_hdd = json_data["hddList"]["hdd"]

        current_storage_data = [json_hdd["id"], json_hdd["hddName"], json_hdd["status"]]
        stored_storage_data = []
        changelog_data = []

        #Call API to check if storage ID exists.
        URL = ("%s/storage/getStorage" % db_address)
        PARAMS = {'storage_id' : json_hdd["id"], "iccid" : iccid}
        storage_records = requests.post(url=URL, data=PARAMS)

        #If query returns results, loop through and save found values to an array for comparison. 
        if len(storage_records.text) > 3 and storage_records.status_code != 500:
            storage_values = storage_records.json()
            print(storage_values)
            stored_storage_data.append([storage_values["device_id"], storage_values["storage_id"], storage_values["name"], storage_values["status"]])
        else:
            #If first entry input null value.
            stored_storage_data.append(["null", "null", "null", "null"])
        
        if len(stored_storage_data) > 0:
            #Iterate through and compare data from API to database array, provided a database entry exists.
            for i in range(len(stored_storage_data)):
                #Check if storage ID is the same.
                if str(current_storage_data[0]) == str(stored_storage_data[i][1]):
                    #Check if storage status is different.
                    if str(current_storage_data[2]) != str(stored_storage_data[i][3]):
                        #Call API to get changelog ID.
                        URL = ("%s/changelog/getNewID" % db_address)
                        get_new_changelog_id = requests.get(url=URL)
                        changelog_id = get_new_changelog_id.text

                        #Append changelog entry to array.
                        changelog_data.append([changelog_id, stored_storage_data[i][0], "status changed", stored_storage_data[i][3], current_storage_data[2], date.today(), datetime.now().strftime("%H:%M:%S")])
                        
                        print(f'{current_storage_data[1]} status changed from output {stored_storage_data[i][3]} to {current_storage_data[2]} at {datetime.now().strftime("%H:%M:%S")}.')
                    else:
                        print(f'{current_storage_data[1]} is showing no changes at {datetime.now().strftime("%H:%M:%S")}.')

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

    insert_storage_log() 


#Function to insert new or update existing storage record.
def insert_storage_log():
    #Request url.
    request_url = ("http://%s/ISAPI/ContentMgmt/Storage/hdd" % ipAddress)
    auth = requests.auth.HTTPDigestAuth(username, password)
    response = requests.get(request_url, auth=auth)

    #Response code check.
    if response.status_code == 200:

        #Convert response to json.
        json_data = xmltodict.parse(response.content)
        json_hdd = json_data["hddList"]["hdd"]

        #Get Site ID from API.
        URL = ("%s/storage/getStorage" % db_address)
        PARAMS = {'storage_id' : json_hdd["id"], 'iccid' : iccid}
        request_storage = requests.post(url=URL, data=PARAMS)
        
        #If query returns data then record exists and to update, otherwise insert new record.
        if len(request_storage.text) > 3 and request_storage.status_code != 500:
            #Storage values.
            storage_values = request_storage.json()

            #Get video data from API call and store in dictionary.
            PARAMS = {'device_id': storage_values["device_id"], 'storage_name': json_hdd["hddName"], 'storage_status': json_hdd["status"], 'check_date': datetime.now().strftime("%Y-%m-%d"), 'check_time': datetime.now().strftime("%H:%M:%S")}

            #Define URL for API call to post acquired storage data for insertion into database.
            URL = ("%s/storage/updateStorage" % db_address)
            
            r = requests.post(url=URL, data=PARAMS)
            print(r.text)
            
        else:
            #Generate new device ID and insert storage data into database.
            new_device_id = get_new_device_id()

            #Get video data from API call and store in dictionary.
            PARAMS = {'device_id': new_device_id, 'storage_id': json_hdd["id"], 'storage_name': json_hdd["hddName"], 'storage_status': json_hdd["status"], 'check_date': datetime.now().strftime("%Y-%m-%d"), 'check_time': datetime.now().strftime("%H:%M:%S")}

            #Define URL for API call to post acquired storage data for insertion into database.
            URL = ("%s/storage/inputStorage" % db_address)
            
            r = requests.post(url=URL, data=PARAMS)
            print(r.text)

    else:
        print(response.status_code)
        
    
#print(check_license.get_license(iccid))

#Get data from API of whether the Pi has been activated or is suspended and if to continue with processing. 
if check_license.get_license(iccid) == True:
    #Insert or update storage records in the database. Insert any changes into changelog table.
    storage_changelog()  
else:
    print("Pi not activated or license suspended.")